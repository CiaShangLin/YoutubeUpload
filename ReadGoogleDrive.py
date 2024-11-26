import os

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# 讀取Google Drive 檔案資料夾ID
# 使用更廣泛的授權範圍
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]

def authenticate():
    # 使用您下載的 credentials.json 路徑
    flow = InstalledAppFlow.from_client_secrets_file(
        'token.json',  # 確保路徑正確
        SCOPES
    )

    # 啟動授權流程
    credentials = flow.run_local_server(port=0)
    return credentials

def list_folders():
    # 獲取憑證
    credentials = authenticate()

    # 建立 Drive 服務
    service = build('drive', 'v3', credentials=credentials)

    # 搜尋所有資料夾的改進查詢
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder'",
        pageSize=100,  # 增加可列出的資料夾數量
        spaces='drive',
        fields="files(id, name, createdTime, webViewLink, parents)"
    ).execute()

    folders = results.get('files', [])

    if not folders:
        print('未找到任何資料夾.')
    else:
        print(f'找到 {len(folders)} 個資料夾:')
        for folder in folders:
            print(f"資料夾名稱: {folder['name']}")
            print(f"資料夾ID: {folder['id']}")
            print(f"建立時間: {folder.get('createdTime', '未知')}")
            print(f"父資料夾: {folder.get('parents', ['無'])}")
            print(f"連結: {folder.get('webViewLink', '無')}")
            print('-' * 40)


if __name__ == '__main__':
    # 列出所有資料夾
    list_folders()
