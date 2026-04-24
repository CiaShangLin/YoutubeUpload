# 程式碼整理與資料夾重組 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 移除無用腳本與測試區塊，將根目錄零散檔案整理進 `services/`、`assets/`、`scripts/` 三個資料夾，並同步更新所有 import 與路徑引用。

**Architecture:** 純整理性重構，不修改任何業務邏輯。移動檔案後同步更新引用它們的 import 路徑與字串路徑，最後以全文搜尋驗證無殘留舊名稱。

**Tech Stack:** Python 3.8+, PyQt5, git

---

## 受影響檔案總覽

| 動作 | 檔案 |
|------|------|
| 刪除 | `ReadGoogleDrive.py`, `test_batch_upload.py`, `test_token_dialog.py`, `nuitka-crash-report.xml` |
| 修改（移除 `__main__` 區塊） | `token_manager.py`, `video_item.py`, `uploaders/bilibili_uploader.py`, `uploaders/youtube_uploader.py`, `uploaders/base_uploader.py` |
| 建立 | `services/__init__.py` |
| 移動+改名 | `UploadGoogleDrive.py` → `services/google_drive.py` |
| 移動 | `icon.ico`, `icon.jpg`, `demo.PNG` → `assets/` |
| 移動 | `YoutubeUploader.spec` → `scripts/` |
| 更新引用 | `uploaders/youtube_uploader.py`, `main.py`, `scripts/YoutubeUploader.spec`, `README.md` |

---

## Task 1：刪除無用檔案

**Files:**
- Delete: `ReadGoogleDrive.py`
- Delete: `test_batch_upload.py`
- Delete: `test_token_dialog.py`
- Delete: `nuitka-crash-report.xml`

- [ ] **Step 1: 刪除四個無用檔案**

```bash
git rm ReadGoogleDrive.py test_batch_upload.py test_token_dialog.py nuitka-crash-report.xml
```

Expected output: 4 files deleted

- [ ] **Step 2: 確認根目錄已無這四個檔案**

```bash
ls *.py *.xml 2>/dev/null
```

Expected: 只剩 `main.py`, `token_manager.py`, `video_item.py`，無 `ReadGoogleDrive.py`、`test_*.py`、`*.xml`

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: 刪除無用工具腳本和測試腳本"
```

---

## Task 2：移除 `__main__` 測試區塊

**Files:**
- Modify: `token_manager.py` (移除末尾 `if __name__ == '__main__':` 區塊，約第 312–322 行)
- Modify: `video_item.py` (移除末尾 `if __name__ == '__main__':` 區塊，約第 236–267 行)
- Modify: `uploaders/bilibili_uploader.py` (移除末尾 `if __name__ == '__main__':` 區塊，約第 66–68 行)
- Modify: `uploaders/youtube_uploader.py` (移除末尾 `if __name__ == '__main__':` 區塊，約第 387–389 行)
- Modify: `uploaders/base_uploader.py` (移除末尾 `if __name__ == '__main__':` 區塊，約第 75–77 行)

- [ ] **Step 1: 移除 `token_manager.py` 末尾測試區塊**

將以下內容從 `token_manager.py` 末尾刪除（從 `if __name__ == '__main__':` 開始到檔案結尾）：

```python
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
```

刪除後，`token_manager.py` 最後一行應為 `_save_credentials` 方法的最後一行（`print(f"儲存 {token_file} 失敗: {str(e)}")`）。

- [ ] **Step 2: 移除 `video_item.py` 末尾測試區塊**

將以下內容從 `video_item.py` 末尾刪除（從 `if __name__ == '__main__':` 開始到檔案結尾）：

```python
if __name__ == '__main__':
    # 測試用程式碼
    import json
    
    # 創建測試影片
    video = VideoItem(
        video_path="/path/to/video.mp4",
        title="【StarCraft II】Nzs (Protoss) vs Opponent (Zerg) - KR Server",
        thumbnail_path="/path/to/thumbnail.jpg",
        replay_path="/path/to/replay.SC2Replay",
        match_type=MatchType.PVZ,
        playlist_ids=["playlist1", "playlist2"]
    )
    
    print("=== VideoItem 測試 ===")
    print(f"標題: {video.title}")
    print(f"對戰類型: {video.match_type_text}")
    print(f"發布時間: {video.publish_time_str}")
    print(f"狀態: {video.status_text}")
    print(f"有縮圖: {video.has_thumbnail}")
    print(f"有 Replay: {video.has_replay}")
    
    # 測試序列化
    print("\n=== 序列化測試 ===")
    data = video.to_dict()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 測試反序列化
    print("\n=== 反序列化測試 ===")
    video2 = VideoItem.from_dict(data)
    print(f"標題: {video2.title}")
    print(f"對戰類型: {video2.match_type_text}")
```

- [ ] **Step 3: 移除 `uploaders/bilibili_uploader.py` 末尾測試區塊**

將以下內容從 `uploaders/bilibili_uploader.py` 末尾刪除：

```python
if __name__ == '__main__':
    print("BilibiliUploader 是預留介面，尚未實作")
    print("未來可以在這裡實作 B站上傳功能")
```

- [ ] **Step 4: 移除 `uploaders/youtube_uploader.py` 末尾測試區塊**

將以下內容從 `uploaders/youtube_uploader.py` 末尾刪除：

```python
if __name__ == '__main__':
    print("YouTubeUploader 需要配合 TokenManager 使用")
    print("請參考 main.py 中的使用範例")
```

- [ ] **Step 5: 移除 `uploaders/base_uploader.py` 末尾測試區塊**

將以下內容從 `uploaders/base_uploader.py` 末尾刪除：

```python
if __name__ == '__main__':
    print("BaseUploader 是抽象基類，不能直接實例化")
    print("請使用 YouTubeUploader 或 BilibiliUploader")
```

- [ ] **Step 6: 確認無殘留 `__main__` 區塊**

```bash
grep -rn "if __name__" --include="*.py" .
```

Expected: 只剩 `main.py` 最底部的 `if __name__ == "__main__":` 主程式入口，其餘全部清除。

- [ ] **Step 7: Commit**

```bash
git add token_manager.py video_item.py uploaders/bilibili_uploader.py uploaders/youtube_uploader.py uploaders/base_uploader.py
git commit -m "chore: 移除各模組底部的非正式測試區塊"
```

---

## Task 3：建立 `services/` 並移入 Google Drive 模組

**Files:**
- Create: `services/__init__.py`
- Create: `services/google_drive.py` (內容來自 `UploadGoogleDrive.py`)
- Delete: `UploadGoogleDrive.py`

- [ ] **Step 1: 建立 `services/` 資料夾與 `__init__.py`**

```bash
mkdir services
```

建立 `services/__init__.py`，內容：

```python
from . import google_drive

__all__ = ["google_drive"]
```

- [ ] **Step 2: 以 git mv 移動並改名**

```bash
git mv UploadGoogleDrive.py services/google_drive.py
```

- [ ] **Step 3: 確認移動結果**

```bash
ls services/
```

Expected: `__init__.py  google_drive.py`

- [ ] **Step 4: Commit**

```bash
git add services/__init__.py
git commit -m "refactor: 將 UploadGoogleDrive.py 移至 services/google_drive.py"
```

---

## Task 4：更新 `uploaders/youtube_uploader.py` 的 import

**Files:**
- Modify: `uploaders/youtube_uploader.py` (第 17 行 import、第 68 行呼叫)

- [ ] **Step 1: 更新 import 行**

將 `uploaders/youtube_uploader.py` 第 17 行：

```python
import UploadGoogleDrive
```

改為：

```python
from services import google_drive
```

- [ ] **Step 2: 更新 upload_replay 呼叫**

將 `uploaders/youtube_uploader.py` 第 68 行：

```python
replay_url = UploadGoogleDrive.upload_replay(video.replay_path)
```

改為：

```python
replay_url = google_drive.upload_replay(video.replay_path)
```

- [ ] **Step 3: 確認無殘留舊 import**

```bash
grep -n "UploadGoogleDrive" uploaders/youtube_uploader.py
```

Expected: 無輸出

- [ ] **Step 4: Commit**

```bash
git add uploaders/youtube_uploader.py
git commit -m "refactor: 更新 youtube_uploader 改用 services.google_drive"
```

---

## Task 5：建立 `assets/` 並移入靜態資源

**Files:**
- Move: `icon.ico` → `assets/icon.ico`
- Move: `icon.jpg` → `assets/icon.jpg`
- Move: `demo.PNG` → `assets/demo.PNG`

- [ ] **Step 1: 建立 `assets/` 資料夾並移動三個檔案**

```bash
mkdir assets
git mv icon.ico assets/icon.ico
git mv icon.jpg assets/icon.jpg
git mv demo.PNG assets/demo.PNG
```

- [ ] **Step 2: 確認移動結果**

```bash
ls assets/
```

Expected: `demo.PNG  icon.ico  icon.jpg`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor: 將靜態資源移至 assets/ 資料夾"
```

---

## Task 6：更新 `main.py` 圖示路徑

**Files:**
- Modify: `main.py` (第 28 行)

- [ ] **Step 1: 更新圖示路徑**

將 `main.py` 第 28 行：

```python
self.setWindowIcon(QtGui.QIcon('icon.jpg'))
```

改為：

```python
self.setWindowIcon(QtGui.QIcon('assets/icon.jpg'))
```

- [ ] **Step 2: 確認更新**

```bash
grep -n "icon" main.py
```

Expected: 顯示 `assets/icon.jpg`，無裸露的 `'icon.jpg'`

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "fix: 更新 main.py 圖示路徑至 assets/icon.jpg"
```

---

## Task 7：建立 `scripts/` 並移入打包設定

**Files:**
- Move: `YoutubeUploader.spec` → `scripts/YoutubeUploader.spec`

- [ ] **Step 1: 建立 `scripts/` 資料夾並移動 spec**

```bash
mkdir scripts
git mv YoutubeUploader.spec scripts/YoutubeUploader.spec
```

- [ ] **Step 2: 更新 spec 內的圖示路徑**

將 `scripts/YoutubeUploader.spec` 第 38 行：

```python
    icon=['icon.jpg'],
```

改為：

```python
    icon=['assets/icon.jpg'],
```

- [ ] **Step 3: 確認更新**

```bash
grep "icon" scripts/YoutubeUploader.spec
```

Expected: `icon=['assets/icon.jpg']`

- [ ] **Step 4: Commit**

```bash
git add scripts/YoutubeUploader.spec
git commit -m "refactor: 將 YoutubeUploader.spec 移至 scripts/ 並更新圖示路徑"
```

---

## Task 8：更新 `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 demo 圖片路徑**

將 `README.md` 第 5 行：

```markdown
![Demo](demo.PNG)
```

改為：

```markdown
![Demo](assets/demo.PNG)
```

- [ ] **Step 2: 更新目錄結構區段**

找到 README.md 中列出 `UploadGoogleDrive.py` 的目錄樹，將其更新為新結構（包含 `services/`、`assets/`、`scripts/`）。將原本的：

```
├── UploadGoogleDrive.py    # Google Drive 上傳
```

替換為：

```
├── assets/                 # 靜態資源 (icon, demo)
├── scripts/                # 打包設定
│   └── YoutubeUploader.spec
└── services/               # 外部服務整合
    └── google_drive.py     # Google Drive 上傳
```

- [ ] **Step 3: 更新打包指令**

找到 README.md 中的打包指令區段，將：

```bash
pyinstaller --onefile --windowed --icon=icon.jpg --name=YoutubeUploader main.py
```

改為：

```bash
pyinstaller scripts/YoutubeUploader.spec
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: 更新 README 反映新目錄結構與打包指令"
```

---

## Task 9：最終驗證

- [ ] **Step 1: 全文搜尋確認無殘留舊名稱**

```bash
grep -rn "UploadGoogleDrive" --include="*.py" --include="*.md" .
```

Expected: 無輸出（`docs/superpowers/` 下的設計文件除外，可忽略）

```bash
grep -rn "'icon\.jpg'\|'icon\.ico'" --include="*.py" .
```

Expected: 無輸出

```bash
grep -rn "demo\.PNG" --include="*.md" . | grep -v "docs/superpowers"
```

Expected: 只剩 `README.md` 且路徑已是 `assets/demo.PNG`

- [ ] **Step 2: 確認專案根目錄結構乾淨**

```bash
ls
```

Expected（相關檔案）：`assets/  dialogs/  docs/  main.py  requirements.txt  scripts/  services/  token_manager.py  uploaders/  venv/  video_item.py`

無：`ReadGoogleDrive.py`, `test_batch_upload.py`, `test_token_dialog.py`, `nuitka-crash-report.xml`, `UploadGoogleDrive.py`, `YoutubeUploader.spec`, `icon.jpg`, `icon.ico`, `demo.PNG`

- [ ] **Step 3: 啟動程式確認正常運行**

```bash
python main.py
```

Expected: PyQt5 視窗正常開啟，圖示顯示正常，無 ImportError 或 FileNotFoundError

- [ ] **Step 4: 最終 commit（若 Step 3 無問題）**

```bash
git log --oneline -8
```

確認所有 task 的 commit 都已記錄在案。
