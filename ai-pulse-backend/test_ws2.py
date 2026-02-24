import asyncio
import websockets
import json
import requests
import time

async def main():
    async with websockets.connect("ws://localhost:8000/ws/vibe") as websocket:
        print("Connected to WS. Triggering analyze...")
        r = requests.post("http://localhost:8000/analyze", json={
            "text": "Tesla is doomed!",
            "target_ticker": "TSLA"
        })
        print("Analyze response:", r.json())
        
        while True:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print("Received from WS:", msg)
                break
            except Exception as e:
                print("WS Recv Error/Timeout:", e)
                break

asyncio.run(main())
