from youtube_service import YouTubeService

# 控制器類
class UploadController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.youtube_service = YouTubeService()
        
    def handle_upload(self):
        # 處理上傳邏輯
        pass 