# 【整合專案報告】OpenAI Realtime API：安全中繼架構與即時語音翻譯系統

## 一、 專案概述 (Project Overview)
本專案開發了一個結合 **安全防護** 與 **高效翻譯** 的語音交互系統。透過 FastAPI 建立後端中繼站，並利用 OpenAI Realtime API (WebSocket) 實現低延遲、全雙工的即時翻譯體驗。

### 核心目標
1. **安全強化**：隱藏 API Key，發放臨時憑證。
2. **語音識別**：精準擷取使用者語音並轉為繁體中文原文。
3. **翻譯順序控制**：解決非同步傳輸導致的原文/譯文順序錯亂問題。

---

## 二、 系統架構與資料流 (System Architecture)

### 1. 安全中繼流程 (Security Proxy)
為了避免 `OPENAI_API_KEY` 在前端外洩，系統採取「雙層授權」機制：
* **後端守門**：由 FastAPI 安全保管永久金鑰。
* **短期通行證**：前端請求 `/session`，後端向 OpenAI 換取 **限時 1 分鐘有效** 的 Ephemeral Token。



### 2. 資料流向細節
* **上行 (Uplink)**：24kHz / 16-bit PCM 音訊以 Base64 編碼推送至伺服器。
* **處理 (Processing)**：OpenAI 執行語音偵測 (VAD) 與 GPT-4o-mini 推論。
* **下行 (Downlink)**：伺服器非同步回傳轉錄結果 (`transcript`) 與翻譯增量 (`text.delta`)。

---

## 三、 核心邏輯：嚴格順序控制 (Strict Order Logic)

在全雙工串流中，常發生「翻譯內容比原文轉錄更快出現」的現象。本系統實作了 **Buffer Gate (緩衝閘)** 機制，落實「以時間換取閱讀邏輯」的策略。



### 執行步驟：
1. **緩衝階段 (Buffer)**：
   當收到翻譯數據但原文轉錄尚未完成時，先將翻譯文字暫存於 `buffered_translation` 變數中。
2. **檢查點確認 (Checkpoint)**：
   系統監聽 `input_audio_transcription.completed` 事件，確保語句錄製已完整（靜音偵測設為 `1000ms`）。
3. **釋放與輸出 (Release)**：
   確認原文輸出後（印出 `👂 [中文原文]`），立即釋放緩衝區內的翻譯文字（印出 `🅰️ [英譯]`）。

### 範例展示：
> **輸入聲音**：「翻譯模型好厲害」
> 1. `👂 [中文原文]: 翻譯模型好厲害`
> 2. `✅ [檢查點]: 確認原文已載入模型，準備翻譯...`
> 3. `🅰️ [英譯]: Wow, this translation model is really impressive!`

---

## 四、 技術規格快速對照表

| 項目 | 詳細說明 |
| :--- | :--- |
| **開發框架** | FastAPI (Python) + WebSocket |
| **即時模型** | gpt-4o-mini-realtime-preview |
| **通訊協定** | WebSocket / WebRTC |
| **音訊處理** | PyAudio / 24kHz Mono 16-bit PCM |
| **安全機制** | Ephemeral Session Token (限時憑證) |
| **指令規範** | 強制「繁體中文（台灣用語）」 |

---

## 五、 當前挑戰與未來改進 (Issues & Future Work)

1. **翻譯任務競爭**：
   * **問題**：當語速過快或句子過長時，模型可能為了處理下一句而跳過目前的翻譯。
   * **優化**：預計引入 **Task Queue (任務隊列)** 確保每一句翻譯任務皆能完整執行。

2. **視覺回饋優化**：
   * **問題**：目前需等待靜音偵測結束後才顯示文字，反饋稍有延遲。
   * **優化**：未來將加入 **流暢轉錄 (Streaming STT)** 功能，讓使用者在說話當下即可看到「文字預覽」。

---

## 六、 如何運行專案
1. 在 `.env` 設定 `OPENAI_API_KEY`。
2. 執行 `uvicorn main:app --reload` 啟動伺服器。
3. 瀏覽器開啟 `http://localhost:8000` 即可開始即時語音翻譯。
