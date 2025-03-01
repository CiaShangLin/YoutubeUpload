# 數據模型類
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