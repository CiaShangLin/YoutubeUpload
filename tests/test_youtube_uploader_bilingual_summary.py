# tests/test_youtube_uploader_bilingual_summary.py
import unittest
from unittest import mock

from uploaders.youtube_uploader import YouTubeUploader
from video_item import VideoItem


class YouTubeUploaderBilingualSummaryTest(unittest.TestCase):
    @mock.patch("uploaders.youtube_uploader.googleapiclient.discovery.build")
    @mock.patch("uploaders.youtube_uploader.MediaFileUpload")
    def test_upload_appends_english_summary_to_default_description(self, mock_media_upload, mock_build):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = mock.Mock(valid=True)

        uploader = YouTubeUploader(token_manager)
        uploader._resumable_upload = mock.Mock(return_value="fake_video_id")

        video = VideoItem(
            video_path="dummy.mp4",
            title="Test Title",
            en_description_summary="Key moments: a crushing 4-base timing push.",
        )

        uploader.upload(video)

        self.assertIn("Test Title", video.description)
        self.assertIn("Key moments: a crushing 4-base timing push.", video.description)
        self.assertTrue(video.description.strip().endswith("Key moments: a crushing 4-base timing push."))

    @mock.patch("uploaders.youtube_uploader.googleapiclient.discovery.build")
    def test_add_localizations_appends_zh_summary_to_zh_tw_only(self, mock_build):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = mock.Mock(valid=True)
        mock_youtube = mock.Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.videos.return_value.list.return_value.execute.return_value = {
            "items": [{"snippet": {"title": "Test Title"}, "localizations": {}}]
        }

        uploader = YouTubeUploader(token_manager)
        uploader.add_localizations("vid123", "https://example.com/replay", zh_description_summary="這場的重點是四礦強攻。")

        update_call = mock_youtube.videos.return_value.update.call_args
        localizations = update_call.kwargs["body"]["localizations"]

        self.assertIn("這場的重點是四礦強攻。", localizations["zh-TW"]["description"])
        self.assertNotIn("這場的重點是四礦強攻。", localizations["ja"]["description"])
        self.assertNotIn("這場的重點是四礦強攻。", localizations["ko"]["description"])

    @mock.patch("uploaders.youtube_uploader.googleapiclient.discovery.build")
    def test_add_localizations_without_summary_matches_previous_behavior(self, mock_build):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = mock.Mock(valid=True)
        mock_youtube = mock.Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.videos.return_value.list.return_value.execute.return_value = {
            "items": [{"snippet": {"title": "Test Title"}, "localizations": {}}]
        }

        uploader = YouTubeUploader(token_manager)
        ok = uploader.add_localizations("vid123", "https://example.com/replay")

        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
