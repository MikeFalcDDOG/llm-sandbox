from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import uvicorn

from ddtrace.llmobs import LLMObs

# enable the integration
LLMObs.enable(
    integrations_enabled=True,
    ml_app="mf-sandbox",
    api_key = os.environ.get("DD_API_KEY"),
    site = os.environ.get("DD_SITE"),
    agentless_enabled = True,
    env="prod",
    service="CAMACHO CHAT"
)

# initialize FastAPI
app = FastAPI()

# get key from env var
openai.api_key = os.getenv("OPENAI_API_KEY")

# track state of convo
conversation_history = []

# CORS middleware before defining any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# endpoint for chat messages
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.message

    conversation_history.append({"role": "user", "content": user_message})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are President Camacho from Idiocracy. Respond in character. You are not allowed to break character."},
                *conversation_history
            ]
        )

        camacho_response = "\u200B\n\n" + response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": camacho_response})

        return ChatResponse(reply=camacho_response)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response from President Camacho")


# clear the conversation history
@app.post("/reset")
async def reset_conversation():
    global conversation_history
    conversation_history = []
    return {"status": "Conversation history reset"}


# run with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
