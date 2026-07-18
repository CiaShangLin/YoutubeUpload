import unittest

from video_item import VideoItem, UploadStatus


class VideoItemBilibiliFieldsTest(unittest.TestCase):
    def test_defaults(self):
        video = VideoItem(video_path="v.mp4", title="t")

        self.assertEqual(video.bilibili_status, UploadStatus.PENDING)
        self.assertIsNone(video.bilibili_video_id)
        self.assertIsNone(video.bilibili_error_message)

    def test_to_dict_and_from_dict_roundtrip(self):
        video = VideoItem(video_path="v.mp4", title="t")
        video.bilibili_status = UploadStatus.COMPLETED
        video.bilibili_video_id = "BV1xx"
        video.bilibili_error_message = None

        data = video.to_dict()
        restored = VideoItem.from_dict(data)

        self.assertEqual(restored.bilibili_status, UploadStatus.COMPLETED)
        self.assertEqual(restored.bilibili_video_id, "BV1xx")
        self.assertIsNone(restored.bilibili_error_message)

    def test_from_dict_missing_bilibili_keys_defaults_to_pending(self):
        data = {"video_path": "v.mp4", "title": "t"}

        restored = VideoItem.from_dict(data)

        self.assertEqual(restored.bilibili_status, UploadStatus.PENDING)
        self.assertIsNone(restored.bilibili_video_id)


if __name__ == "__main__":
    unittest.main()
