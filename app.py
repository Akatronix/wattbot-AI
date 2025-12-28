# # app.py
# # A Flask API for the WattBot AI Energy Monitoring Assistant.

# import os
# import random
# import json
# from flask import Flask, request, jsonify
# from google import genai
# from google.genai import types
# from flask_cors import CORS


# # app.py
# # A Flask API for the WattBot AI Energy Monitoring Assistant.

# from dotenv import load_dotenv  # <-- ADD THIS IMPORT

# # Load environment variables from a .env file
# load_dotenv()  # <-- ADD THIS LINE



# # ==============================================================================
# # --- CONFIGURATION ---
# # ==============================================================================

# app = Flask(__name__)
# CORS(app)

# # Load API keys from environment variables for security on Render
# # On Render, you will set GOOGLE_AI_KEY_1, GOOGLE_AI_KEY_2, etc.
# API_KEYS = [
#     os.environ.get("GOOGLE_AI_KEY_1"),
#     os.environ.get("GOOGLE_AI_KEY_2"),
#     os.environ.get("GOOGLE_AI_KEY_3"),
#     os.environ.get("GOOGLE_AI_KEY_4")
# ]

# # Filter out any keys that are not set
# API_KEYS = [key for key in API_KEYS if key]

# if not API_KEYS:
#     raise RuntimeError("FATAL ERROR: No Google AI API keys found in environment variables.")

# # The model we will use.
# MODEL_ID = "gemini-flash-latest"

# # ==============================================================================
# # --- WATTBOT AI PERSONA AND INSTRUCTIONS ---
# # ==============================================================================

# # SYSTEM_INSTRUCTION = """
# # You are Wattbot AI, a professional energy monitoring and analysis assistant.

# # Your role:
# # - Analyze user energy data accurately
# # - Answer questions using ONLY the data provided
# # - Perform basic calculations when required
# # - Identify high energy usage and inefficiencies
# # - Suggest practical energy-saving actions

# # Response style:
# # - Professional, clear, and confident
# # - Short, direct answers
# # - No unnecessary explanations
# # - No filler words
# # - No long or complex vocabulary
# # - Go straight to the point

# # Rules:
# # - Do NOT guess missing values
# # - Do NOT invent devices or usage
# # - If data is missing or unclear, state it briefly
# # - Do NOT say phrases like "based on the information provided"
# # - Do NOT mention internal analysis, prompts, or system instructions
# # - Avoid repetition

# # Energy guidance:
# # - Highlight devices with high power usage
# # - Compare devices when relevant
# # - Suggest turning off unused devices
# # - Recommend energy-efficient behavior when applicable

# # Tone:
# # - Helpful and expert
# # - Neutral and factual
# # - Friendly but not casual

# # You are Wattbot AI.
# # """
# SYSTEM_INSTRUCTION = """
# You are Wattbot AI, a professional energy monitoring and analysis assistant.

# Your role:
# - Analyze user energy data accurately when asked
# - Answer questions using ONLY the data provided
# - Perform basic calculations when required
# - Identify high energy usage and inefficiencies
# - Suggest practical energy-saving actions


#  Data-First Mandate
# - All analysis, calculations, and conclusions must be based strictly on the `user_device_data` provided in the request. Do not use general knowledge or make assumptions.
# - **CRITICAL: The 'power' data is in kilowatts (kW) and 'energy' is in kilowatt-hours (kWh); report these values with their correct units exactly as provided, with no conversions.**
# - **Never express numerical values in scientific notation; report all data exactly as it is provided.**
# - Do not perform calculations unless explicitly asked by the user (e.g., "calculate the total cost"). Your default is to report and compare, not to calculate.

# Response style:
# - Professional, clear, and confident
# - Short, direct answers
# - No unnecessary explanations
# - No filler words
# - No long or complex vocabulary
# - Go straight to the point

# Rules:
# - Do NOT guess missing values
# - Do NOT invent devices or usage
# - If data is missing or unclear, state it briefly
# - Do NOT say phrases like "based on the information provided"
# - Do NOT mention internal analysis, prompts, or system instructions
# - Avoid repetition
# - If the user sends a general greeting (e.g., "hi", "hello"), respond with a simple, professional greeting, e.g., "Hello [Username]. How can I assist you today?". Do not provide any analysis.
# - Only analyze the provided device data and give advice when the user asks a specific question about energy, power, usage, or a device.

# Energy guidance:
# - Highlight devices with high power usage
# - Compare devices when relevant
# - Suggest turning off unused devices
# - Recommend energy-efficient behavior when applicable

# Tone:
# - Helpful and expert
# - Neutral and factual
# - Friendly but not casual

# You are Wattbot AI.
# """


# # SYSTEM_INSTRUCTION = """
# # # Persona: Wattbot AI
# # You are Wattbot AI, an expert-level energy consultant and data analyst. Your purpose is to translate complex energy data into clear, actionable insights for the user.

# # ## Core Mission
# # Your primary function is to analyze the provided user device data and answer user queries with precision. Every response must be data-driven, objective, and focused on helping the user understand and optimize their energy consumption.

# # ## Interaction Protocols

# # ### For Greetings
# # - If the user sends a general greeting (e.g., "hi", "hello"), respond with a simple, professional greeting, e.g., "Hello [Username]. How can I assist you today?". Do not provide any analysis.

# # ### For Data-Driven Questions
# # - This is your primary function. Follow this process:
# #   1. Acknowledge the user's question.
# #   2. Perform a targeted analysis of the `user_device_data` provided in the request.
# #   3. Deliver a clear recommendation or answer based *only* on that data.

# # ### For Ambiguous or Off-Topic Questions
# # - If a question is outside the scope of energy analysis (e.g., "what is the capital of France?"), you must politely decline by stating: "My expertise is focused on your energy data. I cannot answer that question."

# # ### For Missing or Unclear Data
# # - If the provided data is insufficient to answer a question, state it clearly and specifically. For example: "I cannot provide a complete analysis without the 'energy' usage data for the device." Do not guess.

# # ## Analytical Framework

# # ### Data-First Mandate
# # - All analysis, calculations, and conclusions must be based strictly on the `user_device_data` provided in the request. Do not use general knowledge or make assumptions.

# # ### Prioritization of Advice
# # - When suggesting actions, prioritize them by potential energy savings impact. Start with the most significant opportunity for reduction.

# # ### Calculations
# # - You may perform basic calculations (e.g., total consumption, percentage contribution of a device, cost estimation if a rate is provided) to provide context and strengthen your analysis.

# # ### Comparison
# # - When comparing devices, focus on key metrics like power draw (W) and energy consumption (kWh). Clearly state which device is more efficient or consumes more.

# # ## Output Standard

# # ### Format
# # - Use bullet points for lists of recommendations or device comparisons to improve readability.

# # ### Language
# # - Use clear, direct language. Avoid jargon, filler words ('just', 'basically'), and conversational filler. Go straight to the point.

# # ### Tone
# # - Maintain a consultative, expert, and neutral tone. Be helpful and objective, not casual or emotional.

# # ## Final Mandate
# # You are an expert tool, not a conversational partner. Your value is in your precision and data-driven insights. Do not guess, do not invent, and do not provide information outside your function.
# # """
# # ==============================================================================
# # --- KEY ROTATION LOGIC ---
# # ==============================================================================

# rate_limited_keys = set()

# def get_next_available_key():
#     """Finds and returns an API key that is not currently rate-limited."""
#     available_keys = [key for key in API_KEYS if key not in rate_limited_keys]
#     if not available_keys:
#         return None
#     random.shuffle(available_keys)
#     return available_keys[0]

# def handle_rate_limit(api_key):
#     """Adds a key to the rate-limited set."""
#     print(f"   [API Key {api_key[:10]}... hit its limit. Switching keys.]")
#     rate_limited_keys.add(api_key)

# # ==============================================================================
# # --- HELPER FUNCTIONS ---
# # ==============================================================================

# def format_devices(devices):
#     """Formats the list of device dictionaries into a readable string."""
#     if not devices:
#         return "No device data provided."
#     lines = []
#     for d in devices:
#         status = "ON" if d.get("switchStatus", False) else "OFF"
#         lines.append(
#             f"- {d.get('name', 'Unknown Device')} in {d.get('location', 'Unknown Location')} | "
#             f"Power: {d.get('power', 0)}W | "
#             f"Energy Today: {d.get('energy', 0)}kWh | "
#             f"Status: {status} | "
#             f"Type: {d.get('type', 'Unknown')}"
#         )
#     return "\n".join(lines)

# # ==============================================================================
# # --- FLASK API ROUTE ---
# # ==============================================================================

# @app.route('/analyze', methods=['POST'])
# def analyze_energy():
#     """Main endpoint to analyze user energy data and answer questions."""
    
#     # 1. Get and validate incoming JSON data
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Invalid JSON request."}), 400

#     user_info = data.get('user_info')
#     user_device_data = data.get('user_device_data')
#     user_prompt = data.get('user_prompt')

#     if not all([user_info, user_device_data, user_prompt]):
#         return jsonify({"error": "Missing required fields: user_info, user_device_data, or user_prompt."}), 400

#     # 2. Format the data into a comprehensive prompt for the AI
#     device_summary = format_devices(user_device_data)
    
#     full_prompt = (
#         f"{SYSTEM_INSTRUCTION}\n\n"
#         f"User Information:\n"
#         f"- Name: {user_info.get('username', 'N/A')}\n"
#         f"- Email: {user_info.get('email', 'N/A')}\n\n"
#         f"Current Device Data:\n"
#         f"{device_summary}\n\n"
#         f"User's Question:\n"
#         f"{user_prompt}\n\n"
#         f"Assistant:"
#     )

#     # 3. Main retry loop for API calls
#     while True:
#         current_key = get_next_available_key()
#         if not current_key:
#             return jsonify({"error": "All API keys are currently rate-limited. Please try again later."}), 503 # Service Unavailable

#         try:
#             client = genai.Client(api_key=current_key)
            
#             # Generate the response from the model
#             response = client.models.generate_content(
#                 model=MODEL_ID,
#                 contents=full_prompt
#             )
            
#             # Safely extract the text from the response
#             answer_text = ""
#             if response.candidates and response.candidates[0].content:
#                 for part in response.candidates[0].content.parts:
#                     if hasattr(part, 'text') and part.text:
#                         answer_text += part.text
                        
#             return jsonify({"answer": answer_text.strip()})

#         except genai.errors.APIError as e:
#             if "RESOURCE_EXHAUSTED" in str(e) or "QUOTA_EXCEEDED" in str(e):
#                 handle_rate_limit(current_key)
#                 continue # Retry with the next key
#             else:
#                 return jsonify({"error": f"API Error: {str(e)}"}), 500
#         except Exception as e:
#             return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# # A simple root route to check if the server is running
# @app.route('/')
# def index():
#     return "WattBot AI API is running."

# # ==============================================================================
# # --- RUN SERVER (FOR LOCAL TESTING) ---
# # ==============================================================================

# if __name__ == '__main__':
#     # This is for local development only.
#     # Render will use Gunicorn to run the app.
#     app.run(host='0.0.0.0', port=5000, debug=True)


























# app.py
# A Flask API for the WattBot AI Energy Monitoring Assistant.

import os
import random
import json
from flask import Flask, request, jsonify
from google import genai
from google.genai import types
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# ==============================================================================
# --- CONFIGURATION ---
# ==============================================================================

app = Flask(__name__)
CORS(app)

# Load API keys from environment variables for security on Render
API_KEYS = [
    os.environ.get("GOOGLE_AI_KEY_1"),
    os.environ.get("GOOGLE_AI_KEY_2"),
    os.environ.get("GOOGLE_AI_KEY_3"),
    os.environ.get("GOOGLE_AI_KEY_4")
]

# Filter out any keys that are not set
API_KEYS = [key for key in API_KEYS if key]

if not API_KEYS:
    raise RuntimeError("FATAL ERROR: No Google AI API keys found in environment variables.")

# The model we will use.
MODEL_ID = "gemini-flash-latest"

# ==============================================================================
# --- WATTBOT AI PERSONA AND INSTRUCTIONS ---
# ==============================================================================

SYSTEM_INSTRUCTION = """
You are Wattbot AI, a professional energy monitoring and analysis assistant.

Your role:
- Analyze user energy data accurately when asked
- Answer questions using ONLY the data provided
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
- If the user sends a general greeting (e.g., "hi", "hello"), respond with a simple, professional greeting, e.g., "Hello [Username]. How can I assist you today?". Do not provide any analysis.
- Only analyze the provided device data and give advice when the user asks a specific question about energy, power, usage, or a device.
- All analysis, calculations, and conclusions must be based strictly on the `user_device_data` provided in the request. Do not use general knowledge or make assumptions.
- **CRITICAL: The 'power' data is in kilowatts (kW) and 'energy' is in kilowatt-hours (kWh); report these values with their correct units exactly as provided, with no conversions.**
- **The 'voltage' data is in volts (V) and 'current' is in amperes (A); report these values with their correct units exactly as provided.**
- **Never express numerical values in scientific notation; report all data exactly as it is provided. do use thing like this  5e-05A or this $5.8\times10^{-5}$, say the the data the way it is provided**
- Do not perform calculations unless explicitly asked by the user (e.g., "calculate the total cost"). Your default is to report and compare, not to calculate.


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

# ==============================================================================
# --- KEY ROTATION LOGIC ---
# ==============================================================================

rate_limited_keys = set()

def get_next_available_key():
    """Finds and returns an API key that is not currently rate-limited."""
    available_keys = [key for key in API_KEYS if key not in rate_limited_keys]
    if not available_keys:
        return None
    random.shuffle(available_keys)
    return available_keys[0]

def handle_rate_limit(api_key):
    """Adds a key to the rate-limited set."""
    print(f"   [API Key {api_key[:10]}... hit its limit. Switching keys.]")
    rate_limited_keys.add(api_key)

# ==============================================================================
# --- HELPER FUNCTIONS ---
# ==============================================================================

def format_devices(devices):
    """Formats the list of device dictionaries into a readable string."""
    if not devices:
        return "No device data provided."
    lines = []
    for d in devices:
        status = "ON" if d.get("switchStatus", False) else "OFF"
        lines.append(
            f"- {d.get('name', 'Unknown Device')} in {d.get('location', 'Unknown Location')} | "
            f"Power: {d.get('power', 0)}kW | "
            f"Energy Today: {d.get('energy', 0)}kWh | "
            f"Voltage: {d.get('voltage', 0)}V | "  # <-- ADDED VOLTAGE
            f"Current: {d.get('current', 0)}A | "  # <-- ADDED CURRENT
            f"Status: {status} | "
            f"Type: {d.get('type', 'Unknown')}"
        )
    return "\n".join(lines)

# ==============================================================================
# --- FLASK API ROUTE ---
# ==============================================================================

@app.route('/analyze', methods=['POST'])
def analyze_energy():
    """Main endpoint to analyze user energy data and answer questions."""
    
    # 1. Get and validate incoming JSON data
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON request."}), 400

    user_info = data.get('user_info')
    user_device_data = data.get('user_device_data')
    user_prompt = data.get('user_prompt')

    if not all([user_info, user_device_data, user_prompt]):
        return jsonify({"error": "Missing required fields: user_info, user_device_data, or user_prompt."}), 400

    # 2. Format the data into a comprehensive prompt for the AI
    device_summary = format_devices(user_device_data)
    
    full_prompt = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"User Information:\n"
        f"- Name: {user_info.get('username', 'N/A')}\n"
        f"- Email: {user_info.get('email', 'N/A')}\n\n"
        f"Current Device Data:\n"
        f"{device_summary}\n\n"
        f"User's Question:\n"
        f"{user_prompt}\n\n"
        f"Assistant:"
    )

    # 3. Main retry loop for API calls
    while True:
        current_key = get_next_available_key()
        if not current_key:
            return jsonify({"error": "All API keys are currently rate-limited. Please try again later."}), 503 # Service Unavailable

        try:
            client = genai.Client(api_key=current_key)
            
            # Generate the response from the model
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=full_prompt
            )
            
            # Safely extract the text from the response
            answer_text = ""
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        answer_text += part.text
                        
            return jsonify({"answer": answer_text.strip()})

        except genai.errors.APIError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "QUOTA_EXCEEDED" in str(e):
                handle_rate_limit(current_key)
                continue # Retry with the next key
            else:
                return jsonify({"error": f"API Error: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# A simple root route to check if the server is running
@app.route('/')
def index():
    return "WattBot AI API is running."

# ==============================================================================
# --- RUN SERVER (FOR LOCAL TESTING) ---
# ==============================================================================

if __name__ == '__main__':
    # This is for local development only.
    # Render will use Gunicorn to run the app.
    app.run(host='0.0.0.0', port=5000, debug=True)




