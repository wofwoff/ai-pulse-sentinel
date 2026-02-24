import asyncio
import redis.asyncio as redis
import json

async def main():
    redis_conn = redis.from_url("redis://localhost:6379/0")
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe("vibe_channel")
    
    # create a task to publish
    redis_client_sync = redis.from_url("redis://localhost:6379/0")
    await redis_client_sync.publish("vibe_channel", '{"type": "insight", "text": "test", "data": {"score": 0.5}}')
    
    for _ in range(20):
        msg = await pubsub.get_message(ignore_subscribe_messages=True)
        if msg:
            data_val = msg["data"]
            print("got msg type:", type(data_val))
            try:
                data = json.loads(data_val.decode("utf-8"))
                print("Decoded successfully")
            except Exception as e:
                print("Error decoding:", e)
            print("Data:", data_val)
            break
        await asyncio.sleep(0.1)

asyncio.run(main())
