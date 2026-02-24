import json
from celery import Celery
from dotenv import load_dotenv
from google import genai
from google.genai import types
import redis # Import redis driver
from typing import Optional

load_dotenv()

# Redis URL
REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "ai_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

client = genai.Client()

# Create a synchronous Redis client for publishing
redis_client = redis.from_url(REDIS_URL)

@celery_app.task(bind=True, name="analyze_text_task")
def analyze_text_task(self, text: str, target_ticker: Optional[str] = None):
    if target_ticker:
        prompt = f"""
        You are a highly analytical financial sentiment agent. 
        Analyze the following text and determine the market sentiment and impact specifically on the asset {target_ticker}.
        Provide the reasoning for how this text impacts {target_ticker}.
        Always return {target_ticker} as the primary_ticker.

        Text: "{text}"
        """
    else:
        prompt = f"""
        You are a highly analytical financial sentiment agent. 
        Analyze the following text and determine the market sentiment and the primary asset ticker being discussed.
        If no specific company or asset is mentioned, use a broad market ETF like SPY or BTC.

        Text: "{text}"
        """

    try:
        # ... (Existing Gemini code) ...
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "score": {"type": "NUMBER"},
                        "reasoning": {"type": "STRING"},
                        "primary_ticker": {"type": "STRING"}
                    },
                    "required": ["score", "reasoning", "primary_ticker"]
                },
            ),
        )

        result = json.loads(response.text)

        # --- NEW CODE: BROADCAST ---
        # Tag the result with the original text for context
        final_payload = {
            "type": "insight",
            "text": text,
            "data": result
        }
        # Publish to the 'vibe_channel'
        redis_client.publish("vibe_channel", json.dumps(final_payload))
        # ---------------------------

        return result

    except Exception as e:
        error_msg = str(e)
        error_payload = {
            "type": "insight",
            "text": text,
            "data": {
                "score": 0.0,
                "reasoning": f"API Error: {error_msg}. Sent default neutral sentiment.",
                "primary_ticker": target_ticker or "BTC"
            }
        }
        redis_client.publish("vibe_channel", json.dumps(error_payload))
        return {"error": error_msg}