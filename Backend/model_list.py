from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Checking available models for your key...")
try:
    for model in client.models.list():
        # This will print the exact name you need to use in your code
        print(f"Model ID: {model.name}")
except Exception as e:
    print(f"Error: {e}")