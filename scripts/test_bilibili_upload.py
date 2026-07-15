"""CLI smoke test for Bilibili upload.

Example:
    python scripts/test_bilibili_upload.py --video path/to/video.mp4 --cover path/to/cover.jpg --replay path/to/file.SC2Replay --title "Title"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uploaders.bilibili_uploader import BilibiliUploader
from video_item import VideoItem


TAIPEI_TIMEZONE = ZoneInfo("Asia/Taipei")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--cover")
    parser.add_argument("--replay")
    parser.add_argument("--description", default="")
    parser.add_argument("--publish-time", help="Asia/Taipei time, format: YYYY-MM-DD HH:MM")
    args = parser.parse_args()
    publish_time = datetime.now(TAIPEI_TIMEZONE)
    if args.publish_time:
        publish_time = datetime.strptime(args.publish_time, "%Y-%m-%d %H:%M").replace(
            tzinfo=TAIPEI_TIMEZONE
        )

    video = VideoItem(
        video_path=args.video,
        title=args.title,
        thumbnail_path=args.cover,
        replay_path=args.replay,
        description=args.description,
        publish_time=publish_time,
    )

    bvid = BilibiliUploader().upload(video)
    print(f"Uploaded to Bilibili: https://www.bilibili.com/video/{bvid}")


if __name__ == "__main__":
    main()
