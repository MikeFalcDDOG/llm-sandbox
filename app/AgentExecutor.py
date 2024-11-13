import os

#!/usr/bin/env python
from typing import List

from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langserve import add_routes

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm, workflow
from ddtrace import patch

# Enable the integration
LLMObs.enable(
    integrations_enabled=True, 
    ml_app="mf-sandbox", 
    api_key = os.environ.get("DD_API_KEY"),
    site = os.environ.get("DD_SITE"),
    agentless_enabled = True,
    env="prod",
    service="llm-sandbox"
)

patch(openai=True)
patch(langchain=True)

# 1. Load Retriever
def load_retriever():
    loader = WebBaseLoader(["https://secretdenver.com/foodie-bucket-list-denver/", "https://www.denver.org/food-drink/restaurants/", "https://denver.eater.com/maps/best-restaurants-denver-eater-38"])
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    vector = FAISS.from_documents(documents, embeddings)
    retriever = vector.as_retriever()
    return retriever
    

# 2. Create Tools
def load_tools(ret):
    retriever_tool = create_retriever_tool(
        ret,
        "denver_search",
        "For any questions about Denver, use this tool!",
    )
    search = TavilySearchResults()
    tools = [retriever_tool, search]
    return tools


# 3. Create Agent
@llm(model_name="gpt-3.5-turbo", name="invoke_llm", model_provider="openai")
def create_agent(tools):
    prompt = hub.pull("hwchase17/openai-functions-agent")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

ret = load_retriever()
tools = load_tools(ret)
agent_executor = create_agent(tools)


# 4. App definition
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

# 5. Adding chain route

# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.

class Input(BaseModel):
    input: str
    chat_history: List[BaseMessage] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "location"}},
    )


class Output(BaseModel):
    output: str

add_routes(
    app,
    agent_executor.with_types(input_type=Input, output_type=Output),
    path="/agent",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)