"""
Caption Uploader
封裝 YouTube Data API 的 captions.insert 呼叫，上傳 CC 字幕軌。
獨立於 YouTubeUploader 之外，介面單純（影片 ID / SRT 路徑 / 語言 / 軌道名稱 / 是否草稿），
方便單元測試時直接 mock googleapiclient，不需要真的打 API。
"""
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload

from token_manager import TokenManager


class CaptionUploader:
    """上傳 CC 字幕到 YouTube 影片。"""

    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    def upload(
        self,
        video_id: str,
        srt_path: str,
        language: str = "zh-Hant",
        name: str = "中文",
        is_draft: bool = False,
    ) -> str:
        """
        上傳字幕軌。

        Args:
            video_id: YouTube 影片 ID
            srt_path: SRT 字幕檔路徑
            language: 語言代碼，預設 zh-Hant（繁體中文）
            name: 字幕軌顯示名稱，預設「中文」
            is_draft: 是否存為草稿，預設 False（上傳後立即發布可見）

        Returns:
            str: 新建立的 caption id

        Raises:
            Exception: 無憑證或 API 呼叫失敗時拋出
        """
        creds = self.token_manager.get_youtube_credentials()
        if not creds:
            raise Exception("無法取得 YouTube 憑證，請先進行認證")

        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        response = (
            youtube.captions()
            .insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": language,
                        "name": name,
                        "isDraft": is_draft,
                    }
                },
                media_body=MediaFileUpload(srt_path),
            )
            .execute()
        )

        return response["id"]
