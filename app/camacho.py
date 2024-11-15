from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import uvicorn

from ddtrace.llmobs import LLMObs

# Enable the integration
LLMObs.enable(
    integrations_enabled=True,
    ml_app="mf-sandbox",
    api_key = os.environ.get("DD_API_KEY"),
    site = os.environ.get("DD_SITE"),
    agentless_enabled = True,
    env="prod",
    service="CAMACHO CHAT"
)

# Initialize FastAPI
app = FastAPI()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define a simple in-memory conversation state
conversation_history = []

# Add CORS middleware before defining any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Pydantic model for request and response
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# Endpoint for chat messages
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.message

    # Update conversation history with user's message
    conversation_history.append({"role": "user", "content": user_message})

    try:
        # Generate response from OpenAI's model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are President Camacho from Idiocracy. Respond in character."},
                *conversation_history
            ]
        )

        # Extract the response content
        camacho_response = response.choices[0].message['content'].strip()

        # Update conversation history with AI's response
        conversation_history.append({"role": "assistant", "content": camacho_response})

        # Return the response to the client
        return ChatResponse(reply=camacho_response)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response from President Camacho")


# Optional endpoint to clear the conversation history
@app.post("/reset")
async def reset_conversation():
    global conversation_history
    conversation_history = []
    return {"status": "Conversation history reset"}


# Entry point to run the app with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
