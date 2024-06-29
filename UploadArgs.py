# 上傳用參數,原本用argparser但是這個適合給cmd用,用在GUI他不能重複設置
class UploadArgs:
    def __init__(self, file=None, title=None, thumbnail=None, description=None,
                 category_id=None, keywords=None, privacy_status=None):
        self.file = file
        self.title = title
        self.thumbnail = thumbnail
        self.description = description
        self.category_id = category_id
        self.keywords = keywords
        self.privacy_status = privacy_status
