"""
影片資料模型
定義單一影片的所有資訊和狀態
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class UploadStatus(Enum):
    """上傳狀態枚舉"""
    PENDING = "待上傳"
    UPLOADING = "上傳中"
    COMPLETED = "已完成"
    FAILED = "失敗"


class MatchType(Enum):
    """對戰類型枚舉"""
    PVP = "PVP"
    PVZ = "PVZ"
    PVT = "PVT"
    PVR = "PVR"  # Protoss vs Random
    UNKNOWN = "未知"


@dataclass
class VideoItem:
    """
    影片資料模型
    
    封裝單一影片的所有資訊，包括檔案路徑、標題、描述、
    發布時間、播放清單等
    """
    
    # 必填欄位
    video_path: str
    title: str
    
    # 選填欄位
    thumbnail_path: Optional[str] = None
    replay_path: Optional[str] = None
    description: str = ""
    publish_time: Optional[datetime] = None
    game_name: str = "StarCraft II"
    
    # 播放清單（使用 ID 列表）
    playlist_ids: List[str] = field(default_factory=list)
    
    # 對戰類型
    match_type: MatchType = MatchType.UNKNOWN
    
    # 字幕語言
    subtitle_languages: List[str] = field(default_factory=lambda: ["en", "zh-TW"])
    
    # 上傳狀態
    status: UploadStatus = UploadStatus.PENDING
    
    # 上傳後的影片 ID
    video_id: Optional[str] = None
    
    # 錯誤訊息（如果上傳失敗）
    error_message: Optional[str] = None
    
    # Replay 上傳後的 URL
    replay_url: Optional[str] = None
    
    def __post_init__(self):
        """初始化後處理"""
        # 如果沒有設定發布時間，預設為當天 18:00
        if self.publish_time is None:
            now = datetime.now()
            self.publish_time = datetime(now.year, now.month, now.day, 18, 0)
    
    @property
    def status_text(self) -> str:
        """狀態文字"""
        return self.status.value
    
    @property
    def match_type_text(self) -> str:
        """對戰類型文字"""
        return self.match_type.value
    
    @property
    def publish_time_str(self) -> str:
        """發布時間字串"""
        if self.publish_time:
            return self.publish_time.strftime("%Y-%m-%d %H:%M")
        return ""
    
    @property
    def has_thumbnail(self) -> bool:
        """是否有縮圖"""
        return self.thumbnail_path is not None and self.thumbnail_path != ""
    
    @property
    def has_replay(self) -> bool:
        """是否有 Replay 檔案"""
        return self.replay_path is not None and self.replay_path != ""
    
    def set_status(self, status: UploadStatus, error_message: Optional[str] = None):
        """
        設定上傳狀態
        
        Args:
            status: 新的狀態
            error_message: 錯誤訊息（如果狀態為 FAILED）
        """
        self.status = status
        if status == UploadStatus.FAILED:
            self.error_message = error_message
    
    def set_video_id(self, video_id: str):
        """
        設定上傳後的影片 ID
        
        Args:
            video_id: YouTube 影片 ID
        """
        self.video_id = video_id
        self.status = UploadStatus.COMPLETED
    
    def set_replay_url(self, replay_url: str):
        """
        設定 Replay 檔案的 URL
        
        Args:
            replay_url: Google Drive 分享連結
        """
        self.replay_url = replay_url
    
    def to_dict(self) -> dict:
        """
        轉換為字典格式（用於序列化）
        
        Returns:
            dict: 影片資料字典
        """
        return {
            'video_path': self.video_path,
            'title': self.title,
            'thumbnail_path': self.thumbnail_path,
            'replay_path': self.replay_path,
            'description': self.description,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'game_name': self.game_name,
            'playlist_ids': self.playlist_ids,
            'match_type': self.match_type.value,
            'subtitle_languages': self.subtitle_languages,
            'status': self.status.value,
            'video_id': self.video_id,
            'error_message': self.error_message,
            'replay_url': self.replay_url
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VideoItem':
        """
        從字典創建 VideoItem（用於反序列化）
        
        Args:
            data: 影片資料字典
            
        Returns:
            VideoItem: 影片物件
        """
        # 轉換發布時間
        publish_time = None
        if data.get('publish_time'):
            publish_time = datetime.fromisoformat(data['publish_time'])
        
        # 轉換對戰類型
        match_type = MatchType.UNKNOWN
        if data.get('match_type'):
            try:
                match_type = MatchType(data['match_type'])
            except ValueError:
                pass
        
        # 轉換狀態
        status = UploadStatus.PENDING
        if data.get('status'):
            try:
                status = UploadStatus(data['status'])
            except ValueError:
                pass
        
        return cls(
            video_path=data['video_path'],
            title=data['title'],
            thumbnail_path=data.get('thumbnail_path'),
            replay_path=data.get('replay_path'),
            description=data.get('description', ''),
            publish_time=publish_time,
            game_name=data.get('game_name', 'StarCraft II'),
            playlist_ids=data.get('playlist_ids', []),
            match_type=match_type,
            subtitle_languages=data.get('subtitle_languages', ['en', 'zh-TW']),
            status=status,
            video_id=data.get('video_id'),
            error_message=data.get('error_message'),
            replay_url=data.get('replay_url')
        )


if __name__ == '__main__':
    # 測試用程式碼
    import json
    
    # 創建測試影片
    video = VideoItem(
        video_path="/path/to/video.mp4",
        title="【StarCraft II】Nzs (Protoss) vs Opponent (Zerg) - KR Server",
        thumbnail_path="/path/to/thumbnail.jpg",
        replay_path="/path/to/replay.SC2Replay",
        match_type=MatchType.PVZ,
        playlist_ids=["playlist1", "playlist2"]
    )
    
    print("=== VideoItem 測試 ===")
    print(f"標題: {video.title}")
    print(f"對戰類型: {video.match_type_text}")
    print(f"發布時間: {video.publish_time_str}")
    print(f"狀態: {video.status_text}")
    print(f"有縮圖: {video.has_thumbnail}")
    print(f"有 Replay: {video.has_replay}")
    
    # 測試序列化
    print("\n=== 序列化測試 ===")
    data = video.to_dict()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 測試反序列化
    print("\n=== 反序列化測試 ===")
    video2 = VideoItem.from_dict(data)
    print(f"標題: {video2.title}")
    print(f"對戰類型: {video2.match_type_text}")
