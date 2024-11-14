import os

#!/usr/bin/env python
from typing import List, Union

from fastapi import FastAPI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langserve import add_routes

from ddtrace.llmobs import LLMObs
from ddtrace import patch

app = FastAPI()

# Enable the integration
LLMObs.enable(
    integrations_enabled=True,
    ml_app="mf-chatbot",
    api_key = os.environ.get("DD_API_KEY"),
    site = os.environ.get("DD_SITE"),
    agentless_enabled = True,
    env="prod",
    service="llm-chatbot"
)

patch(openai=True)
patch(langchain=True)

llmopenai = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant that recommends places to eat in denver. Please provide a concise answer for users seeking food options in Denver."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llmopenai | StrOutputParser()

def get_session_history():
    return InMemoryChatMessageHistory()

class InputChat(BaseModel):
    """Input for the chat endpoint."""

    messages: List[Union[HumanMessage, AIMessage, SystemMessage]] = Field(
        ...,
        description="The chat messages representing the current conversation.",
    )

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
).with_types(input_type=InputChat)

add_routes(
    app,
    chain_with_history,
    path="/chat",
    playground_type="default"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)