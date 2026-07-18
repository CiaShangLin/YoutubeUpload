import unittest
from unittest import mock

from uploaders.youtube_uploader import YouTubeUploader
from video_item import VideoItem


class YouTubeUploaderDescriptionTest(unittest.TestCase):
    @mock.patch("uploaders.youtube_uploader.googleapiclient.discovery.build")
    @mock.patch("uploaders.youtube_uploader.MediaFileUpload")
    def test_upload_persists_description_onto_video(self, mock_media_upload, mock_build):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = mock.Mock(valid=True)

        uploader = YouTubeUploader(token_manager)
        uploader._resumable_upload = mock.Mock(return_value="fake_video_id")

        video = VideoItem(video_path="dummy.mp4", title="Test Title")

        video_id = uploader.upload(video)

        self.assertEqual(video_id, "fake_video_id")
        self.assertIn("Test Title", video.description)
        self.assertIn("#starcraft2", video.description)


if __name__ == "__main__":
    unittest.main()
