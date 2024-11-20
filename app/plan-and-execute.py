import os
from fastapi import FastAPI, Request
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableSequence

from ddtrace.llmobs import LLMObs

app = FastAPI()

# Enable the integration
LLMObs.enable(
    integrations_enabled=True,
    ml_app="mf-sandbox",
    api_key = os.environ.get("DD_API_KEY"),
    site = os.environ.get("DD_SITE"),
    agentless_enabled = True,
    env="prod",
    service="llm-plan-and-execute"
)

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define Prompts
planning_prompt = PromptTemplate(
    input_variables=["task"],
    template="Break down the following task into subtasks:\n\nTask: {task}\n\nSubtasks:"
)

execution_prompt = PromptTemplate(
    input_variables=["subtasks"],
    template="Execute the following subtasks step by step:\n\nSubtasks: {subtasks}\n\nResults:"
)

# Define the pipeline with RunnableSequence
plan_and_execute_chain = RunnableSequence(
    planning_prompt | llm,
    execution_prompt | llm
)

@app.post("/planandexecute/")
async def plan_and_execute_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    if not user_input:
        return {"error": "Input required"}

    try:
        # Run the chain with the user input
        result = plan_and_execute_chain.invoke({"task": user_input})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
