import os
from dotenv import load_dotenv

load_dotenv()

# AssemblyAI Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# IBM Granite Configuration (only needed for summarization)
IBM_API_KEY = os.getenv("IBM_API_KEY")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")

# Only check AssemblyAI key when running transcription
if not ASSEMBLYAI_API_KEY:
    raise ValueError("Missing ASSEMBLYAI_API_KEY in .env file")

# Print loaded configuration
print("AssemblyAI Configuration loaded")
if IBM_API_KEY and IBM_PROJECT_ID:
    print("IBM Granite Configuration loaded")
