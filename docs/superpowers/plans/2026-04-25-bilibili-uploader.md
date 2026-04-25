# B站上傳器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在現有 YouTube 上傳工具中新增 B站投稿功能，YouTube 上傳成功後可選擇性同步投稿到 B站。

**Architecture:** `BilibiliUploader` 繼承 `BaseUploader`，透過 `biliup` 函式庫處理分片上傳與封面上傳；`VideoItem` 擴充三個 B站 欄位；上傳邏輯整合在 `main.py` 的 `_execute_batch_upload()` 中，YouTube 成功後才觸發 B站 上傳。

**Tech Stack:** Python 3.8+, PyQt5, biliup>=0.4.0

---

## 檔案異動清單

| 檔案 | 類型 | 說明 |
|------|------|------|
| `requirements.txt` | 修改 | 新增 biliup |
| `video_item.py` | 修改 | 新增 3 個 B站 欄位 + `get_bilibili_dtime()` |
| `token_manager.py` | 修改 | 新增 `get_bilibili_cookies()`, `is_bilibili_logged_in()` |
| `uploaders/bilibili_uploader.py` | 改寫 | 完整上傳實作 |
| `dialogs/video_editor_dialog.py` | 修改 | 新增 B站 投稿區塊 |
| `dialogs/token_status_dialog.py` | 修改 | 新增 B站 Cookie 狀態列 |
| `main.py` | 修改 | `_execute_batch_upload()` 串接 B站 上傳 |
| `tests/test_bilibili_fields.py` | 新建 | 單元測試 |

---

## Task 1: 新增 biliup 依賴

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: 更新 requirements.txt**

```
PyQt5>=5.15.0
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0
httplib2>=0.20.0
oauth2client>=4.1.3
biliup>=0.4.0
```

- [ ] **Step 2: 安裝套件**

```bash
pip install biliup>=0.4.0
```

Expected: 安裝成功，`from biliup.plugins.bili_webup import BiliBili, Data` 可執行無報錯。

- [ ] **Step 3: 驗證匯入**

```bash
python -c "from biliup.plugins.bili_webup import BiliBili, Data; print('OK')"
```

Expected: 輸出 `OK`，無 ImportError。

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: 新增 biliup 依賴"
```

---

## Task 2: 擴充 VideoItem B站欄位

**Files:**
- Modify: `video_item.py`
- Create: `tests/test_bilibili_fields.py`

- [ ] **Step 1: 先寫失敗測試**

建立 `tests/test_bilibili_fields.py`：

```python
"""VideoItem B站欄位與 get_bilibili_dtime 的單元測試"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from video_item import VideoItem


def test_bilibili_defaults():
    """VideoItem 預設 B站 欄位應為 False/None"""
    v = VideoItem(video_path="a.mp4", title="Test")
    assert v.upload_to_bilibili == False
    assert v.bilibili_publish_time is None
    assert v.bilibili_video_id is None


def test_get_bilibili_dtime_future():
    """未來時間應回傳正整數秒數"""
    v = VideoItem(video_path="a.mp4", title="Test")
    future = datetime.now() + timedelta(hours=2)
    v.bilibili_publish_time = future
    dtime = v.get_bilibili_dtime()
    assert dtime > 7000  # 大約 7200 秒，容許 200 秒誤差
    assert dtime <= 7200


def test_get_bilibili_dtime_past():
    """過去時間應回傳 0（立即發布）"""
    v = VideoItem(video_path="a.mp4", title="Test")
    past = datetime.now() - timedelta(hours=1)
    v.bilibili_publish_time = past
    assert v.get_bilibili_dtime() == 0


def test_get_bilibili_dtime_none():
    """bilibili_publish_time 為 None 時回傳 0"""
    v = VideoItem(video_path="a.mp4", title="Test")
    assert v.get_bilibili_dtime() == 0


def test_to_dict_includes_bilibili_fields():
    """to_dict() 應包含 B站 欄位"""
    v = VideoItem(video_path="a.mp4", title="Test")
    v.upload_to_bilibili = True
    v.bilibili_publish_time = datetime(2026, 4, 25, 19, 0)
    v.bilibili_video_id = "BV1abc"
    d = v.to_dict()
    assert d['upload_to_bilibili'] == True
    assert d['bilibili_publish_time'] == "2026-04-25T19:00:00"
    assert d['bilibili_video_id'] == "BV1abc"


def test_from_dict_restores_bilibili_fields():
    """from_dict() 應正確還原 B站 欄位"""
    data = {
        'video_path': 'a.mp4',
        'title': 'Test',
        'upload_to_bilibili': True,
        'bilibili_publish_time': '2026-04-25T19:00:00',
        'bilibili_video_id': 'BV1abc',
    }
    v = VideoItem.from_dict(data)
    assert v.upload_to_bilibili == True
    assert v.bilibili_publish_time == datetime(2026, 4, 25, 19, 0)
    assert v.bilibili_video_id == "BV1abc"


if __name__ == '__main__':
    test_bilibili_defaults()
    test_get_bilibili_dtime_future()
    test_get_bilibili_dtime_past()
    test_get_bilibili_dtime_none()
    test_to_dict_includes_bilibili_fields()
    test_from_dict_restores_bilibili_fields()
    print("All tests passed!")
```

- [ ] **Step 2: 執行確認測試失敗**

```bash
python tests/test_bilibili_fields.py
```

Expected: `AttributeError: 'VideoItem' object has no attribute 'upload_to_bilibili'`

- [ ] **Step 3: 修改 video_item.py — 新增欄位與方法**

在 `VideoItem` dataclass 的 `replay_url` 欄位（第 68 行）之後，新增三個 B站 欄位：

```python
    # Replay 上傳後的 URL
    replay_url: Optional[str] = None
    
    # B站 專屬欄位
    upload_to_bilibili: bool = False
    bilibili_publish_time: Optional[datetime] = None
    bilibili_video_id: Optional[str] = None
```

在 `set_replay_url()` 方法之後，新增 `get_bilibili_dtime()` 方法：

```python
    def get_bilibili_dtime(self) -> int:
        """
        計算 B站 發布延遲秒數
        
        Returns:
            int: 從現在起算的秒數，0 表示立即發布
        """
        if self.bilibili_publish_time is None:
            return 0
        delta = self.bilibili_publish_time - datetime.now()
        return max(0, int(delta.total_seconds()))
```

- [ ] **Step 4: 修改 to_dict() — 新增 B站 欄位**

在 `to_dict()` 的 return dict 中，`replay_url` 之後加入：

```python
            'replay_url': self.replay_url,
            'upload_to_bilibili': self.upload_to_bilibili,
            'bilibili_publish_time': self.bilibili_publish_time.isoformat() if self.bilibili_publish_time else None,
            'bilibili_video_id': self.bilibili_video_id,
```

- [ ] **Step 5: 修改 from_dict() — 還原 B站 欄位**

在 `from_dict()` 的 `cls(...)` 呼叫中，`replay_url` 之後加入：

先在方法頂部的解析區段加入 bilibili_publish_time 解析（在 `publish_time` 解析區段之後）：

```python
        # 轉換 B站 發布時間
        bilibili_publish_time = None
        if data.get('bilibili_publish_time'):
            bilibili_publish_time = datetime.fromisoformat(data['bilibili_publish_time'])
```

然後在 `cls(...)` 的參數中新增：

```python
            replay_url=data.get('replay_url'),
            upload_to_bilibili=data.get('upload_to_bilibili', False),
            bilibili_publish_time=bilibili_publish_time,
            bilibili_video_id=data.get('bilibili_video_id'),
```

- [ ] **Step 6: 執行測試確認通過**

```bash
python tests/test_bilibili_fields.py
```

Expected: `All tests passed!`

- [ ] **Step 7: Commit**

```bash
git add video_item.py tests/test_bilibili_fields.py
git commit -m "feat: VideoItem 新增 B站 投稿欄位與 get_bilibili_dtime()"
```

---

## Task 3: 擴充 TokenManager — B站 Cookie 管理

**Files:**
- Modify: `token_manager.py`
- Modify: `tests/test_bilibili_fields.py`（新增 TokenManager 測試）

- [ ] **Step 1: 新增 TokenManager 測試到現有測試檔案**

在 `tests/test_bilibili_fields.py` 末尾加入：

```python
import json
import tempfile
from unittest.mock import patch
from token_manager import TokenManager


def test_is_bilibili_logged_in_missing_file():
    """Cookie 檔案不存在時回傳 False"""
    tm = TokenManager()
    with patch.object(tm, 'BILIBILI_COOKIE_FILE', '/nonexistent/path.json'):
        assert tm.is_bilibili_logged_in() == False


def test_is_bilibili_logged_in_valid():
    """Cookie 檔案存在且欄位完整時回傳 True"""
    tm = TokenManager()
    cookies = {
        'SESSDATA': 'abc',
        'bili_jct': 'def',
        'DedeUserID': '123',
        'DedeUserID__ckMd5': 'ghi'
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(cookies, f)
        tmp_path = f.name
    try:
        with patch.object(tm, 'BILIBILI_COOKIE_FILE', tmp_path):
            assert tm.is_bilibili_logged_in() == True
    finally:
        os.unlink(tmp_path)


def test_is_bilibili_logged_in_missing_field():
    """Cookie 缺少必要欄位時回傳 False"""
    tm = TokenManager()
    cookies = {'SESSDATA': 'abc'}  # 缺少其他欄位
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(cookies, f)
        tmp_path = f.name
    try:
        with patch.object(tm, 'BILIBILI_COOKIE_FILE', tmp_path):
            assert tm.is_bilibili_logged_in() == False
    finally:
        os.unlink(tmp_path)


def test_get_bilibili_cookies_returns_dict():
    """get_bilibili_cookies() 應回傳 Cookie dict"""
    tm = TokenManager()
    cookies = {
        'SESSDATA': 'abc',
        'bili_jct': 'def',
        'DedeUserID': '123',
        'DedeUserID__ckMd5': 'ghi'
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(cookies, f)
        tmp_path = f.name
    try:
        with patch.object(tm, 'BILIBILI_COOKIE_FILE', tmp_path):
            result = tm.get_bilibili_cookies()
        assert result == cookies
    finally:
        os.unlink(tmp_path)


def test_get_bilibili_cookies_missing_file():
    """檔案不存在時回傳 None"""
    tm = TokenManager()
    with patch.object(tm, 'BILIBILI_COOKIE_FILE', '/nonexistent/path.json'):
        assert tm.get_bilibili_cookies() is None
```

- [ ] **Step 2: 執行確認新增的測試失敗**

```bash
python tests/test_bilibili_fields.py
```

Expected: `AttributeError: type object 'TokenManager' has no attribute 'BILIBILI_COOKIE_FILE'`

- [ ] **Step 3: 修改 token_manager.py — 新增常數與方法**

在 `GOOGLE_DRIVE_TOKEN_FILE` 常數後加入：

```python
    BILIBILI_COOKIE_FILE = "bilibili_cookie.json"
    BILIBILI_REQUIRED_FIELDS = ["SESSDATA", "bili_jct", "DedeUserID", "DedeUserID__ckMd5"]
```

在 `get_google_drive_credentials()` 方法之後，`_load_credentials()` 之前加入：

```python
    def get_bilibili_cookies(self) -> Optional[dict]:
        """
        讀取 B站 Cookie 設定
        
        Returns:
            dict: Cookie 字典，檔案不存在時回傳 None
        """
        if not os.path.exists(self.BILIBILI_COOKIE_FILE):
            return None
        try:
            with open(self.BILIBILI_COOKIE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"讀取 {self.BILIBILI_COOKIE_FILE} 失敗: {str(e)}")
            return None

    def is_bilibili_logged_in(self) -> bool:
        """
        檢查 B站 Cookie 是否存在且包含必要欄位
        
        Returns:
            bool: Cookie 是否有效
        """
        cookies = self.get_bilibili_cookies()
        if not cookies:
            return False
        return all(field in cookies for field in self.BILIBILI_REQUIRED_FIELDS)

    def save_bilibili_cookies(self, cookies: dict) -> bool:
        """
        儲存 B站 Cookie 到檔案
        
        Args:
            cookies: Cookie 字典
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(self.BILIBILI_COOKIE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"儲存 {self.BILIBILI_COOKIE_FILE} 失敗: {str(e)}")
            return False
```

- [ ] **Step 4: 在 token_manager.py 頂部加入 json import**

確認 `import json` 已在第一行的 import 區段中（目前沒有，需新增）：

```python
import json
import os
import pickle
```

- [ ] **Step 5: 執行測試確認通過**

```bash
python tests/test_bilibili_fields.py
```

Expected: `All tests passed!`

- [ ] **Step 6: Commit**

```bash
git add token_manager.py tests/test_bilibili_fields.py
git commit -m "feat: TokenManager 新增 B站 Cookie 管理方法"
```

---

## Task 4: 實作 BilibiliUploader

**Files:**
- Rewrite: `uploaders/bilibili_uploader.py`

- [ ] **Step 1: 改寫 uploaders/bilibili_uploader.py**

完整取代現有內容：

```python
"""
B站上傳器
使用 biliup 函式庫實作 B站影片投稿
"""

import os
from typing import List
from biliup.plugins.bili_webup import BiliBili, Data

from uploaders.base_uploader import BaseUploader
from video_item import VideoItem
from token_manager import TokenManager


BILIBILI_TID = 171
BILIBILI_COPYRIGHT = 1
BILIBILI_TAGS = [
    "StarCraft2", "星海爭霸2", "SC2",
    "天梯", "Protoss", "神族", "Ladder"
]


class BilibiliUploader(BaseUploader):
    """B站上傳器，使用 biliup 投稿"""

    def __init__(self, token_manager: TokenManager):
        """
        初始化 B站上傳器

        Args:
            token_manager: Token 管理器（用於讀取 Cookie）
        """
        self.token_manager = token_manager

    def upload(self, video: VideoItem) -> str:
        """
        上傳影片到 B站

        Args:
            video: 影片資料

        Returns:
            str: B站 BV 號

        Raises:
            ValueError: Cookie 未設定
            Exception: 上傳失敗
        """
        if not self.validate_video(video):
            raise ValueError("影片資料不完整")

        cookies = self.token_manager.get_bilibili_cookies()
        if not cookies:
            raise ValueError("請先設定 B站 Cookie（bilibili_cookie.json）")

        video_data = Data()
        video_data.title = video.title
        video_data.desc = video.description or ""
        video_data.tid = BILIBILI_TID
        video_data.set_tag(BILIBILI_TAGS)
        video_data.copyright = BILIBILI_COPYRIGHT

        dtime = video.get_bilibili_dtime()
        if dtime > 0:
            video_data.delay_time(dtime)

        credential = {
            'cookies': {
                'SESSDATA': cookies['SESSDATA'],
                'bili_jct': cookies['bili_jct'],
                'DedeUserID__ckMd5': cookies['DedeUserID__ckMd5'],
                'DedeUserID': cookies['DedeUserID'],
            },
            'access_token': '',
        }

        with BiliBili(video_data) as bili:
            bili.login(self.token_manager.BILIBILI_COOKIE_FILE, credential)

            video_part = bili.upload_file(video.video_path, lines='AUTO', tasks=3)
            video_data.append(video_part)

            if video.thumbnail_path and os.path.exists(video.thumbnail_path):
                cover_url = bili.cover_up(video.thumbnail_path)
                video_data.cover = cover_url.replace('http:', '')

            ret = bili.submit()

        bvid = ret.get('data', {}).get('bvid', '') if isinstance(ret, dict) else ''
        print(f"✅ B站投稿成功: {bvid}")
        return bvid

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """封面在 upload() 內部處理，此方法為空操作"""
        return True

    def add_to_playlist(self, video_id: str, playlist_ids: List[str]) -> bool:
        """合集功能尚未實作"""
        raise NotImplementedError("B站合集功能尚未實作")
```

- [ ] **Step 2: 手動驗證匯入正常**

```bash
python -c "from uploaders.bilibili_uploader import BilibiliUploader; print('OK')"
```

Expected: 輸出 `OK`

- [ ] **Step 3: Commit**

```bash
git add uploaders/bilibili_uploader.py
git commit -m "feat: 實作 BilibiliUploader（基於 biliup）"
```

---

## Task 5: 更新 VideoEditorDialog — B站 投稿區塊

**Files:**
- Modify: `dialogs/video_editor_dialog.py`

- [ ] **Step 1: 在 setupUi() 的按鈕區之前，新增 B站 區塊**

找到 `dialogs/video_editor_dialog.py` 中的 `# === 按鈕區 ===`（約第 148 行），在其前面插入：

```python
        # === B站 投稿區 ===
        bilibili_group = QtWidgets.QGroupBox("B站 投稿")
        bilibili_layout = QtWidgets.QVBoxLayout(bilibili_group)

        self.ckbBilibili = QtWidgets.QCheckBox("同步上傳到 B站")
        self.ckbBilibili.stateChanged.connect(self._on_bilibili_checked)
        bilibili_layout.addWidget(self.ckbBilibili)

        bilibili_time_layout = QtWidgets.QHBoxLayout()
        bilibili_time_label = QtWidgets.QLabel("B站發布時間:")
        self.dtBilibiliPublish = QtWidgets.QDateTimeEdit()
        self.dtBilibiliPublish.setCalendarPopup(True)
        self.dtBilibiliPublish.setDateTime(
            QtCore.QDateTime(QtCore.QDate.currentDate(), QtCore.QTime(19, 0))
        )
        bilibili_time_layout.addWidget(bilibili_time_label)
        bilibili_time_layout.addWidget(self.dtBilibiliPublish)
        bilibili_time_layout.addStretch()
        bilibili_layout.addLayout(bilibili_time_layout)

        self.bilibili_time_widget = QtWidgets.QWidget()
        self.bilibili_time_widget.setLayout(bilibili_time_layout)
        bilibili_layout.addWidget(self.bilibili_time_widget)
        self.bilibili_time_widget.setVisible(False)

        main_layout.addWidget(bilibili_group)
```

注意：`bilibili_time_layout` 需要重構為 Widget 才能控制顯示/隱藏。請用以下更清晰的版本取代上面的整個 B站 區塊：

```python
        # === B站 投稿區 ===
        bilibili_group = QtWidgets.QGroupBox("B站 投稿")
        bilibili_layout = QtWidgets.QVBoxLayout(bilibili_group)

        self.ckbBilibili = QtWidgets.QCheckBox("同步上傳到 B站")
        self.ckbBilibili.stateChanged.connect(self._on_bilibili_checked)
        bilibili_layout.addWidget(self.ckbBilibili)

        self.bilibiliTimeWidget = QtWidgets.QWidget()
        bilibili_time_layout = QtWidgets.QHBoxLayout(self.bilibiliTimeWidget)
        bilibili_time_layout.setContentsMargins(0, 0, 0, 0)
        bilibili_time_label = QtWidgets.QLabel("B站發布時間:")
        self.dtBilibiliPublish = QtWidgets.QDateTimeEdit()
        self.dtBilibiliPublish.setCalendarPopup(True)
        self.dtBilibiliPublish.setDateTime(
            QtCore.QDateTime(QtCore.QDate.currentDate(), QtCore.QTime(19, 0))
        )
        bilibili_time_layout.addWidget(bilibili_time_label)
        bilibili_time_layout.addWidget(self.dtBilibiliPublish)
        bilibili_time_layout.addStretch()
        self.bilibiliTimeWidget.setVisible(False)
        bilibili_layout.addWidget(self.bilibiliTimeWidget)

        main_layout.addWidget(bilibili_group)
```

- [ ] **Step 2: 新增 _on_bilibili_checked() 方法**

在 `select_video_file()` 方法之前加入：

```python
    def _on_bilibili_checked(self, state: int):
        """
        B站 勾選框狀態變更時，顯示/隱藏發布時間，並同步預設時間
        
        Args:
            state: Qt.Checked 或 Qt.Unchecked
        """
        is_checked = state == QtCore.Qt.Checked
        self.bilibiliTimeWidget.setVisible(is_checked)

        if is_checked:
            # 預設為 YouTube 發布時間 + 1 小時
            yt_dt = self.publishTime.dateTime()
            bilibili_dt = yt_dt.addSecs(3600)
            self.dtBilibiliPublish.setDateTime(bilibili_dt)
```

- [ ] **Step 3: 更新 load_video_data() — 載入 B站 欄位**

在 `load_video_data()` 中，標題設定之後加入：

```python
        # B站 投稿
        if self.video.upload_to_bilibili:
            self.ckbBilibili.setChecked(True)
            if self.video.bilibili_publish_time:
                qt_bilibili_dt = QtCore.QDateTime.fromString(
                    self.video.bilibili_publish_time.strftime("%Y-%m-%d %H:%M"),
                    "yyyy-MM-dd HH:mm"
                )
                self.dtBilibiliPublish.setDateTime(qt_bilibili_dt)
```

- [ ] **Step 4: 更新 confirm() — 儲存 B站 欄位**

在 `confirm()` 中的 `publish_time` 解析之後，`thumbnail_path` 之前加入 B站 時間解析：

```python
        # 解析 B站 發布時間
        bilibili_publish_time = None
        if self.ckbBilibili.isChecked():
            qt_bilibili = self.dtBilibiliPublish.dateTime()
            bilibili_publish_time = datetime(
                qt_bilibili.date().year(),
                qt_bilibili.date().month(),
                qt_bilibili.date().day(),
                qt_bilibili.time().hour(),
                qt_bilibili.time().minute()
            )
```

在編輯模式的欄位更新區段（`self.video.match_type = match_type` 之後）加入：

```python
            self.video.upload_to_bilibili = self.ckbBilibili.isChecked()
            self.video.bilibili_publish_time = bilibili_publish_time
```

在新增模式的 `VideoItem(...)` 建構式中，`match_type=match_type` 之後加入：

```python
                upload_to_bilibili=self.ckbBilibili.isChecked(),
                bilibili_publish_time=bilibili_publish_time,
```

- [ ] **Step 5: 新增 timedelta import**

確認 `video_editor_dialog.py` 頂部的 datetime import 包含 timedelta：

```python
from datetime import datetime, timedelta
```

（目前只有 `from datetime import datetime`，需加上 `, timedelta`）

- [ ] **Step 6: 手動測試 UI**

```bash
python dialogs/video_editor_dialog.py
```

驗證：
- 對話框正常開啟
- 「B站 投稿」區塊顯示在字幕語言下方
- 勾選「同步上傳到 B站」後，B站 發布時間顯示，且預設為當前時間 +1 小時
- 取消勾選後，B站 發布時間隱藏

- [ ] **Step 7: Commit**

```bash
git add dialogs/video_editor_dialog.py
git commit -m "feat: VideoEditorDialog 新增 B站 投稿勾選框與發布時間"
```

---

## Task 6: 更新 TokenStatusDialog — B站 Cookie 狀態

**Files:**
- Modify: `dialogs/token_status_dialog.py`

- [ ] **Step 1: 更新 check_tokens() — 加入 B站 檢查**

在 `check_tokens()` 中，`statuses = self.token_manager.check_all_tokens()` 之後加入 B站 檢查：

```python
        # 執行 YouTube/Google Drive 檢查
        statuses = self.token_manager.check_all_tokens()

        # 加入 B站 Cookie 狀態
        is_bilibili_ok = self.token_manager.is_bilibili_logged_in()
        # 移除載入中標籤
        self.status_layout.removeWidget(loading_label)
        loading_label.deleteLater()

        # 顯示 YouTube / Google Drive 結果
        for name, status in statuses.items():
            self.add_token_status_widget(name, status)

        # 顯示 B站 狀態
        self._add_bilibili_status_widget(is_bilibili_ok)
```

注意：原本的「移除載入中標籤」和「顯示結果」也在 `check_tokens()` 裡，需要重新排版。請用以下完整替換 `check_tokens()` 方法：

```python
    def check_tokens(self):
        """檢查所有 Token 狀態"""
        self.clear_status_widgets()

        loading_label = QtWidgets.QLabel("檢查中...")
        self.status_layout.addWidget(loading_label)
        QtWidgets.QApplication.processEvents()

        statuses = self.token_manager.check_all_tokens()
        is_bilibili_ok = self.token_manager.is_bilibili_logged_in()

        self.status_layout.removeWidget(loading_label)
        loading_label.deleteLater()

        for name, status in statuses.items():
            self.add_token_status_widget(name, status)

        self._add_bilibili_status_widget(is_bilibili_ok)
```

- [ ] **Step 2: 新增 _add_bilibili_status_widget() 方法**

在 `add_token_status_widget()` 之後加入：

```python
    def _add_bilibili_status_widget(self, is_logged_in: bool):
        """
        新增 B站 Cookie 狀態顯示元件
        
        Args:
            is_logged_in: Cookie 是否有效
        """
        container = QtWidgets.QGroupBox("B站 Cookie")
        container_layout = QtWidgets.QVBoxLayout(container)

        if is_logged_in:
            status_label = QtWidgets.QLabel("✅ 已設定")
            status_label.setStyleSheet("color: green; font-size: 11pt;")
        else:
            status_label = QtWidgets.QLabel("❌ 未設定")
            status_label.setStyleSheet("color: red; font-size: 11pt;")
        container_layout.addWidget(status_label)

        button_layout = QtWidgets.QHBoxLayout()
        btn_text = "🔄 重新設定" if is_logged_in else "🔐 設定 Cookie"
        cookie_btn = QtWidgets.QPushButton(btn_text)
        cookie_btn.clicked.connect(self._open_bilibili_cookie_dialog)
        button_layout.addWidget(cookie_btn)
        button_layout.addStretch()
        container_layout.addLayout(button_layout)

        self.status_layout.addWidget(container)

    def _open_bilibili_cookie_dialog(self):
        """開啟 B站 Cookie 輸入對話框"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("設定 B站 Cookie")
        dialog.resize(500, 320)
        layout = QtWidgets.QVBoxLayout(dialog)

        instruction = QtWidgets.QLabel(
            "請貼上 B站 Cookie JSON（需包含 SESSDATA, bili_jct, DedeUserID, DedeUserID__ckMd5）："
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        text_edit = QtWidgets.QPlainTextEdit()
        text_edit.setPlaceholderText(
            '{\n'
            '  "SESSDATA": "your_sessdata",\n'
            '  "bili_jct": "your_bili_jct",\n'
            '  "DedeUserID": "your_uid",\n'
            '  "DedeUserID__ckMd5": "your_ckmd5"\n'
            '}'
        )
        layout.addWidget(text_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QtWidgets.QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QtWidgets.QPushButton("儲存")
        save_btn.clicked.connect(lambda: self._save_bilibili_cookie(text_edit.toPlainText(), dialog))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        dialog.exec_()

    def _save_bilibili_cookie(self, json_text: str, dialog: QtWidgets.QDialog):
        """
        驗證並儲存 B站 Cookie
        
        Args:
            json_text: 使用者輸入的 JSON 文字
            dialog: 輸入對話框（成功後關閉）
        """
        import json
        try:
            cookies = json.loads(json_text.strip())
        except Exception:
            QtWidgets.QMessageBox.warning(self, "格式錯誤", "請輸入有效的 JSON 格式。")
            return

        required = ["SESSDATA", "bili_jct", "DedeUserID", "DedeUserID__ckMd5"]
        missing = [f for f in required if f not in cookies]
        if missing:
            QtWidgets.QMessageBox.warning(
                self, "欄位缺少",
                f"Cookie 缺少必要欄位：{', '.join(missing)}"
            )
            return

        if self.token_manager.save_bilibili_cookies(cookies):
            QtWidgets.QMessageBox.information(self, "成功", "B站 Cookie 已儲存！")
            dialog.accept()
            self.check_tokens()
        else:
            QtWidgets.QMessageBox.critical(self, "錯誤", "儲存失敗，請檢查檔案權限。")
```

- [ ] **Step 3: 手動測試 UI**

```bash
python dialogs/token_status_dialog.py
```

驗證：
- 對話框顯示三個狀態區塊（YouTube、Google Drive、B站 Cookie）
- B站 顯示「❌ 未設定」（首次執行時）
- 點擊「設定 Cookie」出現 JSON 輸入框
- 輸入格式錯誤的 JSON 時顯示警告
- 缺少欄位時顯示哪些欄位缺少
- 正確 JSON 儲存後，狀態更新為「✅ 已設定」

- [ ] **Step 4: Commit**

```bash
git add dialogs/token_status_dialog.py
git commit -m "feat: TokenStatusDialog 新增 B站 Cookie 狀態與設定入口"
```

---

## Task 7: 整合 B站 上傳到批次流程

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 在 main.py 頂部新增 BilibiliUploader import**

在現有 import 區段加入：

```python
from uploaders.bilibili_uploader import BilibiliUploader
```

- [ ] **Step 2: 在 _execute_batch_upload() 中加入 B站 上傳步驟**

找到 `_execute_batch_upload()` 中 YouTube 上傳成功後的區段（約第 304 行 `video.set_status(UploadStatus.COMPLETED)`），在其之前插入 B站 上傳邏輯：

```python
                # 4. 添加多國語言
                print(f"添加多國語言...")
                self.youtube_uploader.add_localizations(video_id, video.replay_url or "")

                # 5. 同步投稿到 B站（若已勾選）
                if video.upload_to_bilibili:
                    print(f"投稿到 B站...")
                    try:
                        bilibili_uploader = BilibiliUploader(self.token_manager)
                        bvid = bilibili_uploader.upload(video)
                        video.bilibili_video_id = bvid
                        print(f"✅ B站投稿成功: {bvid}")
                    except Exception as bilibili_err:
                        print(f"⚠️ B站投稿失敗（YouTube 已成功）: {bilibili_err}")
                        QtWidgets.QMessageBox.warning(
                            self,
                            "B站投稿失敗",
                            f"影片「{video.title}」的 B站 投稿失敗：\n{bilibili_err}\n\n（YouTube 上傳已成功）"
                        )

                # 設定為完成
                video.set_status(UploadStatus.COMPLETED)
```

- [ ] **Step 3: 手動執行主程式驗證**

```bash
python main.py
```

驗證：
- 主視窗正常啟動
- 新增影片後，編輯視窗出現「B站 投稿」區塊
- 勾選「同步上傳到 B站」時，B站 發布時間正確顯示
- 不勾選 B站 的情況下，正常執行 YouTube 上傳流程（不報錯）
- 「🔐 檢查 Token」按鈕的對話框顯示 B站 Cookie 狀態列

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: 批次上傳流程串接 B站 投稿（YouTube 成功後觸發）"
```

---

## 驗收清單

完成所有 Task 後，確認以下行為：

- [ ] `python tests/test_bilibili_fields.py` 全部通過
- [ ] `python main.py` 正常啟動，無 ImportError
- [ ] 新增影片 → 勾選「同步上傳到 B站」→ B站 時間預設為 YouTube 時間 +1 小時
- [ ] 「🔐 檢查 Token」→ 顯示 B站 Cookie 狀態
- [ ] 未設定 Cookie 時點「設定 Cookie」→ 可貼上 JSON 儲存
- [ ] `bilibili_cookie.json` 存在時，B站 狀態顯示「✅ 已設定」
- [ ] YouTube 上傳成功 + 未勾選 B站 → 流程正常結束，不呼叫 BilibiliUploader
- [ ] YouTube 上傳成功 + 已勾選 B站 + Cookie 已設定 → 執行 B站 投稿
- [ ] B站 投稿失敗 → 顯示 Warning，YouTube 狀態仍為「已完成」
