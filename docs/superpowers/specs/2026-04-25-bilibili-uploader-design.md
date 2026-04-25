# B站上傳器設計文件

**日期**：2026-04-25  
**狀態**：待實作  
**範圍**：實作 `BilibiliUploader`，整合到現有 YouTube 上傳工具

---

## 目標

為現有的 StarCraft II 影片批次上傳工具新增 B站投稿功能，讓使用者在上傳 YouTube 的同時，可勾選同步投稿到 B站。

---

## 核心限制與決策

| 項目 | 決策 | 原因 |
|------|------|------|
| 上傳函式庫 | `biliup` (`biliup.plugins.bili_webup`) | 專為 B站投稿設計，處理分片上傳與重試 |
| 認證方式 | 手動 Cookie JSON | 使用者已有現成 Cookie，無需實作登入流程 |
| 版權設定 | 原創（`copyright=1`）| 自己打的天梯局 |
| 合集功能 | 暫不實作 | 留待後續需求 |
| 上傳觸發 | YouTube 上傳成功後才觸發 | 避免孤立的 B站 影片 |
| B站 預設發布時間 | YouTube 發布時間 + 1 小時 | B站 時區展示與 YouTube 有一小時落差 |

---

## 架構概覽

```
VideoEditorDialog
  └─ 勾選「同步上傳到 B站」
  └─ 設定 B站 發布時間（預設 = YouTube時間 + 1h）
  └─ 寫入 VideoItem.upload_to_bilibili / bilibili_publish_time

UploadManager
  └─ YouTubeUploader.upload() 成功
  └─ VideoItem.upload_to_bilibili == True
      └─ BilibiliUploader.upload(video)
          └─ 讀取 bilibili_cookie.json（透過 TokenManager）
          └─ 上傳影片分片
          └─ 上傳封面圖
          └─ 送出投稿（含 dtime）

TokenStatusDialog
  └─ 顯示 B站 Cookie 狀態
  └─ 提供「設定 Cookie」入口
```

---

## 1. 資料模型（`video_item.py`）

在 `VideoItem` dataclass 新增三個欄位：

```python
# B站 專屬欄位
upload_to_bilibili: bool = False
bilibili_publish_time: Optional[datetime] = None
bilibili_video_id: Optional[str] = None
```

### 發布時間換算（`dtime`）

```python
from datetime import datetime, timedelta

def get_bilibili_dtime(bilibili_publish_time: datetime) -> int:
    """將 B站 發布時間轉換為從現在起算的秒數"""
    delta = bilibili_publish_time - datetime.now()
    seconds = int(delta.total_seconds())
    return max(0, seconds)  # 已過時間 → 立即發布
```

### `to_dict()` / `from_dict()` 更新

新增欄位需同步更新序列化方法，確保儲存/讀取正確。

---

## 2. 認證管理（`token_manager.py`）

### Cookie 檔案格式

`bilibili_cookie.json`（放在專案根目錄）：

```json
{
    "SESSDATA": "your_sessdata",
    "bili_jct": "your_bili_jct",
    "DedeUserID": "your_uid",
    "DedeUserID__ckMd5": "your_ckmd5"
}
```

### 新增方法

```python
def get_bilibili_cookies(self) -> Optional[dict]:
    """讀取 bilibili_cookie.json，不存在回傳 None"""

def is_bilibili_logged_in(self) -> bool:
    """bilibili_cookie.json 存在且包含必要欄位"""
```

必要欄位：`SESSDATA`, `bili_jct`, `DedeUserID`, `DedeUserID__ckMd5`

---

## 3. `BilibiliUploader`（`uploaders/bilibili_uploader.py`）

### 固定常數（SC2 專用）

```python
BILIBILI_TID = 171          # 電子競技分區
BILIBILI_COPYRIGHT = 1      # 原創
BILIBILI_TAGS = [
    "StarCraft2", "星海爭霸2", "SC2",
    "天梯", "Protoss", "神族", "Ladder"
]
```

### `upload()` 流程

```
1. validate_video(video)
2. TokenManager.get_bilibili_cookies() → cookies
3. 建立 Data 物件，填入 title / desc / tid / tags / copyright
4. 計算 dtime（若 bilibili_publish_time 有值）
5. BiliBili(video).login(cookies)
6. bili.upload_file(video.video_path) → video_part
7. video.append(video_part)
8. bili.cover_up(thumbnail_path) → cover URL（若有封面）
9. bili.submit() → 回傳 bvid
```

### 方法簽名

```python
class BilibiliUploader(BaseUploader):
    def __init__(self, token_manager: TokenManager): ...
    def upload(self, video: VideoItem) -> str: ...          # 回傳 bvid
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool: ...
    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        raise NotImplementedError("合集功能尚未實作")
```

`set_thumbnail()` 在 `upload()` 內部處理（biliup 在 submit 前上傳封面），此方法保留供外部呼叫但實際可為空操作。

### 錯誤處理

- Cookie 不存在 → 拋出 `ValueError("請先設定 B站 Cookie")`
- 上傳失敗 → 拋出 `Exception`，由 `UploadManager` 捕捉並顯示 `QMessageBox`

---

## 4. UI 整合

### `dialogs/video_editor_dialog.py`

在 YouTube 設定區塊下方新增 B站 區塊：

```
─── B站 投稿 ─────────────────────────────
☐ 同步上傳到 B站

B站發布時間: [2026-04-25  19:00]   ← 僅打勾時顯示
```

**互動行為**：
- 勾選時：顯示 B站 發布時間，預設值 = `youtube_publish_time + timedelta(hours=1)`
- 取消勾選：隱藏 B站 發布時間
- 儲存時：寫入 `video.upload_to_bilibili` 與 `video.bilibili_publish_time`

**UI 元件命名**（遵循專案慣例）：
- `ckbBilibili` — 「同步上傳到 B站」勾選框
- `dtBilibiliPublish` — B站 發布時間選擇器（`QDateTimeEdit`）

### `dialogs/token_status_dialog.py`

在現有 YouTube / Google Drive 狀態列下方新增第三行：

```
B站 Cookie：✅ 已設定  [重新設定]
           ❌ 未設定  [設定 Cookie]
```

「設定 Cookie」按鈕開啟文字輸入對話框，讓使用者貼上 JSON 內容，自動儲存到 `bilibili_cookie.json`。

### `upload_manager.py`

```python
# YouTube 上傳成功後
if video.upload_to_bilibili:
    try:
        bilibili_uploader = BilibiliUploader(self.token_manager)
        bvid = bilibili_uploader.upload(video)
        video.bilibili_video_id = bvid
        print(f"✅ B站投稿成功: {bvid}")
    except Exception as e:
        QMessageBox.warning(None, "B站上傳失敗", str(e))
        # YouTube 已成功，不中斷整體流程
```

---

## 5. 新增依賴

`requirements.txt` 新增：

```
biliup>=0.4.0
```

---

## 6. 不在此次範圍內

- B站 合集（Series）管理
- B站 登入自動化（掃碼/密碼）
- B站 上傳進度顯示
- B站 影片管理（刪除、編輯）
- YouTube 失敗後的 B站 獨立上傳

---

## 檔案異動清單

| 檔案 | 異動類型 |
|------|---------|
| `video_item.py` | 修改：新增 3 個 B站 欄位 |
| `token_manager.py` | 修改：新增 2 個 Cookie 方法 |
| `uploaders/bilibili_uploader.py` | 改寫：實作完整上傳邏輯 |
| `dialogs/video_editor_dialog.py` | 修改：新增 B站 勾選框與時間選擇器 |
| `dialogs/token_status_dialog.py` | 修改：新增 B站 Cookie 狀態顯示 |
| `upload_manager.py` | 修改：串接 B站 上傳流程 |
| `requirements.txt` | 修改：新增 `biliup` |
