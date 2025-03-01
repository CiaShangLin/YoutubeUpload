class UploadArgs:
    def __init__(self, file, title, thumbnail, description, category_id, keywords, privacy_status):
        self.file = file
        self.title = title
        self.thumbnail = thumbnail
        self.description = description
        self.category_id = category_id
        self.keywords = keywords
        self.privacy_status = privacy_status 