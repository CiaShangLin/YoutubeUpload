"""
B站上傳器（預留介面）
未來可實作 Bilibili 影片上傳功能
"""

from typing import List
from uploaders.base_uploader import BaseUploader
from video_item import VideoItem


class BilibiliUploader(BaseUploader):
    """B站上傳器 - 預留介面"""
    
    def __init__(self):
        """初始化 B站上傳器"""
        pass
    
    def upload(self, video: VideoItem) -> str:
        """
        上傳影片到 B站
        
        Args:
            video: 影片資料
            
        Returns:
            str: B站影片 ID
            
        Raises:
            NotImplementedError: 功能尚未實作
        """
        raise NotImplementedError("B站上傳功能尚未實作")
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
        設定影片封面
        
        Args:
            video_id: B站影片 ID
            thumbnail_path: 封面檔案路徑
            
        Returns:
            bool: 是否成功
            
        Raises:
            NotImplementedError: 功能尚未實作
        """
        raise NotImplementedError("B站上傳功能尚未實作")
    
    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        """
        將影片加入合集
        
        Args:
            video_id: B站影片 ID
            playlist_ids: 合集 ID 列表
            
        Returns:
            bool: 是否成功
            
        Raises:
            NotImplementedError: 功能尚未實作
        """
        raise NotImplementedError("B站上傳功能尚未實作")


if __name__ == '__main__':
    print("BilibiliUploader 是預留介面，尚未實作")
    print("未來可以在這裡實作 B站上傳功能")
