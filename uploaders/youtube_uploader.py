"""
YouTube 上傳器
實作 YouTube 影片上傳功能
"""

import random
import time
from typing import List, Dict, Optional
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from uploaders.base_uploader import BaseUploader
from video_item import VideoItem
from token_manager import TokenManager
import UploadGoogleDrive


# 重試設定
MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# YouTube 設定
CATEGORY_ID = "20"  # Gaming
KEYWORDS = "StarCraft II, Starcraft 2, SC2, 星海爭霸2, Ladder, 天梯, Ranked Match, Protoss, 神族, Zerg, 蟲族, Terran, 人族, Nzx, Gameplay, SC2 Strategy, PvP, PvZ, PvT, IEM, ESL, KR Server"

# 多語言翻譯
ENG_TO_TW = {"Protoss": "神族", "Zerg": "蟲族", "Terran": "人族", "Random": "隨機"}
ENG_TO_JA = {"Protoss": "プロトス", "Zerg": "ザーグ", "Terran": "テラン", "Random": "ランダム"}
ENG_TO_KR = {"Protoss": "프로토스", "Zerg": "저그", "Terran": "테란", "Random": "랜덤"}


class YouTubeUploader(BaseUploader):
    """YouTube 上傳器"""
    
    def __init__(self, token_manager: TokenManager):
        """
        初始化 YouTube 上傳器
        
        Args:
            token_manager: Token 管理器
        """
        self.token_manager = token_manager
    
    def upload(self, video: VideoItem) -> str:
        """
        上傳影片到 YouTube
        
        Args:
            video: 影片資料
            
        Returns:
            str: YouTube 影片 ID
            
        Raises:
            Exception: 上傳失敗時拋出異常
        """
        # 驗證影片資料
        if not self.validate_video(video):
            raise ValueError("影片資料不完整")
        
        # 1. 上傳 Replay 到 Google Drive（如果有）
        replay_url = ""
        if video.has_replay:
            try:
                print(f"上傳 Replay: {video.replay_path}")
                replay_url = UploadGoogleDrive.upload_replay(video.replay_path)
                video.set_replay_url(replay_url)
                print(f"Replay URL: {replay_url}")
            except Exception as e:
                print(f"Replay 上傳失敗: {str(e)}")
                # Replay 上傳失敗不影響影片上傳
        
        # 2. 準備影片描述
        social_links = self._get_social_links()
        description = self._get_description(video.title, replay_url, social_links)
        
        # 3. 取得 YouTube 憑證
        creds = self.token_manager.get_youtube_credentials()
        if not creds:
            raise Exception("無法取得 YouTube 憑證，請先進行認證")
        
        # 4. 建立 YouTube 服務
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=creds
        )
        
        # 5. 準備上傳參數
        tags = KEYWORDS.split(",")
        if video.game_name and video.game_name not in tags:
            tags.append(video.game_name)
        
        # 6. 處理發布時間
        publish_at = None
        privacy_status = "private"
        
        if video.publish_time:
            from datetime import datetime
            if video.publish_time > datetime.now():
                publish_at = video.publish_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
                privacy_status = "private"  # 預約發布必須先設為 private
        
        # 7. 建立上傳請求
        body = {
            "snippet": {
                "title": video.title,
                "description": description,
                "tags": tags,
                "categoryId": CATEGORY_ID,
            },
            "status": {
                "privacyStatus": privacy_status,
            }
        }
        
        if publish_at:
            body["status"]["publishAt"] = publish_at
        
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video.video_path, chunksize=-1, resumable=True)
        )
        
        # 8. 執行上傳
        video_id = self._resumable_upload(insert_request)
        
        print(f"✅ 影片上傳成功: {video_id}")
        return video_id
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
        設定影片縮圖
        
        Args:
            video_id: YouTube 影片 ID
            thumbnail_path: 縮圖檔案路徑
            
        Returns:
            bool: 是否成功
        """
        try:
            creds = self.token_manager.get_youtube_credentials()
            if not creds:
                return False
            
            youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=creds
            )
            
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            
            print(f"✅ 縮圖設定成功: {video_id}")
            return True
            
        except Exception as e:
            print(f"❌ 縮圖設定失敗: {str(e)}")
            return False
    
    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        """
        將影片加入播放清單
        
        Args:
            video_id: YouTube 影片 ID
            playlist_ids: 播放清單 ID 列表
            
        Returns:
            bool: 是否成功
        """
        try:
            creds = self.token_manager.get_youtube_credentials()
            if not creds:
                return False
            
            youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=creds
            )
            
            for playlist_id in playlist_ids:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        'snippet': {
                            'playlistId': playlist_id,
                            'resourceId': {
                                'kind': 'youtube#video',
                                'videoId': video_id
                            }
                        }
                    }
                ).execute()
                print(f"✅ 加入播放清單: {playlist_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ 加入播放清單失敗: {str(e)}")
            return False
    
    def add_localizations(self, video_id: str, replay_url: str) -> bool:
        """
        添加多國語言字幕
        
        Args:
            video_id: YouTube 影片 ID
            replay_url: Replay 檔案 URL
            
        Returns:
            bool: 是否成功
        """
        try:
            creds = self.token_manager.get_youtube_credentials()
            if not creds:
                return False
            
            youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=creds
            )
            
            # 取得影片資訊
            video_response = youtube.videos().list(
                part="snippet,localizations",
                id=video_id
            ).execute()
            
            if not video_response['items']:
                return False
            
            video = video_response['items'][0]
            snippet = video['snippet']
            existing_localizations = video.get('localizations', {})
            
            # 設定預設語言
            snippet['defaultLanguage'] = "en"
            
            # 準備多語言內容
            en_title = snippet['title']
            en_description = self._get_description(en_title, replay_url, include_social=False)
            
            social_links = self._get_social_links()
            
            # 繁體中文
            zh_tw_title = self._translate_title(en_title, ENG_TO_TW)
            zh_tw_description = self._get_description(zh_tw_title, replay_url, social_links)
            
            # 日文
            ja_title = self._translate_title(en_title, ENG_TO_JA)
            ja_description = self._get_description(ja_title, replay_url, social_links)
            
            # 韓文
            ko_title = self._translate_title(en_title, ENG_TO_KR)
            ko_description = self._get_description(ko_title, replay_url, social_links)
            
            # 更新本地化內容
            localizations = {
                'zh-TW': {'title': zh_tw_title, 'description': zh_tw_description},
                'ja': {'title': ja_title, 'description': ja_description},
                'ko': {'title': ko_title, 'description': ko_description}
            }
            
            existing_localizations.update(localizations)
            
            # 更新影片
            youtube.videos().update(
                part="snippet,localizations",
                body=dict(
                    id=video_id,
                    snippet=snippet,
                    localizations=existing_localizations
                )
            ).execute()
            
            print(f"✅ 多國語言設定成功")
            return True
            
        except Exception as e:
            print(f"❌ 多國語言設定失敗: {str(e)}")
            return False
    
    def _resumable_upload(self, insert_request) -> str:
        """
        可恢復的上傳
        
        Args:
            insert_request: YouTube API 上傳請求
            
        Returns:
            str: 影片 ID
        """
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                print("上傳中...")
                status, response = insert_request.next_chunk()
                
                if response is not None:
                    if 'id' in response:
                        return response['id']
                    else:
                        raise Exception(f"上傳失敗，未預期的回應: {response}")
                        
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"HTTP 錯誤 {e.resp.status}: {e.content}"
                else:
                    raise
                    
            except Exception as e:
                error = f"上傳錯誤: {str(e)}"
            
            if error is not None:
                print(f"⚠️ {error}")
                retry += 1
                
                if retry > MAX_RETRIES:
                    raise Exception("重試次數已達上限")
                
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"等待 {sleep_seconds:.1f} 秒後重試...")
                time.sleep(sleep_seconds)
                error = None
    
    def _get_description(self, title: str, replay_url: str, 
                        social_links: str = "", include_social: bool = True) -> str:
        """
        生成影片描述
        
        Args:
            title: 影片標題
            replay_url: Replay URL
            social_links: 社群連結
            include_social: 是否包含社群連結
            
        Returns:
            str: 影片描述
        """
        tags = '#starcraft2 #星海爭霸2 #gaming'
        rp = f'RP : {replay_url}' if replay_url else ""
        
        if include_social and social_links:
            return f'{tags}\n{title}\n{rp}\n{social_links}'
        else:
            return f'{tags}\n{title}\n{rp}'
    
    def _translate_title(self, title: str, translation_dict: Dict[str, str]) -> str:
        """
        翻譯標題
        
        Args:
            title: 原始標題
            translation_dict: 翻譯字典
            
        Returns:
            str: 翻譯後的標題
        """
        for eng, translated in translation_dict.items():
            title = title.replace(eng, translated)
        return title
    
    def _get_social_links(self) -> str:
        """
        取得社群連結
        
        Returns:
            str: 社群連結文字
        """
        paypal = 'Paypal斗內連結 \nhttps://www.paypal.com/paypalme/Sc2Nzs906?country.x=TW&locale.x=zh_TW'
        opay = '歐富寶斗內連結 \nhttps://payment.opay.tw/Broadcaster/Donate/F7149E2B175ACA220EAD8B99E1F69EB8'
        facebook = 'Facebook_粉絲團 \nhttps://www.facebook.com/profile.php?id=61550685848292'
        instagram = 'Instagram粉絲團 \nhttps://www.instagram.com/sc2nzs906/'
        thread = 'Thread粉絲團 \nhttps://www.threads.com/@sc2nzs906?xmt=AQGzwQoSE8s-7o1yAmyIpw_aDv1pe5Rj7ew0QsQQJiFPq_I'
        youtube = '加入Nzs的頻道會員神族一起偉大 \nhttps://www.youtube.com/@Sc2Nzs906'
        end_message = '記得幫我按讚訂閱開啟小鈴鐺\n感謝大家~~'
        
        return f"{paypal}\n{opay}\n{facebook}\n{instagram}\n{thread}\n{youtube}\n{end_message}"


if __name__ == '__main__':
    print("YouTubeUploader 需要配合 TokenManager 使用")
    print("請參考 main.py 中的使用範例")
