from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Checking available embedding models...")
for m in client.models.list():
    if "embedContent" in m.supported_actions:
        print(f"✅ Available: {m.name}")