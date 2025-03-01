from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import httplib2
import random
import time
from oauth2client import client, tools, file
from ..utils.logger import logger
from ..utils.error_handler import handle_error, UploadError

class YouTubeService:
    def __init__(self):
        self.MAX_RETRIES = 10
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        
    def get_authenticated_service(self, token_path, scope):
        """
        获取已认证的YouTube服务
        """
        try:
            credential_path = token_path
            store = file.Storage(credential_path)
            credentials = store.get()
            
            if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(token_path, scope)
                credentials = tools.run_flow(flow, store)
            
            return build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"認證YouTube服務時出錯: {str(e)}")
            raise
    
    def upload_video(self, youtube, options):
        """上傳視頻到YouTube"""
        tags = options.keywords.split(",") if options.keywords else []
        
        body = {
            "snippet": {
                "title": options.title,
                "description": options.description,
                "tags": tags,
                "categoryId": options.category_id,
            },
            "status": {
                "privacyStatus": options.privacy_status,
            }
        }
        
        # 如果設置了發布時間
        if hasattr(options, 'publish_at') and options.publish_at:
            body["status"]["privacyStatus"] = "private"
            body["status"]["publishAt"] = options.publish_at
            
        try:
            insert_request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
            )
            return self._resumable_upload(insert_request)
        except Exception as e:
            logger.error(f"準備上傳視頻時出錯: {str(e)}")
            raise
    
    def _resumable_upload(self, insert_request):
        """處理可恢復的上傳過程"""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                logger.info("正在上傳文件...")
                status, response = insert_request.next_chunk()
                
                if response is not None:
                    if 'id' in response:
                        logger.info(f"視頻ID '{response['id']}' 已成功上傳。")
                        return response['id']
                    else:
                        error_msg = f"上傳失敗，意外的響應: {response}"
                        logger.error(error_msg)
                        raise UploadError(error_msg)
                        
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = f"發生可重試的HTTP錯誤 {e.resp.status}: {e.content}"
                else:
                    raise
                    
            except self.RETRIABLE_EXCEPTIONS as e:
                error = f"發生可重試的錯誤: {e}"

            if error is not None:
                logger.error(error)
                retry += 1
                
                if retry > self.MAX_RETRIES:
                    logger.error("不再嘗試重試。")
                    raise UploadError("超過最大重試次數")
                    
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                logger.info(f"休眠 {sleep_seconds} 秒後重試...")
                time.sleep(sleep_seconds)
    
    def set_thumbnail(self, youtube, video_id, thumbnail_path):
        """設置視頻縮略圖"""
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            logger.info(f"已為視頻ID '{video_id}' 設置縮略圖。")
        except Exception as e:
            logger.error(f"設置縮略圖時出錯: {str(e)}")
            raise
    
    def add_video_to_playlist(self, youtube, video_id, playlist_ids):
        """將視頻添加到播放列表"""
        for playlist_id in playlist_ids:
            try:
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
                logger.info(f"視頻ID '{video_id}' 已添加到播放列表ID '{playlist_id}'。")
            except Exception as e:
                logger.error(f"將視頻添加到播放列表時出錯: {str(e)}")
                
    def add_video_localizations(self, youtube, video_id, localizations):
        """添加視頻的多語言版本"""
        try:
            video_response = youtube.videos().list(
                part="snippet,localizations",
                id=video_id
            ).execute()

            video = video_response['items'][0]
            snippet = video['snippet']
            existing_localizations = video.get('localizations', {})
            snippet['defaultLanguage'] = "en"
            existing_localizations.update(localizations)

            youtube.videos().update(
                part="snippet,localizations",
                body=dict(
                    id=video_id,
                    snippet=snippet,
                    localizations=existing_localizations
                )
            ).execute()
            logger.info(f"已更新視頻 '{video_id}' 的多語言版本")
        except Exception as e:
            logger.error(f"添加視頻多語言版本時出錯: {str(e)}")
            raise 