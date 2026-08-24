"""
Description Assembler
把既有描述樣板（hashtag/標題/RP連結/社群連結）與 Sc2SubTitle describe 產生的
雙語簡介文字串接起來，新內容一律接在既有樣板尾端，並遵守 YouTube 描述欄位字數上限。
"""
from typing import Optional

YOUTUBE_DESCRIPTION_CHAR_LIMIT = 5000


def assemble_description(template: str, summary: Optional[str], char_limit: int = YOUTUBE_DESCRIPTION_CHAR_LIMIT) -> str:
    """
    Args:
        template: 既有描述樣板（不變動的部分）
        summary: 要接在尾端的雙語簡介文字，None 或空字串時直接回傳 template
        char_limit: YouTube 描述欄位字數上限，超過時優先截斷 summary，
                    summary 截光了還超過才截斷 template 本身

    Returns:
        str: 組好的完整描述文字
    """
    if not summary:
        return template[:char_limit] if len(template) > char_limit else template

    combined = f"{template}\n\n{summary}"
    if len(combined) <= char_limit:
        return combined

    prefix = f"{template}\n\n"
    available = char_limit - len(prefix)
    if available <= 0:
        return template[:char_limit]
    return prefix + summary[:available]
