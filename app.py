import os
import time

from fastapi import FastAPI
import uvicorn
from utils.mock_llm import ask

app = FastAPI(title="My AI Agent")
START_TIME = time.time()


@app.get("/")
def root():
    return {"message": "Agent is running!", "environment": os.getenv("ENVIRONMENT", "development")}


@app.post("/ask")
async def ask_agent(question: str):
    return {"answer": ask(question)}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app="app:app", host="0.0.0.0", port=port)
