"""
Token 管理器 - 統一管理所有 OAuth Token
支援 YouTube 和 Google Drive 的認證管理
"""

import os
import pickle
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


@dataclass
class TokenStatus:
    """Token 狀態資料類別"""
    name: str
    is_valid: bool
    expiry: Optional[datetime]
    error_message: Optional[str] = None
    
    @property
    def status_text(self) -> str:
        """狀態文字描述"""
        if not self.is_valid:
            return "❌ 已過期或無效"
        if self.expiry:
            return f"✅ 有效 (至 {self.expiry.strftime('%Y-%m-%d %H:%M:%S')})"
        return "✅ 有效"


class TokenManager:
    """統一的 Token 管理器"""
    
    # Token 檔案路徑
    YOUTUBE_TOKEN_FILE = "youtube_token.pickle"
    GOOGLE_DRIVE_TOKEN_FILE = "google_drive_token.pickle"
    CLIENT_SECRETS_FILE = "token.json"
    
    # OAuth Scopes
    YOUTUBE_SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    GOOGLE_DRIVE_SCOPES = [
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self):
        """初始化 Token 管理器"""
        self._youtube_creds: Optional[Credentials] = None
        self._google_drive_creds: Optional[Credentials] = None
    
    def check_all_tokens(self) -> Dict[str, TokenStatus]:
        """
        檢查所有 token 狀態
        
        Returns:
            Dict[str, TokenStatus]: Token 名稱對應的狀態資訊
        """
        statuses = {}
        
        # 檢查 YouTube Token
        try:
            youtube_creds = self._load_credentials(
                self.YOUTUBE_TOKEN_FILE,
                self.YOUTUBE_SCOPES
            )
            
            if youtube_creds and youtube_creds.valid:
                statuses['YouTube'] = TokenStatus(
                    name='YouTube',
                    is_valid=True,
                    expiry=youtube_creds.expiry
                )
            elif youtube_creds and youtube_creds.expired and youtube_creds.refresh_token:
                statuses['YouTube'] = TokenStatus(
                    name='YouTube',
                    is_valid=False,
                    expiry=youtube_creds.expiry,
                    error_message="Token 已過期，可嘗試刷新"
                )
            else:
                statuses['YouTube'] = TokenStatus(
                    name='YouTube',
                    is_valid=False,
                    expiry=None,
                    error_message="Token 不存在或無效，需要重新認證"
                )
        except Exception as e:
            statuses['YouTube'] = TokenStatus(
                name='YouTube',
                is_valid=False,
                expiry=None,
                error_message=f"檢查失敗: {str(e)}"
            )
        
        # 檢查 Google Drive Token
        try:
            drive_creds = self._load_credentials(
                self.GOOGLE_DRIVE_TOKEN_FILE,
                self.GOOGLE_DRIVE_SCOPES
            )
            
            if drive_creds and drive_creds.valid:
                statuses['Google Drive'] = TokenStatus(
                    name='Google Drive',
                    is_valid=True,
                    expiry=drive_creds.expiry
                )
            elif drive_creds and drive_creds.expired and drive_creds.refresh_token:
                statuses['Google Drive'] = TokenStatus(
                    name='Google Drive',
                    is_valid=False,
                    expiry=drive_creds.expiry,
                    error_message="Token 已過期，可嘗試刷新"
                )
            else:
                statuses['Google Drive'] = TokenStatus(
                    name='Google Drive',
                    is_valid=False,
                    expiry=None,
                    error_message="Token 不存在或無效，需要重新認證"
                )
        except Exception as e:
            statuses['Google Drive'] = TokenStatus(
                name='Google Drive',
                is_valid=False,
                expiry=None,
                error_message=f"檢查失敗: {str(e)}"
            )
        
        return statuses
    
    def refresh_token(self, token_type: str) -> bool:
        """
        刷新指定類型的 token
        
        Args:
            token_type: 'youtube' 或 'google_drive'
            
        Returns:
            bool: 刷新是否成功
        """
        try:
            if token_type.lower() == 'youtube':
                creds = self._load_credentials(
                    self.YOUTUBE_TOKEN_FILE,
                    self.YOUTUBE_SCOPES
                )
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self._save_credentials(creds, self.YOUTUBE_TOKEN_FILE)
                    self._youtube_creds = creds
                    return True
                    
            elif token_type.lower() == 'google_drive':
                creds = self._load_credentials(
                    self.GOOGLE_DRIVE_TOKEN_FILE,
                    self.GOOGLE_DRIVE_SCOPES
                )
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self._save_credentials(creds, self.GOOGLE_DRIVE_TOKEN_FILE)
                    self._google_drive_creds = creds
                    return True
            
            return False
            
        except Exception as e:
            print(f"刷新 {token_type} token 失敗: {str(e)}")
            return False
    
    def authenticate(self, token_type: str) -> bool:
        """
        執行 OAuth 認證流程
        
        Args:
            token_type: 'youtube' 或 'google_drive'
            
        Returns:
            bool: 認證是否成功
        """
        try:
            if token_type.lower() == 'youtube':
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE,
                    self.YOUTUBE_SCOPES
                )
                creds = flow.run_local_server(port=0)
                self._save_credentials(creds, self.YOUTUBE_TOKEN_FILE)
                self._youtube_creds = creds
                return True
                
            elif token_type.lower() == 'google_drive':
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE,
                    self.GOOGLE_DRIVE_SCOPES
                )
                creds = flow.run_local_server(port=0)
                self._save_credentials(creds, self.GOOGLE_DRIVE_TOKEN_FILE)
                self._google_drive_creds = creds
                return True
            
            return False
            
        except Exception as e:
            print(f"認證 {token_type} 失敗: {str(e)}")
            return False
    
    def get_youtube_credentials(self) -> Optional[Credentials]:
        """
        取得 YouTube 憑證（自動處理過期刷新）
        
        Returns:
            Credentials: YouTube 憑證，如果無效則返回 None
        """
        if self._youtube_creds and self._youtube_creds.valid:
            return self._youtube_creds
        
        creds = self._load_credentials(
            self.YOUTUBE_TOKEN_FILE,
            self.YOUTUBE_SCOPES
        )
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self._save_credentials(creds, self.YOUTUBE_TOKEN_FILE)
                    self._youtube_creds = creds
                    return creds
                except Exception as e:
                    print(f"自動刷新 YouTube token 失敗: {str(e)}")
                    return None
            return None
        
        self._youtube_creds = creds
        return creds
    
    def get_google_drive_credentials(self) -> Optional[Credentials]:
        """
        取得 Google Drive 憑證（自動處理過期刷新）
        
        Returns:
            Credentials: Google Drive 憑證，如果無效則返回 None
        """
        if self._google_drive_creds and self._google_drive_creds.valid:
            return self._google_drive_creds
        
        creds = self._load_credentials(
            self.GOOGLE_DRIVE_TOKEN_FILE,
            self.GOOGLE_DRIVE_SCOPES
        )
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self._save_credentials(creds, self.GOOGLE_DRIVE_TOKEN_FILE)
                    self._google_drive_creds = creds
                    return creds
                except Exception as e:
                    print(f"自動刷新 Google Drive token 失敗: {str(e)}")
                    return None
            return None
        
        self._google_drive_creds = creds
        return creds
    
    def _load_credentials(self, token_file: str, scopes: list) -> Optional[Credentials]:
        """
        從檔案載入憑證
        
        Args:
            token_file: Token 檔案路徑
            scopes: OAuth scopes
            
        Returns:
            Credentials: 憑證物件，如果不存在則返回 None
        """
        if not os.path.exists(token_file):
            return None
        
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                return creds
        except Exception as e:
            print(f"載入 {token_file} 失敗: {str(e)}")
            return None
    
    def _save_credentials(self, creds: Credentials, token_file: str):
        """
        儲存憑證到檔案
        
        Args:
            creds: 憑證物件
            token_file: Token 檔案路徑
        """
        try:
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            print(f"儲存 {token_file} 失敗: {str(e)}")


if __name__ == '__main__':
    # 測試用程式碼
    manager = TokenManager()
    statuses = manager.check_all_tokens()
    
    print("=== Token 狀態檢查 ===")
    for name, status in statuses.items():
        print(f"\n{name}:")
        print(f"  {status.status_text}")
        if status.error_message:
            print(f"  錯誤: {status.error_message}")
