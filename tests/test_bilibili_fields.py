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


if __name__ == '__main__':
    test_bilibili_defaults()
    test_get_bilibili_dtime_future()
    test_get_bilibili_dtime_past()
    test_get_bilibili_dtime_none()
    test_to_dict_includes_bilibili_fields()
    test_from_dict_restores_bilibili_fields()
    test_is_bilibili_logged_in_missing_file()
    test_is_bilibili_logged_in_valid()
    test_is_bilibili_logged_in_missing_field()
    test_get_bilibili_cookies_returns_dict()
    test_get_bilibili_cookies_missing_file()
    print("All tests passed!")
