OpenAI Realtime API - 即時語音翻譯系統專案報告
1. 專案概述 (Project Overview)
本專案實作了一個基於 OpenAI Realtime API (WebSocket) 的全雙工即時語音翻譯系統。系統能透過麥克風擷取使用者語音，並透過 GPT-4o-mini 模型即時轉寫（Transcription）並翻譯（Translation）為英文。

本系統的核心特色在於 「嚴格順序控制 (Strict Order Logic)」，解決了串流傳輸中翻譯內容可能先於原文出現的非同步問題，確保使用者介面呈現符合閱讀邏輯（先顯示原文，再顯示譯文）。

2. 技術架構 (Technical Architecture)
核心技術堆疊
語言: Python 3.x

通訊協定: WebSocket (wss://) - 實現低延遲雙向傳輸。

並發處理: asyncio - 同時處理音訊上傳 (Producer) 與文字接收 (Consumer)。

音訊處理: PyAudio - 負責 24kHz / 16-bit PCM 音訊流的實時擷取。

模型: gpt-4o-mini-realtime-preview 搭配 whisper-1 進行語音識別。

資料流架構
系統採用全雙工模式運作，資料流向如下：

上行 (Uplink): 本地端持續將 Base64 編碼的音訊 Chunk 推送至 OpenAI Server。

處理 (Processing): Server 端進行 VAD (語音偵測)、STT (轉寫) 與 LLM 推論。

下行 (Downlink): Server 非同步回傳 transcript (原文) 與 text.delta (翻譯)。

3. 關鍵邏輯：嚴格順序控制 (Strict Order Logic)
為了避免即時串流中「翻譯跑得比原文快」導致的閱讀混亂，本程式碼實作了 Buffer Gate 機制。

運作流程
緩衝階段: 當收到翻譯文字 (response.text.delta) 但尚未收到完整原文時，系統將翻譯文字暫存於 self.buffered_translation，不輸出至螢幕。

檢查點 (Checkpoint): 系統監聽 conversation.item.input_audio_transcription.completed 事件。一旦收到，確認原文已完整（印出 👂 [中文原文]）。

釋放階段: 原文確認後，系統將 transcript_received 設為 True，並立即釋放緩衝區內的翻譯文字，隨後的串流內容則直接輸出。