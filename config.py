import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not all([OPENAI_API_KEY, ASSEMBLYAI_API_KEY]):
    raise ValueError("Missing required API keys in .env file")

print(f"API Key loaded: {OPENAI_API_KEY[:5]}...")  # Show just first 5 chars
