from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# 如果修改這些範圍，請刪除token.pickle檔案
SCOPES = ['https://www.googleapis.com/auth/drive.file']
google_drive_client_secret = 'google_drive_client_secret.json'
temp_token = 'google_drive_token.pickle'
replay_folder_id = '1qNBBlfLe17nEOE9aI5ePcs55DGsmgp0J'


def cut_string(input_string):
    index = input_string.find("【StarCraft II】")
    if index != -1:
        return input_string[index:]
    return input_string

def upload_replay(filePath):
    creds = None
    # token.pickle儲存使用者的存取權和重新整理權杖
    if os.path.exists(temp_token):
        with open(temp_token, 'rb') as token:
            creds = pickle.load(token)
    # 如果沒有可用的（有效的）憑證，讓使用者登入
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                google_drive_client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        # 儲存憑證以供下次執行使用
        with open(temp_token, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': cut_string(filePath), 'parents': [replay_folder_id]}
    media = MediaFileUpload(filePath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: %s' % file.get('id'))

    # 設定共享權限
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(fileId=file.get('id'), body=permission).execute()

    # 取得檔案URL
    file_id = file.get('id')
    file_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    print('File URL:', file_url)
    return file_url


if __name__ == '__main__':
    upload_replay('')
