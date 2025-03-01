# YouTube API 配置
CLIENT_SECRETS_FILE = "token.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
LOGIN_TOKEN_FILE = "login_token.json"
UPLOAD_TOKEN_FILE = "upload_token.json"
CHANNEL_ID = 'UC9RrMSH_OaUP2kIFqzPrBpw'

# 視頻配置
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
CATEGORY_ID = "20"
DEFAULT_KEYWORDS = "StarCraft II, Starcraft 2, SC2, 星海爭霸2, Ladder, 天梯, Ranked Match, Protoss, 神族, Zerg, 蟲族, Terran, 人族, Nzx, Gameplay, SC2 Strategy, PvP, PvZ, PvT, IEM, ESL, KR Server"

# 播放列表ID
PLAYLIST_IDS = {
    "PVT": "PL8TREsr2ZmqYpi_IM1zSQSarofDQftjLj",
    "PVZ": "PL8TREsr2ZmqaY8-tTDPvTLYRH38dtvY4I",
    "PVP": "PL8TREsr2ZmqbGXupnsOkyzoFTkr12cmVF",
    "PVR": "PL8TREsr2ZmqY80QnGjRpFpxcq2ES_YGKf",
    "SC2_RANK": "PL8TREsr2ZmqbIAM5TODn26C8my3cNiRev"
}

# 語言翻譯映射
LANGUAGE_MAPPINGS = {
    "eng_to_tw": {"Protoss": "神族", "Zerg": "蟲族", "Terran": "人族", "Random": "隨機"},
    "eng_to_ja": {"Protoss": "プロトス", "Zerg": "ザーグ", "Terran": "テラン", "Random": "ランダム"},
    "eng_to_kr": {"Protoss": "프로トス", "Zerg": "저그", "Terran": "テラン", "Random": "랜덤"},
    "eng_to_ch": {"Protoss": "神族", "Zerg": "虫族", "Terran": "人类", "Random": "随机"}
}

# Google Drive 配置
GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']
GOOGLE_DRIVE_TOKEN_FILE = 'google_drive_token.pickle'
REPLAY_FOLDER_ID = '1ZJLoKqzxymZ9XUyYeOWmvZkeEwxTti-x' 