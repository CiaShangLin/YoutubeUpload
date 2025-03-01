class VideoData:
    def __init__(self):
        self.video_path = ""
        self.thumbnail_path = ""
        self.replay_path = ""
        self.title = ""
        self.description = ""
        self.playlists = []
        self.languages = []
        self.game_name = "StarCraft II"
        self.publish_time = None
        self.category_id = "20"
        self.keywords = ""
        self.privacy_status = "private"
        
    @property
    def file(self):
        """兼容UploadArgs的屬性"""
        return self.video_path 