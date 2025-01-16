from collections import defaultdict
import datetime
from pathlib import Path
import tempfile
import time
from typing import Sequence
import PyPDF2
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.code_executor import CodeBlock
from autogen_core import CancellationToken
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.ui import Console
from autogen.code_utils import extract_code
from autogen.code_utils import create_virtual_env
from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
import asyncio
import os
import venv
from bs4 import BeautifulSoup
from openai import AzureOpenAI
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import base64
import requests
import io

# Load .env file
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_VISION"), 
  api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),  
  api_version="2024-10-21"
)

model_name = "gpt-4o-2"

model_client = AzureOpenAIChatCompletionClient(model="gpt-4o",
                                               azure_deployment="gpt-4o-2", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21",
                                               temperature=0.0,
                                               seed=42,
                                               maz_tokens=4096)
work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)

def extract_code_tools(content: str) -> str:
    code_blocks = ""
    code_blocks = extract_code(content)
    print('Code blocks:', code_blocks)
    python_code = ""
    if code_blocks:
        print("Code blocks extracted:", code_blocks)
        #shell_commands = next(block[1] for block in code_blocks if block[0] == 'sh' or block[0] == 'bash' or block[0] == 'shell')
        #print(shell_commands)
        python_code = next(block[1] for block in code_blocks if block[0] == 'python')
        local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)
        result = local_executor.execute_code_blocks(
                code_blocks=[
                    CodeBlock(language="python", code=python_code),
                ],
                cancellation_token=CancellationToken(),
            )
        #print(result)
        print('Output of code: ' , result.output.strip())
    return code_blocks

async def main():

    st.set_page_config(page_title="CodeAgent", page_icon=":robot:")
    st.title("CodeAgent :robot:")
    st.write("An AI agent that can read and write code to solve programming problems.")
    work_dir = Path("coding")
    work_dir.mkdir(exist_ok=True)

    code_create = AssistantAgent(
        "CreateCodeAgent",
        description="Create code for the given task.",
        #tools=[extract_code_tools],
        model_client=model_client,
        system_message="""
        Create code for the given task. Create code in python and only respond code as output.
        Also add the necessary packages needed for the code to run.
        if there are data please save the output as csv file called stocks.csv.
        """,        
    )

    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination
    team = MagenticOneGroupChat([code_create], 
                                 model_client=model_client,
                                 termination_condition=termination, max_turns=1)
    
    # Extract the generated code
    query = "Write a Python function that to chat last 6 months of Tesla stock price using yfinance library and print as table."
    result = await Console(team.run_stream(task=query))
    last_message = result.messages
    # print('Code created:', last_message[-1].content)
    code_blocks = extract_code(last_message[-1].content)
    # print('Code blocks:', code_blocks)
    try:
        # print("Start")
        python_code = ""
        if code_blocks:
            print("Code blocks extracted:", code_blocks)
            #shell_commands = next(block[1] for block in code_blocks if block[0] == 'sh' or block[0] == 'bash' or block[0] == 'shell')
            #print(shell_commands)
            python_code = next(block[1] for block in code_blocks if block[0] == 'python')
            local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)
            result = await local_executor.execute_code_blocks(
                    code_blocks=[
                        CodeBlock(language="python", code=python_code),
                    ],
                    cancellation_token=CancellationToken(),
                )
            #print(result)
            print(result.output.strip())
    except Exception as e:
        print(e)

    
if __name__ == "__main__":
    asyncio.run(main())