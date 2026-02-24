import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from worker import celery_app
import redis.asyncio as redis  # Use async Redis
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ticker/{symbol}")
async def get_ticker_history(symbol: str):
    try:
        # Fetch the last 3 months to ensure we have at least 50 valid trading days
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        hist = hist.tail(50) # Grab exactly the last 50 points
        
        data_points = []
        for date, row in hist.iterrows():
            data_points.append({
                "time": date.strftime("%Y-%m-%d"),
                "price": row["Close"]
            })
            
        if not data_points:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
            
        return {
            "symbol": symbol,
            "data": data_points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional

class AnalyzeRequest(BaseModel):
    text: str
    target_ticker: Optional[str] = None

@app.post("/analyze")
async def trigger_analysis(request: AnalyzeRequest):
    """
    Instantly accepts the request, creates a background task, 
    and returns a task ID without waiting for the AI.
    """
    task = celery_app.send_task("analyze_text_task", args=[request.text, request.target_ticker])
    
    return {
        "status": "Queued", 
        "task_id": task.id,
        "message": "Task queued successfully. The AI is working on it."
    }

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"status": "Pending"}
    elif task_result.state == 'SUCCESS':
        return {"status": "Completed", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "Failed", "error": str(task_result.info)}
    else:
        return {"status": task_result.state}

import websockets as ws_client

@app.websocket("/ws/vibe")
async def vibe_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Connect to local Redis for listening to the Gemini AI
    redis_conn = redis.from_url("redis://localhost:6379/0")
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe("vibe_channel")

    try:
        while True:
            # Only listen to Redis here
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message["data"].decode("utf-8"))
                await websocket.send_json(data)
                
            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await redis_conn.close()