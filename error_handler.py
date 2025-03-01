class YouTubeUploadError(Exception):
    """YouTube上傳過程中的錯誤基類"""
    pass

class AuthenticationError(YouTubeUploadError):
    """認證錯誤"""
    pass

class UploadError(YouTubeUploadError):
    """上傳錯誤"""
    pass

def handle_error(error, retry_function=None, max_retries=3):
    """統一的錯誤處理函數"""
    if isinstance(error, HttpError):
        if error.resp.status in [500, 502, 503, 504]:
            # 可重試的HTTP錯誤
            if retry_function and max_retries > 0:
                time.sleep(2)
                return retry_function(max_retries-1)
        # 其他HTTP錯誤
        raise UploadError(f"HTTP錯誤 {error.resp.status}: {error.content}")
    else:
        # 其他錯誤
        raise YouTubeUploadError(f"上傳過程中發生錯誤: {str(error)}") 