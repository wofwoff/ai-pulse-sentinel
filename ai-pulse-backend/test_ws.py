import asyncio
import websockets
import json

async def main():
    async with websockets.connect("ws://localhost:8000/ws/vibe") as websocket:
        print("Connected to WS.")
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"Received: {response}")
            except asyncio.TimeoutError:
                break

asyncio.run(main())
