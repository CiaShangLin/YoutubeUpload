import unittest

from video_item import VideoItem


class VideoItemSubtitleFieldsTest(unittest.TestCase):
    def test_defaults_are_none_and_not_uploaded(self):
        video = VideoItem(video_path="a.mp4", title="A")

        self.assertIsNone(video.srt_path)
        self.assertIsNone(video.zh_description_summary)
        self.assertIsNone(video.en_description_summary)
        self.assertFalse(video.caption_uploaded)
        self.assertIsNone(video.caption_error_message)

    def test_round_trips_through_to_dict_and_from_dict(self):
        video = VideoItem(
            video_path="a.mp4",
            title="A",
            srt_path="workspace/sc2subtitle/videos/EP-41/subtitles.srt",
            zh_description_summary="這場對戰重點在...",
            en_description_summary="Key moments in this match...",
        )
        video.caption_uploaded = True

        restored = VideoItem.from_dict(video.to_dict())

        self.assertEqual(restored.srt_path, video.srt_path)
        self.assertEqual(restored.zh_description_summary, video.zh_description_summary)
        self.assertEqual(restored.en_description_summary, video.en_description_summary)
        self.assertTrue(restored.caption_uploaded)


if __name__ == "__main__":
    unittest.main()
