import unittest

from uploaders.bilibili_uploader import BilibiliUploadFile, BilibiliUploader
from video_item import VideoItem


class BilibiliDescriptionReuseTest(unittest.TestCase):
    def _make_uploader(self):
        uploader = BilibiliUploader()
        uploader.cookies = type("Cookies", (), {"csrf": "csrf"})()
        return uploader

    def test_uses_video_description_when_present(self):
        uploader = self._make_uploader()
        video = VideoItem(video_path="video.mp4", title="t")
        video.description = "EXACT YT DESCRIPTION TEXT"

        payload = uploader._build_archive_payload(
            video=video,
            uploaded=BilibiliUploadFile(filename="f", cid=1),
            cover_url="",
            replay_url="",
        )

        self.assertEqual(payload["desc"], "EXACT YT DESCRIPTION TEXT")

    def test_falls_back_to_default_when_description_empty(self):
        uploader = self._make_uploader()
        video = VideoItem(video_path="video.mp4", title="t")

        payload = uploader._build_archive_payload(
            video=video,
            uploaded=BilibiliUploadFile(filename="f", cid=1),
            cover_url="",
            replay_url="https://drive.example/rp",
        )

        self.assertIn("t", payload["desc"])
        self.assertIn("RP: https://drive.example/rp", payload["desc"])


if __name__ == "__main__":
    unittest.main()
