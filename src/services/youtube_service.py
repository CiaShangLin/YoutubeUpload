from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httplib2
from oauth2client import client, tools, file

class YouTubeService:
    def __init__(self):
        self.MAX_RETRIES = 10
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        
    def get_authenticated_service(self, token_path, scope):
        """
        获取已认证的YouTube服务
        """
        credential_path = token_path
        store = file.Storage(credential_path)
        credentials = store.get()
        
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(token_path, scope)
            credentials = tools.run_flow(flow, store)
            
        return build('youtube', 'v3', credentials=credentials) 