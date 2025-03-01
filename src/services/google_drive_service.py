from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from ..utils.logger import logger

class GoogleDriveService:
    # 如果修改這些範圍，請刪除token.pickle檔案
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    CLIENT_SECRET_FILE = 'token.json'
    TOKEN_PICKLE_FILE = 'google_drive_token.pickle'
    REPLAY_FOLDER_ID = '1ZJLoKqzxymZ9XUyYeOWmvZkeEwxTti-x'
    
    def __init__(self):
        self.service = self._get_service()
    
    def _get_service(self):
        """獲取已認證的Google Drive服務"""
        creds = None
        # token.pickle儲存使用者的存取權和重新整理權杖
        if os.path.exists(self.TOKEN_PICKLE_FILE):
            with open(self.TOKEN_PICKLE_FILE, 'rb') as token:
                creds = pickle.load(token)
                
        # 如果沒有可用的（有效的）憑證，讓使用者登入
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
                
            # 儲存憑證以供下次執行使用
            with open(self.TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)
                
        return build('drive', 'v3', credentials=creds)
    
    def _cut_string(self, input_string):
        """從檔案名稱中提取有用部分"""
        index = input_string.find("【StarCraft II】")
        if index != -1:
            return input_string[index:]
        return input_string
    
    def upload_replay(self, file_path):
        """上傳重播文件到Google Drive"""
        if not file_path:
            logger.warning("未提供文件路徑")
            return ""
            
        try:
            file_metadata = {
                'name': self._cut_string(file_path), 
                'parents': [self.REPLAY_FOLDER_ID]
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f'File ID: {file_id}')
            
            # 設定共享權限
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self.service.permissions().create(
                fileId=file_id, 
                body=permission
            ).execute()
            
            # 取得檔案URL
            file_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
            logger.info(f'File URL: {file_url}')
            return file_url
            
        except Exception as e:
            logger.error(f"上傳重播文件時出錯: {str(e)}")
            return ""
    
    def list_folders(self):
        """列出Google Drive中的所有資料夾"""
        try:
            results = self.service.files().list(
                q="mimeType='application/vnd.google-apps.folder'",
                pageSize=100,
                spaces='drive',
                fields="files(id, name, createdTime, webViewLink, parents)"
            ).execute()
            
            folders = results.get('files', [])
            
            if not folders:
                logger.info('未找到任何資料夾.')
                return []
                
            logger.info(f'找到 {len(folders)} 個資料夾')
            for folder in folders:
                logger.info(f"資料夾名稱: {folder['name']}")
                logger.info(f"資料夾ID: {folder['id']}")
                
            return folders
            
        except Exception as e:
            logger.error(f"列出資料夾時出錯: {str(e)}")
            return [] 