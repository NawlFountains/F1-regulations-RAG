import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-120b"
_client = None

def generate(messages, model=MODEL):
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = _client.chat.completions.create(model=model, messages=messages, temperature=0)
    return resp.choices[0].message.content