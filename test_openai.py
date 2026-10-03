import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY not found")
    raise SystemExit(1)

client = OpenAI(api_key=api_key)

print("✅ OpenAI API key loaded")
print("✅ OpenAI client created successfully")
