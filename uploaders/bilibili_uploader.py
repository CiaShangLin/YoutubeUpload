"""
B站上傳器
基於 biliup 1.1.29 實作 Bilibili 影片上傳功能
"""

import os
import logging
from typing import List

from uploaders.base_uploader import BaseUploader
from video_item import VideoItem

logger = logging.getLogger(__name__)

# 預設 B站標籤
DEFAULT_TAGS: List[str] = [
    "StarCraft2", "星海爭霸2", "SC2", "天梯",
    "Protoss", "神族", "Ladder"
]

# B站遊戲分區 tid（遊戲 > 網絡遊戲）
BILIBILI_TID_GAME: int = 171


def _build_cookie_payload(flat_cookies: dict) -> dict:
    """
    將 TokenManager 儲存的平坦 Cookie 字典轉換為
    biliup login_by_cookies() 所需的格式。

    TokenManager 格式：
        {"SESSDATA": "...", "bili_jct": "...", ...}

    biliup 所需格式：
        {"cookie_info": {"cookies": [{"name": "SESSDATA", "value": "..."}, ...]}}

    Args:
        flat_cookies: TokenManager 儲存的平坦 Cookie 字典

    Returns:
        dict: biliup 格式的 Cookie Payload
    """
    cookies_list = [
        {"name": key, "value": value}
        for key, value in flat_cookies.items()
    ]
    return {
        "cookie_info": {
            "cookies": cookies_list
        }
    }


class BilibiliUploader(BaseUploader):
    """
    B站影片上傳器

    基於 biliup 1.1.29 實作，透過 TokenManager 取得 Cookie
    進行身分驗證後上傳影片到 Bilibili。
    """

    def __init__(self, token_manager):
        """
        初始化 B站上傳器

        Args:
            token_manager: TokenManager 實例，用於取得 B站 Cookie
        """
        self._token_manager = token_manager

    # ------------------------------------------------------------------
    # BaseUploader 抽象方法實作
    # ------------------------------------------------------------------

    def upload(self, video: VideoItem) -> str:
        """
        上傳影片到 B站

        流程：
        1. 驗證影片資料完整性
        2. 取得 Cookie 並登入
        3. 建立投稿資料（Data）
        4. 上傳影片檔案
        5. 上傳封面（如果有）
        6. 設定延遲發布（如果需要）
        7. 提交投稿，回傳 BV 號

        Args:
            video: 影片資料模型

        Returns:
            str: B站影片 BV 號（bvid）

        Raises:
            ValueError: Cookie 不存在或影片資料不完整
            Exception: biliup API 回報錯誤
        """
        # 1. 驗證影片資料
        if not self.validate_video(video):
            raise ValueError(
                f"影片資料不完整：video_path={video.video_path!r}，title={video.title!r}"
            )

        if not os.path.isfile(video.video_path):
            raise ValueError(f"影片檔案不存在：{video.video_path}")

        # 2. 取得 Cookie
        flat_cookies = self._token_manager.get_bilibili_cookies()
        if flat_cookies is None:
            raise ValueError(
                "B站 Cookie 不存在，請先登入 B站（執行 Cookie 匯入流程）"
            )

        cookie_payload = _build_cookie_payload(flat_cookies)

        # 延遲 import，避免在未安裝 biliup 時的 ImportError 影響整個模組
        from biliup.plugins.bili_webup import BiliBili, Data

        # 3. 建立投稿資料
        data = Data(
            copyright=1,          # 1=自製；2=轉載
            tid=BILIBILI_TID_GAME,
            title=video.title,
            desc=video.description or "",
        )
        data.set_tag(DEFAULT_TAGS)

        # 設定延遲發布（dtime 需大於提交時間 2 小時以上，biliup 會自動驗證）
        dtime = video.get_bilibili_dtime()
        if dtime > 0:
            import time
            abs_dtime = int(time.time()) + dtime
            data.delay_time(abs_dtime)
            logger.info(f"設定延遲發布，dtime={abs_dtime}")

        # 4. 建立 BiliBili 上傳器實例並登入
        with BiliBili(data) as bili:
            bili.login_by_cookies(cookie_payload)

            # 5. 上傳影片檔案
            logger.info(f"開始上傳影片：{video.video_path}")
            video_part = bili.upload_file(video.video_path)
            # upload_file 回傳包含 filename 等資訊的 dict，需加入 Data
            data.append(video_part)

            # 6. 上傳封面（如果有）
            if video.thumbnail_path and os.path.isfile(video.thumbnail_path):
                try:
                    cover_url = bili.cover_up(video.thumbnail_path)
                    data.cover = cover_url
                    logger.info(f"封面上傳成功：{cover_url}")
                except Exception as e:
                    logger.warning(f"封面上傳失敗（繼續上傳影片）：{e}")

            # 7. 提交投稿
            result = bili.submit()

        logger.info(f"B站投稿成功，回傳結果：{result}")

        # 解析 BV 號
        bvid = self._extract_bvid(result)
        if bvid:
            video.bilibili_video_id = bvid

        return bvid or ""

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
        設定影片封面（B站封面在 upload() 中一併處理，此方法為 no-op）

        Args:
            video_id: B站影片 BV 號
            thumbnail_path: 封面檔案路徑

        Returns:
            bool: 永遠回傳 True
        """
        logger.debug(
            f"set_thumbnail 被呼叫（no-op）：video_id={video_id}，"
            f"thumbnail_path={thumbnail_path}"
        )
        return True

    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        """
        將影片加入合集（B站不支援此操作，請使用 B站後台手動管理合集）

        Args:
            video_id: B站影片 BV 號
            playlist_ids: 合集 ID 列表

        Raises:
            NotImplementedError: B站不支援透過 API 加入合集
        """
        raise NotImplementedError(
            "B站不支援透過上傳 API 加入合集，請至 B站創作中心手動管理。"
        )

    # ------------------------------------------------------------------
    # 私有輔助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_bvid(result: dict) -> str:
        """
        從 submit() 回傳的 dict 中解析 BV 號

        biliup submit_web() 回傳格式：
            {"code": 0, "data": {"bvid": "BVxxxxxxxx", "aid": 12345}}

        Args:
            result: submit() 的回傳值

        Returns:
            str: BV 號，無法解析時回傳空字串
        """
        if not isinstance(result, dict):
            logger.warning(f"submit 回傳非預期格式：{result}")
            return ""

        if result.get("code") != 0:
            logger.error(f"B站投稿 API 回傳錯誤：{result}")
            raise Exception(f"B站投稿失敗：{result}")

        data = result.get("data", {})
        if isinstance(data, dict):
            bvid = data.get("bvid", "")
            if bvid:
                logger.info(f"解析 BV 號成功：{bvid}")
                return bvid

        logger.warning(f"無法從回傳值解析 BV 號：{result}")
        return ""
