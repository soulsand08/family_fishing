import google.generativeai as genai
import os

GENAI_API_KEY = "AIzaSyAKIWk5UJAiiVGHeXwqm8nxp7IGec0cKNs"
genai.configure(api_key=GENAI_API_KEY)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
