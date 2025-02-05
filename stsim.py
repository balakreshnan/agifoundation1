import os
import asyncio
from typing import Any, Dict, List, Optional
from azure.ai.evaluation.simulator import Simulator
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool
# [START enable_tracing]
from openai import AzureOpenAI
from datetime import datetime
import streamlit as st
import datetime
from azure.ai.evaluation import BleuScoreEvaluator, GleuScoreEvaluator, RougeScoreEvaluator, MeteorScoreEvaluator, RougeType
from dotenv import load_dotenv

# Load .env file
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-10-21",
)

model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
}

def callopenai(query, messages_list, context):
    returntxt = ""

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"), #"gpt-4-turbo", # model = "deployment_name".
        messages=messages_list,
        temperature=0.0,
        top_p=0.0,
        seed=42,
        max_tokens=1000,
    )

    returntxt = response.choices[0].message.content
    return returntxt

async def callback(
    messages: Dict[str, List[Dict]],
    stream: bool = False,
    session_state: Any = None,
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    messages_list = messages["messages"]
    # Get the last message from the user
    latest_message = messages_list[-1]
    query = latest_message["content"]
    # Call your endpoint or AI application here
    # response should be a string
    response = callopenai(query, messages_list, context)
    formatted_response = {
        "content": response,
        "role": "assistant",
        "context": "",
    }
    messages["messages"].append(formatted_response)
    return {"messages": messages["messages"], "stream": stream, "session_state": session_state, "context": context}

simulator = Simulator(model_config=model_config)

# Simulate a conversation with a structured message

# Function to extract the latest assistant message
def get_latest_assistant_message(conversations):
    for conversation in reversed(conversations):  # Start from the latest conversation
        for message in reversed(conversation["messages"]):  # Look at messages in reverse order
            if message["role"] == "assistant":
                return message["content"]
    return None  # Return None if no assistant message is found

if __name__ == "__main__":
    # asyncio.run(callback)
    custom_simulator = Simulator(model_config=model_config)
    outputs = asyncio.run(custom_simulator(
        target=callback,
        conversation_turns=[
            [
                "Describe the 1983 cricket world cup with details on the players and their scores and highlights?",
            ],
            [
                "How do I simulate data against LLMs",
            ],
        ],
        max_conversation_turns=2,
    ))
    # print(outputs)
    # Extract and display the latest assistant message
    latest_message = get_latest_assistant_message(outputs)
    if latest_message:
        print("Latest Assistant Message:")
        print(latest_message)
    else:
        print("No assistant messages found.")
    with open("simulator_output.jsonl", "w") as f:
        for output in outputs:
            f.write(output.to_eval_qr_json_lines())