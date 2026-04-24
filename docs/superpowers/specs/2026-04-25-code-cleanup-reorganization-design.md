# 程式碼整理與資料夾重組設計文件

**日期**：2026-04-25  
**狀態**：已核准

---

## 目標

移除無用的測試腳本與程式碼片段，並將根目錄的零散檔案依職責歸入對應資料夾，讓專案結構更清晰易維護。

---

## 最終目錄結構

```
YoutubeUpload/
├── main.py                        # 主程式入口
├── token_manager.py               # Token 統一管理
├── video_item.py                  # 影片資料模型
├── requirements.txt
├── assets/                        # 靜態資源
│   ├── icon.ico
│   ├── icon.jpg
│   └── demo.PNG
├── scripts/                       # 打包設定
│   └── YoutubeUploader.spec
├── dialogs/                       # PyQt5 對話框（不變）
│   ├── __init__.py
│   ├── token_status_dialog.py
│   └── video_editor_dialog.py
├── uploaders/                     # 平台上傳器（不變）
│   ├── __init__.py
│   ├── base_uploader.py
│   ├── youtube_uploader.py
│   └── bilibili_uploader.py
└── services/                      # 外部服務整合（新建）
    ├── __init__.py
    └── google_drive.py            # 原 UploadGoogleDrive.py
```

---

## 刪除清單

| 檔案 | 理由 |
|------|------|
| `ReadGoogleDrive.py` | 一次性工具腳本，無任何模組 import 它 |
| `test_batch_upload.py` | 非正式測試，只是啟動主視窗的捷徑 |
| `test_token_dialog.py` | 非正式測試，只是啟動對話框的捷徑 |
| `nuitka-crash-report.xml` | 建置產生的 crash log，不需納入版控 |
| `token_manager.py` 底部 `if __name__ == '__main__':` 區塊 | 非正式測試代碼 |
| `video_item.py` 底部 `if __name__ == '__main__':` 區塊 | 非正式測試代碼 |
| `bilibili_uploader.py` 底部 `if __name__ == '__main__':` 區塊 | 非正式測試代碼（B 站本體保留） |

---

## 移動清單

| 原路徑 | 新路徑 | 說明 |
|--------|--------|------|
| `UploadGoogleDrive.py` | `services/google_drive.py` | 改名，語意更清楚 |
| `YoutubeUploader.spec` | `scripts/YoutubeUploader.spec` | 打包設定集中管理 |
| `icon.ico` | `assets/icon.ico` | 靜態資源集中管理 |
| `icon.jpg` | `assets/icon.jpg` | 靜態資源集中管理 |
| `demo.PNG` | `assets/demo.PNG` | 靜態資源集中管理 |

---

## 需同步更新的程式碼

### `main.py`
```python
# 變更前
self.setWindowIcon(QtGui.QIcon('icon.jpg'))

# 變更後
self.setWindowIcon(QtGui.QIcon('assets/icon.jpg'))
```

### `scripts/YoutubeUploader.spec`
```python
# 變更前
icon=['icon.jpg']

# 變更後
icon=['assets/icon.jpg']
```

### `uploaders/youtube_uploader.py`
```python
# 變更前
import UploadGoogleDrive

# 變更後
from services import google_drive
```
並將所有 `UploadGoogleDrive.upload_replay(...)` 呼叫改為 `google_drive.upload_replay(...)`。

---

## 新建檔案

### `services/__init__.py`
空白或只 expose `google_drive` 模組。

---

## 不在本次範圍內

- B 站上傳器功能實作（保留現有 placeholder）
- 正式單元測試（之後另行補上）
- 核心業務邏輯修改

---

## 風險評估

| 風險 | 影響 | 緩解方式 |
|------|------|---------|
| `assets/` 路徑在打包（Nuitka/PyInstaller）時找不到 | 中 | 確認 spec 和 Nuitka 設定同步更新 |
| `google_drive` import 路徑更新遺漏 | 低 | 全文搜尋 `UploadGoogleDrive` 確認無殘留 |
| PyInstaller spec 移到 `scripts/` 後需指定路徑打包 | 低 | README 補充打包指令：`pyinstaller scripts/YoutubeUploader.spec` |
