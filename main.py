import os
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

from indexer import build_index, search

load_dotenv()

app = FastAPI()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

class Query(BaseModel):
    message: str

is_ready = False

def run_index():
    global is_ready
    try:
        build_index()
        is_ready = True
        print("✅ Index ready")
    except Exception as e:
        print("❌ Index failed:", e)

@app.on_event("startup")
def startup_event():
    print("🚀 Server started")
    thread = threading.Thread(target=run_index)
    thread.start()

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/chat")
def chat(query: Query):
    global is_ready

    if not is_ready:
        return {"response": "⏳ Loading documents, please wait..."}

    results = search(query.message)

    if not results:
        return {"response": "❌ Not available in knowledge base"}

    context = "\n\n".join([
        f"{r['name']}:\n{r['content'][:800]}"
        for r in results
    ])

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=400,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": f"""
You are a smart enterprise assistant.

RULES:
- Answer ONLY from context
- No hallucination
- Be concise

FORMAT:
1. Summary
2. Bullet points
3. Sources

Context:
{context}

Question:
{query.message}
"""
            }
        ]
    )

    answer = response.content[0].text

    sources = "\n\n📄 Sources:\n" + "\n".join([f"• {r['name']}" for r in results])

    return {"response": answer + sources}