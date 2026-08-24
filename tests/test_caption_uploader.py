import unittest
from unittest import mock

from uploaders.caption_uploader import CaptionUploader


class CaptionUploaderTest(unittest.TestCase):
    @mock.patch("uploaders.caption_uploader.MediaFileUpload")
    @mock.patch("uploaders.caption_uploader.googleapiclient.discovery.build")
    def test_upload_calls_captions_insert_with_correct_params(self, mock_build, mock_media_upload):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = mock.Mock(valid=True)
        mock_youtube = mock.Mock()
        mock_build.return_value = mock_youtube
        mock_insert = mock_youtube.captions.return_value.insert
        mock_insert.return_value.execute.return_value = {"id": "caption123"}
        mock_media_upload.return_value = "fake_media_body"

        uploader = CaptionUploader(token_manager)
        caption_id = uploader.upload("vid123", "subtitles.srt", language="zh-Hant", name="中文", is_draft=False)

        self.assertEqual(caption_id, "caption123")
        mock_media_upload.assert_called_once_with("subtitles.srt")
        mock_insert.assert_called_once_with(
            part="snippet",
            body={
                "snippet": {
                    "videoId": "vid123",
                    "language": "zh-Hant",
                    "name": "中文",
                    "isDraft": False,
                }
            },
            media_body="fake_media_body",
        )

    def test_upload_uses_zh_hant_and_published_by_default(self):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = mock.Mock(valid=True)

        with mock.patch("uploaders.caption_uploader.googleapiclient.discovery.build") as mock_build, \
             mock.patch("uploaders.caption_uploader.MediaFileUpload"):
            mock_youtube = mock.Mock()
            mock_build.return_value = mock_youtube
            mock_insert = mock_youtube.captions.return_value.insert
            mock_insert.return_value.execute.return_value = {"id": "caption456"}

            uploader = CaptionUploader(token_manager)
            uploader.upload("vid123", "subtitles.srt")

            called_body = mock_insert.call_args.kwargs["body"]
            self.assertEqual(called_body["snippet"]["language"], "zh-Hant")
            self.assertEqual(called_body["snippet"]["name"], "中文")
            self.assertFalse(called_body["snippet"]["isDraft"])

    def test_upload_raises_when_no_credentials(self):
        token_manager = mock.Mock()
        token_manager.get_youtube_credentials.return_value = None

        uploader = CaptionUploader(token_manager)

        with self.assertRaises(Exception):
            uploader.upload("vid123", "subtitles.srt")


if __name__ == "__main__":
    unittest.main()
