import os
from dotenv import load_dotenv

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not ASSEMBLYAI_API_KEY:
    raise ValueError("Missing ASSEMBLYAI_API_KEY in .env file")

print(f"API Key loaded: {ASSEMBLYAI_API_KEY[:5]}...")  # Show just first 5 chars
