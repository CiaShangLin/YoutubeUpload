"""Read Bilibili login cookies from Chromium-based browsers on Windows."""

import base64
import ctypes
import json
import os
import shutil
import sqlite3
import tempfile
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


BILIBILI_COOKIE_NAMES = ("SESSDATA", "bili_jct")


@dataclass
class BilibiliCookies:
    sessdata: str
    bili_jct: str
    source: str

    @property
    def csrf(self) -> str:
        return self.bili_jct

    def as_cookie_header(self) -> str:
        return f"SESSDATA={self.sessdata}; bili_jct={self.bili_jct}"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def get_bilibili_cookies(config_path: str = "bilibili_cookies.json") -> BilibiliCookies:
    """Load Bilibili cookies from browsers first, then from a local JSON file."""
    browser_cookies = load_from_browsers()
    if browser_cookies:
        return browser_cookies

    file_cookies = load_from_config(config_path)
    if file_cookies:
        return file_cookies

    raise RuntimeError(
        "Cannot find Bilibili cookies. Login to bilibili.com in Chrome/Edge, "
        "or create bilibili_cookies.json with SESSDATA and bili_jct."
    )


def load_from_config(config_path: str = "bilibili_cookies.json") -> Optional[BilibiliCookies]:
    path = Path(config_path)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    sessdata = data.get("SESSDATA") or data.get("sessdata")
    bili_jct = data.get("bili_jct") or data.get("csrf")
    if sessdata and bili_jct:
        return BilibiliCookies(sessdata=sessdata, bili_jct=bili_jct, source=str(path))
    return None


def load_from_browsers() -> Optional[BilibiliCookies]:
    for browser_name, user_data_dir in _browser_roots():
        local_state = user_data_dir / "Local State"
        if not local_state.exists():
            continue

        try:
            key = _get_chromium_key(local_state)
        except Exception:
            continue

        for cookies_db in _cookie_databases(user_data_dir):
            try:
                cookies = _read_bilibili_cookie_db(cookies_db, key)
            except OSError:
                continue
            if all(name in cookies for name in BILIBILI_COOKIE_NAMES):
                return BilibiliCookies(
                    sessdata=cookies["SESSDATA"],
                    bili_jct=cookies["bili_jct"],
                    source=f"{browser_name}:{cookies_db}",
                )
    return None


def _browser_roots() -> Iterable[tuple[str, Path]]:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return []

    base = Path(local_app_data)
    return [
        ("Chrome", base / "Google" / "Chrome" / "User Data"),
        ("Edge", base / "Microsoft" / "Edge" / "User Data"),
    ]


def _cookie_databases(user_data_dir: Path) -> Iterable[Path]:
    for profile_dir in user_data_dir.iterdir():
        if not profile_dir.is_dir():
            continue
        if profile_dir.name not in {"Default", "Guest Profile"} and not profile_dir.name.startswith("Profile "):
            continue

        for relative in (Path("Network") / "Cookies", Path("Cookies")):
            db = profile_dir / relative
            if db.exists():
                yield db


def _get_chromium_key(local_state_path: Path) -> bytes:
    with local_state_path.open("r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    if encrypted_key.startswith(b"DPAPI"):
        encrypted_key = encrypted_key[5:]
    return _crypt_unprotect_data(encrypted_key)


def _read_bilibili_cookie_db(cookies_db: Path, key: bytes) -> Dict[str, str]:
    copied_db = _copy_locked_db(cookies_db)
    cookies: Dict[str, str] = {}
    try:
        connection = sqlite3.connect(str(copied_db))
        try:
            cursor = connection.execute(
                """
                SELECT host_key, name, value, encrypted_value
                FROM cookies
                WHERE host_key LIKE '%bilibili.com'
                  AND name IN ('SESSDATA', 'bili_jct')
                """
            )
            for _host_key, name, value, encrypted_value in cursor.fetchall():
                decrypted = value or _decrypt_chromium_value(encrypted_value, key)
                if decrypted:
                    cookies[name] = decrypted
        finally:
            connection.close()
    finally:
        try:
            copied_db.unlink()
        except OSError:
            pass
    return cookies


def _copy_locked_db(source: Path) -> Path:
    fd, destination = tempfile.mkstemp(prefix="bilibili-cookies-", suffix=".sqlite")
    os.close(fd)
    shutil.copy2(source, destination)
    return Path(destination)


def _decrypt_chromium_value(encrypted_value: bytes, key: bytes) -> str:
    if not encrypted_value:
        return ""

    if encrypted_value.startswith((b"v10", b"v11", b"v20")):
        nonce = encrypted_value[3:15]
        ciphertext = encrypted_value[15:]
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    return _crypt_unprotect_data(encrypted_value).decode("utf-8")


def _crypt_unprotect_data(encrypted: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    in_blob = DATA_BLOB(len(encrypted), ctypes.cast(ctypes.create_string_buffer(encrypted), ctypes.POINTER(ctypes.c_char)))
    out_blob = DATA_BLOB()

    if not crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()

    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)
