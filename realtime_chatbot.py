import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 提供前端的 HTML 頁面
@app.get("/")
async def get():
    with open("test.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# 產生 ephemeral session (短期憑證)
@app.get("/session")
async def get_session():
    url = "https://api.openai.com/v1/realtime/sessions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-4o-mini-realtime-preview",  # 語音即時模型
        "voice": "marin",
        "instructions": "請使用繁體中文（台灣用語），以自然的對話方式回應使用者。"   # 語音風格，可改成 verse, sage...
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=body)
        return JSONResponse(r.json())
