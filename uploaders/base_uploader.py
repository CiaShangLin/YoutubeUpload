"""
上傳器抽象基類
定義所有平台上傳器的統一介面
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from video_item import VideoItem


class BaseUploader(ABC):
    """上傳器基類"""
    
    @abstractmethod
    def upload(self, video: VideoItem) -> str:
        """
        上傳影片
        
        Args:
            video: 影片資料
            
        Returns:
            str: 影片 ID
            
        Raises:
            Exception: 上傳失敗時拋出異常
        """
        pass
    
    @abstractmethod
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
        設定影片縮圖
        
        Args:
            video_id: 影片 ID
            thumbnail_path: 縮圖檔案路徑
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        """
        將影片加入播放清單
        
        Args:
            video_id: 影片 ID
            playlist_ids: 播放清單 ID 列表
            
        Returns:
            bool: 是否成功
        """
        pass
    
    def validate_video(self, video: VideoItem) -> bool:
        """
        驗證影片資料是否完整
        
        Args:
            video: 影片資料
            
        Returns:
            bool: 是否有效
        """
        if not video.video_path:
            return False
        if not video.title:
            return False
        return True


if __name__ == '__main__':
    print("BaseUploader 是抽象基類，不能直接實例化")
    print("請使用 YouTubeUploader 或 BilibiliUploader")
