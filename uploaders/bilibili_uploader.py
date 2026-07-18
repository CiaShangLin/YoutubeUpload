"""Bilibili uploader using the web creator-center upload endpoints."""

import base64
import math
import mimetypes
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from zoneinfo import ZoneInfo

import requests

from services import google_drive
from services.browser_cookies import BilibiliCookies, get_bilibili_cookies
from uploaders.base_uploader import BaseUploader
from video_item import MatchType, VideoItem


BILIBILI_ADD_URL = "https://member.bilibili.com/x/vu/web/add/v3"
BILIBILI_COVER_URL = "https://member.bilibili.com/x/vu/web/cover/up"
BILIBILI_PREUPLOAD_URL = "https://member.bilibili.com/preupload"
BILIBILI_TID_ESPORTS = 171
BILIBILI_DESC_FORMAT_PLAIN_TEXT = 9999
BILIBILI_PROFILE = "ugcfx/bup"
BILIBILI_CHUNK_FALLBACK = 10 * 1024 * 1024
BILIBILI_TIMEZONE = ZoneInfo("Asia/Taipei")
BILIBILI_MIN_SCHEDULE_DELTA = timedelta(hours=4)


@dataclass
class BilibiliUploadFile:
    filename: str
    cid: int


class BilibiliUploader(BaseUploader):
    """Upload videos to Bilibili through the web upload API."""

    def __init__(self, cookie_config_path: str = "bilibili_cookies.json"):
        self.cookie_config_path = cookie_config_path
        self.session = requests.Session()
        self.cookies: BilibiliCookies | None = None

    def upload(self, video: VideoItem) -> str:
        """Upload a video to Bilibili and return the BV id."""
        if not self.validate_video(video):
            raise ValueError("Invalid video item")

        self._ensure_auth()

        replay_url = ""
        if video.has_replay:
            try:
                print(f"Uploading replay to Google Drive: {video.replay_path}")
                replay_url = google_drive.upload_replay(video.replay_path)
                video.set_replay_url(replay_url)
            except Exception as exc:
                print(f"Replay upload failed, continuing without RP URL: {exc}")

        cover_url = ""
        if video.has_thumbnail:
            try:
                cover_url = self._upload_cover(video.thumbnail_path)
                print(f"Bilibili cover URL: {cover_url}")
            except Exception as exc:
                print(f"Cover upload failed, Bilibili will auto-pick a cover: {exc}")

        uploaded = self._upload_video_file(video.video_path)
        payload = self._build_archive_payload(video, uploaded, cover_url, replay_url)
        response = self._post_json(
            BILIBILI_ADD_URL,
            params={"t": self._timestamp_ms(), "csrf": self.cookies.csrf},
            json_body=payload,
        )

        data = response.get("data") or {}
        bvid = data.get("bvid")
        aid = data.get("aid")
        if not bvid:
            raise RuntimeError(f"Bilibili archive submitted but no bvid returned: {response}")

        print(f"Bilibili upload completed: {bvid} (aid={aid})")
        return bvid

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Bilibili cover is submitted with the archive payload."""
        return True

    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        """Collection support is intentionally not part of the first uploader."""
        return False

    def _ensure_auth(self):
        if self.cookies:
            return
        self.cookies = get_bilibili_cookies(self.cookie_config_path)
        self.session.headers.update({
            "Cookie": self.cookies.as_cookie_header(),
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
            "Referer": "https://member.bilibili.com/platform/upload/video/frame",
        })
        print(f"Loaded Bilibili cookies from {self.cookies.source}")

    def _upload_cover(self, thumbnail_path: str) -> str:
        with open(thumbnail_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")

        mime_type = mimetypes.guess_type(thumbnail_path)[0] or "image/jpeg"
        cover = f"data:{mime_type};base64,{encoded}"
        response = self.session.post(
            BILIBILI_COVER_URL,
            params={"ts": self._timestamp_ms()},
            data={"csrf": self.cookies.csrf, "cover": cover},
            timeout=60,
        )
        payload = self._parse_bilibili_response(response)
        url = (payload.get("data") or {}).get("url")
        if not url:
            raise RuntimeError(f"Cover upload returned no URL: {payload}")
        return url

    def _upload_video_file(self, video_path: str) -> BilibiliUploadFile:
        filename = os.path.basename(video_path)
        filesize = os.path.getsize(video_path)
        preupload = self._preupload(filename)
        upload_url = self._upos_url(preupload)
        chunk_size = int(preupload.get("chunk_size") or BILIBILI_CHUNK_FALLBACK)
        biz_id = int(preupload["biz_id"])
        auth = preupload["auth"]

        upload_meta = self._create_upos_upload(upload_url, filesize, chunk_size, biz_id, auth)
        upload_id = upload_meta["upload_id"]
        chunks = max(1, math.ceil(filesize / chunk_size))

        print(f"Uploading Bilibili video in {chunks} chunks")
        parts = []
        with open(video_path, "rb") as f:
            for chunk_index in range(chunks):
                start = chunk_index * chunk_size
                data = f.read(chunk_size)
                end = start + len(data)
                part_number = chunk_index + 1
                self._upload_chunk(
                    upload_url=upload_url,
                    auth=auth,
                    upload_id=upload_id,
                    part_number=part_number,
                    chunk_index=chunk_index,
                    chunks=chunks,
                    size=len(data),
                    start=start,
                    end=end,
                    total=filesize,
                    data=data,
                )
                parts.append({"partNumber": part_number, "eTag": "etag"})
                print(f"Uploaded chunk {part_number}/{chunks}")

        self._complete_upos_upload(upload_url, filename, upload_id, biz_id, auth, parts)
        bili_filename = os.path.splitext(os.path.basename(preupload["upos_uri"]))[0]
        return BilibiliUploadFile(filename=bili_filename, cid=biz_id)

    def _preupload(self, filename: str) -> dict:
        response = self.session.get(
            BILIBILI_PREUPLOAD_URL,
            params={"name": filename, "r": "upos", "profile": BILIBILI_PROFILE},
            timeout=60,
        )
        data = response.json()
        if "auth" not in data or "upos_uri" not in data or "endpoint" not in data:
            raise RuntimeError(f"Preupload failed: {data}")
        return data

    def _create_upos_upload(self, upload_url: str, filesize: int, chunk_size: int, biz_id: int, auth: str) -> dict:
        response = self.session.post(
            upload_url,
            params={
                "uploads": "",
                "output": "json",
                "profile": BILIBILI_PROFILE,
                "filesize": filesize,
                "partsize": chunk_size,
                "biz_id": biz_id,
            },
            headers={"X-Upos-Auth": auth},
            timeout=60,
        )
        data = response.json()
        if data.get("OK") != 1 or "upload_id" not in data:
            raise RuntimeError(f"Create UPOS upload failed: {data}")
        return data

    def _upload_chunk(
        self,
        upload_url: str,
        auth: str,
        upload_id: str,
        part_number: int,
        chunk_index: int,
        chunks: int,
        size: int,
        start: int,
        end: int,
        total: int,
        data: bytes,
    ):
        response = self.session.put(
            upload_url,
            params={
                "partNumber": part_number,
                "uploadId": upload_id,
                "chunk": chunk_index,
                "chunks": chunks,
                "size": size,
                "start": start,
                "end": end,
                "total": total,
            },
            headers={"X-Upos-Auth": auth, "Content-Type": "application/octet-stream"},
            data=data,
            timeout=120,
        )
        if response.text.strip() != "MULTIPART_PUT_SUCCESS":
            raise RuntimeError(f"Chunk upload failed: HTTP {response.status_code} {response.text[:500]}")

    def _complete_upos_upload(self, upload_url: str, filename: str, upload_id: str, biz_id: int, auth: str, parts: list):
        response = self.session.post(
            upload_url,
            params={
                "output": "json",
                "name": filename,
                "profile": BILIBILI_PROFILE,
                "uploadId": upload_id,
                "biz_id": biz_id,
            },
            headers={"X-Upos-Auth": auth, "Content-Type": "application/json; charset=UTF-8"},
            json={"parts": parts},
            timeout=120,
        )
        data = response.json()
        if data.get("OK") != 1:
            raise RuntimeError(f"Complete UPOS upload failed: {data}")

    def _build_archive_payload(
        self,
        video: VideoItem,
        uploaded: BilibiliUploadFile,
        cover_url: str,
        replay_url: str,
    ) -> dict:
        title = video.title[:80]
        desc = (video.description or self._get_description(video, replay_url))[:2000]
        dynamic = title[:233]
        tag = ",".join(self._get_tags(video)[:10])

        payload = {
            "videos": [
                {
                    "filename": uploaded.filename,
                    "title": title,
                    "desc": "",
                    "cid": uploaded.cid,
                }
            ],
            "cover": cover_url,
            "cover43": "",
            "title": title,
            "source": "",
            "copyright": 1,
            "tid": BILIBILI_TID_ESPORTS,
            "tag": tag,
            "desc_format_id": BILIBILI_DESC_FORMAT_PLAIN_TEXT,
            "desc": desc,
            "recreate": -1,
            "dynamic": dynamic,
            "interactive": 0,
            "act_reserve_create": 0,
            "no_disturbance": 0,
            "no_reprint": 1,
            "subtitle": {"open": 0, "lan": ""},
            "open_subtitle": False,
            "dolby": 0,
            "lossless_music": 0,
            "charging_pay": 0,
            "up_selection_reply": False,
            "up_close_reply": False,
            "up_close_danmu": False,
            "web_os": 3,
            "csrf": self.cookies.csrf,
        }
        if not cover_url:
            payload.pop("cover")
        dtime = self._get_dtime(video)
        if dtime:
            payload["dtime"] = dtime
        return payload

    def _get_dtime(self, video: VideoItem) -> int | None:
        if not video.publish_time:
            return None

        publish_time = video.publish_time
        if publish_time.tzinfo is None:
            publish_time = publish_time.replace(tzinfo=BILIBILI_TIMEZONE)

        now = datetime.now(BILIBILI_TIMEZONE)
        if publish_time <= now + BILIBILI_MIN_SCHEDULE_DELTA:
            return None

        return int(publish_time.timestamp())

    def _get_description(self, video: VideoItem, replay_url: str) -> str:
        parts = [
            "#星海争霸2 #StarCraft2 #SC2",
            video.title,
        ]
        if replay_url:
            parts.append(f"RP: {replay_url}")
        if video.description:
            parts.append(video.description)
        return "\n".join(part for part in parts if part)

    def _get_tags(self, video: VideoItem) -> List[str]:
        tags = ["星海争霸2", "StarCraft II", "SC2", "电子竞技", "即时战略", "Protoss"]
        if video.game_name:
            tags.append(video.game_name)
        match_tags = {
            MatchType.PVP: "PvP",
            MatchType.PVZ: "PvZ",
            MatchType.PVT: "PvT",
            MatchType.PVR: "PvR",
        }
        if video.match_type in match_tags:
            tags.append(match_tags[video.match_type])

        unique_tags = []
        for tag in tags:
            tag = tag.strip()
            if tag and tag not in unique_tags:
                unique_tags.append(tag)
        return unique_tags

    def _post_json(self, url: str, params: dict, json_body: dict) -> dict:
        response = self.session.post(
            url,
            params=params,
            json=json_body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60,
        )
        return self._parse_bilibili_response(response)

    def _parse_bilibili_response(self, response: requests.Response) -> dict:
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(f"Bilibili returned non-JSON response: HTTP {response.status_code}") from exc

        if payload.get("code") != 0:
            raise RuntimeError(f"Bilibili API error: {payload}")
        return payload

    def _upos_url(self, preupload: dict) -> str:
        endpoint = preupload["endpoint"]
        upos_uri = preupload["upos_uri"].replace("upos://", "")
        return f"https:{endpoint}/{upos_uri}"

    def _timestamp_ms(self) -> str:
        return str(int(time.time() * 1000))
