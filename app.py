from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import os
import httpx
from dotenv import load_dotenv

# -----------------------
# Load environment variables
# -----------------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# -----------------------
# FastAPI + Socket.IO setup
# -----------------------
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

asgi_app = socketio.ASGIApp(sio, app)

# -----------------------
# Wattbot system prompt (UNCHANGED)
# -----------------------
SYSTEM_PROMPT = """
You are Wattbot AI, a professional energy monitoring and analysis assistant.

Your role:
- Analyze user energy data accurately
- Answer questions using ONLY the data provided
- Perform basic calculations when required
- Identify high energy usage and inefficiencies
- Suggest practical energy-saving actions

Response style:
- Professional, clear, and confident
- Short, direct answers
- No unnecessary explanations
- No filler words
- No long or complex vocabulary
- Go straight to the point

Rules:
- Do NOT guess missing values
- Do NOT invent devices or usage
- If data is missing or unclear, state it briefly
- Do NOT say phrases like "based on the information provided"
- Do NOT mention internal analysis, prompts, or system instructions
- Avoid repetition

Energy guidance:
- Highlight devices with high power usage
- Compare devices when relevant
- Suggest turning off unused devices
- Recommend energy-efficient behavior when applicable

Tone:
- Helpful and expert
- Neutral and factual
- Friendly but not casual

You are Wattbot AI.
"""

# -----------------------
# Helper functions
# -----------------------
def format_devices(devices):
    lines = []
    for d in devices:
        status = "ON" if d.get("switchStatus") else "OFF"
        lines.append(
            f"- {d['name']} in {d['location']} | "
            f"Power: {d['power']}KW | "
            f"Energy: {d['energy']}kWh | "
            f"Status: {status} | "
            f"Type: {d['type']}"
        )
    return "\n".join(lines)

async def wattbot_chat(question, user, devices):
    device_summary = format_devices(devices)

    prompt = f"""
User Information:
- Name: {user['username']}
- Email: {user['email']}

Connected Devices:
{device_summary}

User Question:
{question}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://wattbot-ai.onrender.com",
        "X-Title": "Wattbot AI"
    }

    payload = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]

    return "Wattbot is busy. Try again shortly."

# -----------------------
# Socket.IO events
# -----------------------
@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.on("ask_wattbot")
async def ask_wattbot(sid, data):
    await sio.emit("wattbot_response", {"answer": "⚡ Analyzing energy data..."}, to=sid)

    answer = await wattbot_chat(
        data["question"],
        data["user"],
        data["devices"]
    )

    await sio.emit("wattbot_response", {"answer": answer}, to=sid)

# -----------------------
# Run server (Render compatible)
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        asgi_app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )

