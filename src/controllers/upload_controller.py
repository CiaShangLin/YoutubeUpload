from ..services.youtube_service import YouTubeService
from ..services.google_drive_service import GoogleDriveService
from ..utils.logger import logger
from ..config.settings import (
    YOUTUBE_UPLOAD_SCOPE, 
    YOUTUBE_SSL_SCOPE, 
    UPLOAD_TOKEN_FILE, 
    LOGIN_TOKEN_FILE,
    PLAYLIST_IDS,
    LANGUAGE_MAPPINGS
)
import os
import re

class UploadController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.youtube_service = YouTubeService()
        self.drive_service = GoogleDriveService()
        
    def handle_upload(self):
        """處理上傳流程"""
        try:
            # 1. 上傳重播文件到Google Drive（如果有）
            replay_url = ""
            if self.model.replay_path:
                logger.info(f"上傳重播文件: {self.model.replay_path}")
                replay_url = self.drive_service.upload_replay(self.model.replay_path)
            
            # 2. 準備多語言標題和描述
            localizations = self._prepare_localizations(replay_url)
            
            # 3. 獲取YouTube服務
            youtube = self.youtube_service.get_authenticated_service(
                UPLOAD_TOKEN_FILE, 
                YOUTUBE_UPLOAD_SCOPE
            )
            
            # 4. 上傳視頻
            logger.info(f"上傳視頻: {self.model.video_path}")
            video_id = self.youtube_service.upload_video(youtube, self.model)
            
            # 5. 設置縮略圖（如果有）
            if self.model.thumbnail_path:
                logger.info(f"設置縮略圖: {self.model.thumbnail_path}")
                self.youtube_service.set_thumbnail(youtube, video_id, self.model.thumbnail_path)
            
            # 6. 獲取SSL服務（用於播放列表和本地化）
            ssl_service = self.youtube_service.get_authenticated_service(
                LOGIN_TOKEN_FILE, 
                YOUTUBE_SSL_SCOPE
            )
            
            # 7. 添加到播放列表
            playlists = self._get_playlists()
            if playlists:
                logger.info(f"添加到播放列表: {playlists}")
                self.youtube_service.add_video_to_playlist(ssl_service, video_id, playlists)
            
            # 8. 添加多語言版本
            if localizations:
                logger.info("添加多語言版本")
                self.youtube_service.add_video_localizations(ssl_service, video_id, localizations)
            
            # 9. 通知用戶上傳成功
            self.view.show_success_message(f"視頻已成功上傳，ID: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"上傳過程中出錯: {str(e)}")
            self.view.show_error_message(f"上傳失敗: {str(e)}")
            return False
    
    def _get_playlists(self):
        """根據用戶選擇獲取播放列表ID"""
        playlists = []
        
        if self.view.is_pvz_checked():
            playlists.append(PLAYLIST_IDS["PVZ"])
            
        if self.view.is_pvp_checked():
            playlists.append(PLAYLIST_IDS["PVP"])
            
        if self.view.is_pvt_checked():
            playlists.append(PLAYLIST_IDS["PVT"])
            
        if self.view.is_rank_checked():
            playlists.append(PLAYLIST_IDS["SC2_RANK"])
            
        return playlists
    
    def _prepare_localizations(self, replay_url):
        """準備多語言版本的標題和描述"""
        localizations = {}
        
        # 獲取英文標題和描述（默認）
        en_title = self.model.title
        en_description = self._get_description(en_title, replay_url)
        
        # 如果啟用了中文
        if self.view.is_chinese_enabled():
            zh_title = self._translate_title(en_title, LANGUAGE_MAPPINGS["eng_to_tw"])
            zh_description = self._get_description(zh_title, replay_url)
            localizations["zh-TW"] = {"title": zh_title, "description": zh_description}
        
        # 可以添加更多語言...
        
        return localizations
    
    def _translate_title(self, title, translation_map):
        """使用映射表翻譯標題"""
        translated = title
        for eng, translated_text in translation_map.items():
            translated = translated.replace(eng, translated_text)
        return translated
    
    def _get_description(self, title, replay_url):
        """生成視頻描述"""
        tags = '#starcraft2 #星海爭霸2 #gaming'
        rp = f'RP : {replay_url}' if replay_url else ""
        return f'{tags}\n{title}\n{rp}'
    
    def handle_file_selection(self, file_type):
        """處理文件選擇"""
        file_path = self.view.open_file_dialog()
        if not file_path:
            return
            
        if file_type == "video":
            self.model.video_path = file_path
            self.view.set_video_path(file_path)
            
            # 從文件名自動生成標題
            title = self._generate_title_from_filename(file_path)
            self.model.title = title
            self.view.set_title(title)
            
            # 自動檢測對戰類型
            self._detect_matchup_from_filename(file_path)
            
        elif file_type == "thumbnail":
            self.model.thumbnail_path = file_path
            self.view.set_thumbnail_path(file_path)
            
        elif file_type == "replay":
            self.model.replay_path = file_path
            self.view.set_replay_path(file_path)
    
    def _generate_title_from_filename(self, file_path):
        """從文件名生成標題"""
        basename = os.path.basename(file_path)
        name_without_ext = basename.rsplit(".", 1)[0].strip()
        
        pattern = r"(【StarCraft II】.*?KR Server)"
        match = re.search(pattern, name_without_ext)
        
        if match:
            game_name = self.model.game_name if self.model.game_name else "StarCraft II"
            return match.group(1).replace("【StarCraft II】", f"【{game_name}】")
            
        return name_without_ext
    
    def _detect_matchup_from_filename(self, file_path):
        """從文件名檢測對戰類型"""
        basename = os.path.basename(file_path)
        pattern = r".*\((Protoss|Zerg|Terran)(?:\s*\d*)\)\s*vs\s*.*\((Protoss|Zerg|Terran)(?:\s*\d*)\)"
        match = re.search(pattern, basename, re.IGNORECASE)
        
        if match:
            left_race, right_race = match.groups()
            
            # 重置所有對戰類型選擇
            self.view.set_pvp_checked(False)
            self.view.set_pvz_checked(False)
            self.view.set_pvt_checked(False)
            
            # 根據檢測到的對戰類型設置選擇
            if left_race.lower() == "protoss" and right_race.lower() == "protoss":
                self.view.set_pvp_checked(True)
                
            elif left_race.lower() == "protoss" and right_race.lower() == "zerg":
                self.view.set_pvz_checked(True)
                
            elif left_race.lower() == "protoss" and right_race.lower() == "terran":
                self.view.set_pvt_checked(True) 