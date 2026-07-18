import unittest
from unittest import mock

from uploaders.bilibili_uploader import BilibiliUploader
from video_item import VideoItem


class BilibiliReplayReuseTest(unittest.TestCase):
    @mock.patch("uploaders.bilibili_uploader.google_drive.upload_replay")
    def test_reuses_existing_replay_url_without_reuploading(self, mock_upload_replay):
        uploader = BilibiliUploader()
        video = VideoItem(video_path="video.mp4", title="t", replay_path="replay.SC2Replay")
        video.set_replay_url("https://drive.google.com/existing-link")

        result = uploader._ensure_replay_uploaded(video)

        self.assertEqual(result, "https://drive.google.com/existing-link")
        mock_upload_replay.assert_not_called()

    @mock.patch("uploaders.bilibili_uploader.google_drive.upload_replay")
    def test_uploads_replay_when_not_already_set(self, mock_upload_replay):
        mock_upload_replay.return_value = "https://drive.google.com/new-link"
        uploader = BilibiliUploader()
        video = VideoItem(video_path="video.mp4", title="t", replay_path="replay.SC2Replay")

        result = uploader._ensure_replay_uploaded(video)

        self.assertEqual(result, "https://drive.google.com/new-link")
        mock_upload_replay.assert_called_once_with("replay.SC2Replay")
        self.assertEqual(video.replay_url, "https://drive.google.com/new-link")

    @mock.patch("uploaders.bilibili_uploader.google_drive.upload_replay")
    def test_no_replay_path_returns_empty_string(self, mock_upload_replay):
        uploader = BilibiliUploader()
        video = VideoItem(video_path="video.mp4", title="t")

        result = uploader._ensure_replay_uploaded(video)

        self.assertEqual(result, "")
        mock_upload_replay.assert_not_called()


if __name__ == "__main__":
    unittest.main()
