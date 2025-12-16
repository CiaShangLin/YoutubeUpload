# YouTube 上傳器專案 - Claude AI 規則

## 專案概述

這是一個基於 PyQt5 的 YouTube 影片批次上傳工具，專門為星海爭霸 2 (StarCraft II) 遊戲影片設計。

### 核心功能
- 批次上傳多部影片到 YouTube
- 自動上傳 Replay 檔案到 Google Drive
- 多國語言支援（英文、繁中、日文、韓文）
- OAuth Token 管理和過期檢查
- 預留 B站上傳介面

---

## 程式碼風格規範

### Python 規範
- **版本**：Python 3.8+
- **風格指南**：遵循 PEP 8
- **Type Hints**：所有公開函數必須使用型別提示
- **文檔字串**：使用中文撰寫，採用 Google Style

```python
def check_token_status(self, token_type: str) -> bool:
    """
    檢查指定類型的 Token 狀態
    
    Args:
        token_type: Token 類型，'youtube' 或 'google_drive'
        
    Returns:
        bool: Token 是否有效
    """
    pass
```

### 命名慣例
- **類別**：`PascalCase` (例如：`TokenManager`, `VideoItem`)
- **函數/方法**：`snake_case` (例如：`check_token_status`, `upload_video`)
- **常數**：`UPPER_SNAKE_CASE` (例如：`YOUTUBE_SCOPES`, `MAX_RETRIES`)
- **私有方法**：`_snake_case` (例如：`_load_credentials`, `_save_token`)
- **UI 元件**：
  - 按鈕：`bt` 前綴 (例如：`btUpload`, `btCheckToken`)
  - 標籤：`tv` 或 `label` 前綴 (例如：`tvFilePath`, `labelGame`)
  - 核取方塊：`ckb` 前綴 (例如：`ckbPVP`, `ckbTW`)

---

## 專案結構規範

### 目錄組織
```
YoutubeUpload/
├── main.py                    # 主程式入口
├── token_manager.py           # Token 統一管理
├── video_item.py              # 影片資料模型
├── upload_manager.py          # 批次上傳管理
├── UploadGoogleDrive.py       # Google Drive 上傳
├── UploadArgs.py              # 上傳參數類別
├── dialogs/                   # 對話框模組
│   ├── __init__.py
│   ├── token_status_dialog.py
│   └── video_editor_dialog.py
├── uploaders/                 # 上傳器模組
│   ├── __init__.py
│   ├── base_uploader.py
│   ├── youtube_uploader.py
│   └── bilibili_uploader.py
└── tests/                     # 測試腳本
```

### 模組職責
- **dialogs/**：所有 PyQt5 對話框元件
- **uploaders/**：平台上傳器實作（YouTube、B站等）
- **根目錄**：核心邏輯和工具類別

---

## 開發規則

### 1. Token 管理
- ✅ **必須**：所有 Token 操作透過 `TokenManager` 統一管理
- ❌ **禁止**：直接讀寫 token 檔案
- ✅ **建議**：使用 `get_youtube_credentials()` 自動處理過期刷新

```python
# ✅ 正確做法
creds = self.token_manager.get_youtube_credentials()

# ❌ 錯誤做法
with open('youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)
```

### 2. UI 開發
- **框架**：使用 PyQt5
- **佈局**：優先使用 Layout 而非絕對定位（新元件）
- **國際化**：UI 文字使用繁體中文
- **圖示**：使用 Emoji 或 Unicode 符號（例如：🔐、✅、❌）

### 3. 錯誤處理
- 所有外部 API 呼叫必須有 try-except
- 使用者操作錯誤應顯示友善的 QMessageBox
- 記錄詳細錯誤訊息到 console

```python
try:
    success = self.token_manager.refresh_token(token_type)
    if success:
        QtWidgets.QMessageBox.information(self, "成功", "Token 刷新成功！")
except Exception as e:
    QtWidgets.QMessageBox.critical(self, "錯誤", f"刷新失敗：{str(e)}")
    print(f"詳細錯誤: {e}")
```

### 4. 擴展性設計
- 使用抽象基類（ABC）設計介面
- 預留 B站上傳功能（`BilibiliUploader`）
- 新增平台時繼承 `BaseUploader`

```python
class BaseUploader(ABC):
    @abstractmethod
    def upload(self, video: VideoItem) -> str:
        """上傳影片，返回影片 ID"""
        pass
```

---

## 測試規範

### 測試檔案命名
- 測試腳本：`test_*.py` (例如：`test_token_dialog.py`)
- 放置位置：專案根目錄或 `tests/` 目錄

### 測試內容
- 每個新功能需要提供獨立測試腳本
- GUI 元件提供 `if __name__ == '__main__'` 測試區塊

```python
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = TokenStatusDialog(TokenManager())
    dialog.exec_()
    sys.exit(0)
```

---

## Git 提交規範

### Commit Message 格式
```
<type>: <subject>

<body>
```

### Type 類型
- `feat`: 新功能
- `fix`: 修復 Bug
- `refactor`: 重構
- `docs`: 文檔更新
- `test`: 測試相關
- `chore`: 雜項（依賴更新等）

### 範例
```
feat: 加入 Token 過期檢查對話框

- 新增 TokenStatusDialog 類別
- 整合到主視窗右上角按鈕
- 支援自動刷新和重新認證
```

---

## 依賴管理

### 核心依賴
```
PyQt5>=5.15.0                    # GUI 框架
google-api-python-client>=2.0.0  # YouTube API
google-auth>=2.0.0               # 新版認證庫
google-auth-oauthlib>=0.5.0      # OAuth 流程
google-auth-httplib2>=0.1.0      # HTTP 傳輸
httplib2>=0.20.0                 # HTTP 客戶端
oauth2client>=4.1.3              # 舊版相容（逐步淘汰）
```

### 新增依賴
- 更新 `requirements.txt`
- 在 commit message 中說明原因

---

## 特殊注意事項

### 1. 相容性維護
- 保留 `UploadArgs.py` 以維持向後相容
- 舊版 token 檔案（`login_token.json`, `upload_token.json`）逐步遷移

### 2. 預設值設定
- 遊戲名稱：`StarCraft II`
- 發布時間：當天 18:00
- 播放清單：預設勾選「SC2天梯」
- 字幕語言：預設勾選「英文」和「中文（台灣）」

### 3. 檔案名稱解析
- 自動從檔案名稱解析對戰種族（Protoss/Zerg/Terran）
- 自動勾選對應的播放清單（PVP/PVZ/PVT）

### 4. 多語言處理
```python
eng_to_tw = {"Protoss": "神族", "Zerg": "蟲族", "Terran": "人族"}
eng_to_ja = {"Protoss": "プロトス", "Zerg": "ザーグ", "Terran": "テラン"}
eng_to_kr = {"Protoss": "프로토스", "Zerg": "저그", "Terran": "테란"}
```

---

## 開發流程

### Phase 實作順序
1. ✅ **Phase 1**: Token 管理器 + 過期檢查 UI
2. ⏳ **Phase 2**: 影片資料模型 + 批次列表 UI
3. ⏳ **Phase 3**: 重構上傳邏輯為 YouTubeUploader
4. ⏳ **Phase 4**: 批次上傳管理器
5. ⏳ **Phase 5**: 預留 B站介面

### 每個 Phase 完成後
1. 創建測試腳本驗證功能
2. 撰寫 `PHASE_X_REPORT.md` 文檔
3. 更新 `implementation_plan.md`
4. 提交 Git commit

---

## 常見問題

### Q: Token 每週過期怎麼辦？
A: 檢查 Google Cloud Console 的 OAuth 同意畫面，將發布狀態從「測試」改為「正式版」。

### Q: 如何新增其他平台上傳？
A: 繼承 `BaseUploader` 並實作 `upload()`, `set_thumbnail()`, `add_to_playlist()` 方法。

### Q: UI 元件位置如何調整？
A: 目前使用絕對定位 `setGeometry()`，新元件建議改用 Layout 系統。

---

## 參考資源

- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Google Drive API](https://developers.google.com/drive/api/v3/about-sdk)
- [PyQt5 文檔](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [PEP 8 風格指南](https://peps.python.org/pep-0008/)

---

> **最後更新**: 2025-12-16  
> **當前版本**: Phase 1 已完成  
> **維護者**: Cia Shang Lin
