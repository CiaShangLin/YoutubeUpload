# 星海爭霸 2 影片字幕製作流程分析

> 分析日期：2026-08-21
> 狀態：分析階段，尚未實作

## 背景

目標流程：
1. 使用 Whisper 產生字幕檔
2. 透過繁體中文語言 lib 檢查文字
3. 分詞
4. 專有名詞常用替換表（修正 ASR 錯字，例如「叉」→「狂戰士」、「王重」→「王蟲」）
5. 分析字幕 + Replay（RP）單位頻率，產出影片簡短說明

---

## 階段拆解與技術選項

### 階段 1：語音轉字幕（ASR）

- 原生 `openai-whisper` 速度慢，且無精確逐字時間戳
- 建議改用：
  - **faster-whisper**（CTranslate2 重寫，同精度下快約 4 倍）
  - **WhisperX**（在 faster-whisper 基礎上疊加 wav2vec2 強制對齊，可取得精確到 <100ms 的逐字時間戳，對後續分詞後重切 SRT 時間軸很關鍵）
- 對戰語音常混雜英文單位名（Zealot / Mutalisk）與口頭禪，建議用 `initial_prompt` 或自訂詞彙表提示 Whisper，從源頭減少辨識錯誤，比事後修正更省事

### 階段 2：簡轉繁 + 文字正規化（原規劃未涵蓋，建議補上）

Whisper 中文模型常輸出簡體或簡繁混雜，若不處理，後續分詞與替換表比對都會失準：

- **OpenCC**（`opencc-python-reimplemented` 或原生 `opencc`），使用 `s2twp.json`（簡體轉台灣正體＋詞彙轉換，例如「軟件」→「軟體」）

### 階段 3：分詞（對應「台灣語言 lib」）

- **CKIP Transformers**（中研院 CKIP Lab）：斷詞 + 詞性標註 + NER，繁中支援最完整、準確度最高，但模型較重，跑起來吃資源
- 較輕量替代：**jieba**（可用 `jieba.set_dictionary` 換成繁中詞庫），速度快很多但準確度較低，對未登錄詞（OOV，如遊戲術語）表現較弱
- 關鍵：**SC2 專有名詞（狂戰士、王蟲、跳蟲、電磁脈衝...）需餵入自訂詞典**，否則分詞會把專有名詞切碎，影響階段 4 的比對效果

### 階段 4：專有名詞替換表（錯字修正）

單純字典替換（exact match dict）只能處理已知的固定錯誤，無法泛化到未見過的變體。可補強：

- **rapidfuzz**：對分詞結果做模糊比對，計算與專有名詞庫的編輯距離，抓出疑似錯誤但未收錄在字典裡的詞
- **pypinyin**：將辨識詞轉拼音/注音，與正確術語庫比對相似度（例如「王重」ㄨㄤˊ ㄓㄨㄥˋ vs「王蟲」ㄨㄤˊ ㄔㄨㄥˊ 韻母相近），可捕捉同音字錯誤，比純 dict 替換更 robust

建議架構：**一個 JSON/YAML 詞庫 + 一層 fuzzy fallback**，而非只靠死板 dict。fuzzy 抓到的疑似錯誤應標記為「待人工確認」，不自動替換，避免誤改。

### 階段 5：字幕檔輸出/處理（原規劃未涵蓋，建議補上）

- **srt** 或 **pysrt**：讀寫、合併、調整時間軸
- 若使用 WhisperX 的逐字時間戳，替換專有名詞後需連動更新該詞對應的時間區間

### 階段 6：字幕 + APM/單位頻率 → 簡短說明

需要兩份資料源同時輸入：

- **字幕文字**：分詞後可用 `jieba.analyse`（TF-IDF/TextRank）做關鍵詞/頻率抽取，或整份丟給 LLM 摘要
- **Replay 解析**：
  - **sc2reader**：解析 `.SC2Replay`，取得 APM、單位建造事件（UnitInitEvent）、時間軸資料
  - **spawningtool**：基於 sc2reader 進一步整理出人類可讀的 build order，比自行刻事件解析省事

將 replay 抽出的單位頻率/APM 曲線，與字幕文字（含時間戳）對齊後一併餵給 LLM（例如 Claude API）生成摘要，會比純文字摘要更準確，因為能結合「這段時間在做什麼」與「講者當下說了什麼」。

---

## 建議補上的部分（原規劃未涵蓋）

1. **簡繁轉換（OpenCC）**：不補這步，後面分詞和替換表比對都會失準
2. **人工審核/待確認佇列**：fuzzy matching 抓到的疑似錯誤不自動替換，應產出建議清單供人工快速確認後套用
3. **SC2 專有名詞詞庫同時餵給「分詞」與「Whisper prompt」兩處**，從源頭減少辨識錯誤，比事後修正更有效率
4. **逐字時間戳（WhisperX）而非整句時間戳**：若之後要做「單位頻率 vs 講解內容」的精確時間對齊，逐字級別遠比整句級別準確
5. **版本化/快取中間產物**：Whisper 原始輸出、簡繁轉換後、分詞後、替換後，建議都存成中間檔案，方便 debug 定位問題階段，也方便單獨重跑某一階段而不必整個 pipeline 重來

---

## 參考資料

- [CKIP Transformers GitHub](https://github.com/ckiplab/ckip-transformers)
- [sc2reader GitHub](https://github.com/GraylinKim/sc2reader)
- [spawningtool PyPI](https://pypi.org/project/spawningtool/)
- [WhisperX GitHub](https://github.com/m-bain/whisperx)
