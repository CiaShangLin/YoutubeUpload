from ..services.youtube_service import YouTubeService

class UploadController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.youtube_service = YouTubeService()
        
    def handle_upload(self):
        # 處理上傳邏輯
        pass 