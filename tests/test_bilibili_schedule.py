import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from uploaders.bilibili_uploader import BilibiliUploadFile, BilibiliUploader
from video_item import VideoItem


class BilibiliScheduleTest(unittest.TestCase):
    def test_build_archive_payload_uses_publish_time_as_taipei_dtime(self):
        uploader = BilibiliUploader()
        uploader.cookies = type("Cookies", (), {"csrf": "csrf"})()
        publish_time = datetime(2026, 7, 30, 18, 0)
        video = VideoItem(
            video_path="video.mp4",
            title="scheduled video",
            publish_time=publish_time,
        )

        payload = uploader._build_archive_payload(
            video=video,
            uploaded=BilibiliUploadFile(filename="uploaded-file", cid=123),
            cover_url="",
            replay_url="",
        )

        expected_timestamp = int(
            datetime(2026, 7, 30, 18, 0, tzinfo=ZoneInfo("Asia/Taipei")).timestamp()
        )
        self.assertEqual(payload["dtime"], expected_timestamp)


if __name__ == "__main__":
    unittest.main()
