import os
from pathlib import Path
import tempfile

from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor
from PIL import Image

# Create a temporary directory to store the code files.
# temp_dir = tempfile.TemporaryDirectory()
temp_dir = Path("coding")

# Create a local command line code executor.
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

code_writer_system_message = """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply 'TERMINATE' in the end when everything is done.
"""

# Create an agent with code executor configuration.
code_executor_agent = ConversableAgent(
    "code_executor_agent",
    system_message=code_writer_system_message,
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the local command line code executor.
    human_input_mode="NEVER",  # Always take human input for this agent for safety.
)

message_with_code_block = """This is a message with code block.
The code block is below:
```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_tesla_stock_data():
    # Define the ticker symbol for Tesla
    ticker_symbol = 'TSLA' 
    # Calculate the date range for the last 6 months\n    
    end_date = datetime.now()    
    start_date = end_date - timedelta(days=6*30)  
    # Approximate 6 months as 180 days\n    \n    
    # # Fetch the stock data using yfinance\n    
    tesla_data = yf.download(ticker_symbol, start=start_date, end=end_date)    
    # Print the data as a table\n    
    print(tesla_data)   
    # Save the data to a CSV file\n    
    tesla_data.to_csv('stocks.csv')
    # Call the function to fetch and display the data\n
    # 
fetch_tesla_stock_data()
```
This is the end of the message.
"""

message_with_code_block = """Write Python code to plot TSLA's and META's "
    "stock price gains YTD, and save the plot to a file named 'stock_gains.png'."""

# Generate a reply for the given code.
# reply = code_executor_agent.generate_reply(messages=[{"role": "user", "content": message_with_code_block}])
# print(reply)

import datetime

code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config={"config_list": [{"model": "gpt-4o-2", 
                                 "api_key": os.environ["AZURE_OPENAI_KEY"], 
                                 "base_url": os.environ["AZURE_OPENAI_ENDPOINT"],
                                 # "azure_deployment":"gpt-4o-2",
                                 "api_type":"azure",
                                 "api_version":"2024-10-21"
                                }],
                                "temperature": 0.0,
                                "cache_seed": 42
                },
    code_execution_config=False,  # Turn off code execution for this agent.
)

today = datetime.datetime.now().strftime("%Y-%m-%d")
chat_result = code_executor_agent.initiate_chat(
    code_writer_agent,
    message=f"Today is {today}. Write Python code to plot TSLA's and META's "
    "stock price gains YTD, and save the plot to a file named 'stock_gains.png'.",
    max_turns=5
)

print(chat_result)

#img = Image.open("C:\Code\agifoundation1\coding\plot_stock_gains.png")

# Display the image
#img.show()