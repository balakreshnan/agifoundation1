import datetime
from typing import Sequence
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import asyncio
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import base64
import requests
import io
from mfgdata import extractmfgresults, extracttop5questions

# Load .env file
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_VISION"), 
  api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),  
  api_version="2024-10-21"
)

model_name = "gpt-4o-2"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def processimage(base64_image, imgprompt, model_name="gpt-4o-2"):
    response = client.chat.completions.create(
    model=model_name,
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": f"{imgprompt}"},
            {
            "type": "image_url",
            "image_url": {
                "url" : f"data:image/jpeg;base64,{base64_image}",
            },
            },
        ],
        }
    ],
    max_tokens=2000,
    temperature=0,
    top_p=1,
    seed=105,
    )

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

# Note: This example uses mock tools instead of real APIs for demonstration purposes
def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
        Udonis Haslem: 844 points
        Dwayne Wade: 1397 points
        James Posey: 550 points
        ...
        """
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."

def mfg_compl_data(query: str) -> str:
    return extractmfgresults(query)


model_client = AzureOpenAIChatCompletionClient(model="gpt-4o", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21")

async def mfg_response(query):

    returntxt = ""

    planning_agent = AssistantAgent(
        "PlanningAgent",
        description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
        model_client=model_client,
        system_message="""
        You are a planning agent.
        Your job is to break down complex tasks into smaller, manageable subtasks.
        Your team members are:
            Web search agent: Searches for information
            Manufacturing Industry analyst: You are Manufacturing Complaince, OSHA, CyberSecurity AI agent

        You only plan and delegate tasks - you do not execute them yourself.
        Also pick the right team member to use for the task.

        When assigning tasks, use this format:
        1. <agent> : <task>

        After all tasks are complete, summarize the findings and end with "TERMINATE".
        Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
        """,
    )

    web_search_agent = AssistantAgent(
        "WebSearchAgent",
        description="A web search agent.",
        tools=[search_web_tool],
        model_client=model_client,
        system_message="""
        You are a web search agent.
        Your only tool is search_tool - use it to find information.
        You make only one search call at a time.
        Once you have the results, you never do calculations based on them.
        """,
    )

    mfg_ind_analyst_agent = AssistantAgent(
        "DataAnalystAgent",
        description="A Manufacturing Complaince, OSHA, CyberSecurity AI agent. Data source is stored in AI Search to get grounded information.",
        model_client=model_client,
        tools=[mfg_compl_data],
        system_message="""
        You are Manufacturing Complaince, OSHA, CyberSecurity AI agent. Be politely, and provide positive tone answers.
        Based on the question do a detail analysis on information and provide the best answers.
        Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
        """,
    )

    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    model_client_mini = AzureOpenAIChatCompletionClient(model="gpt-4o", 
                                                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                                api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                                api_version="2024-10-21")

    team = SelectorGroupChat(
        [planning_agent, web_search_agent, mfg_ind_analyst_agent],
        model_client=model_client_mini,
        termination_condition=termination,
    )

    result = await Console(team.run_stream(task=query))
    #print(result)  # Process the result or output here
    # Extract and print only the message content
    returntxt = ""
    returntxtall = ""
    for message in result.messages:
        # print('inside loop - ' , message.content)
        returntxt = str(message.content)
        returntxtall += str(message.content) + "\n"

    return returntxt, returntxtall
        

def mfgagents():
    count = 0
    temp_file_path = ""
    rfttopics = ""

    #tab1, tab2, tab3, tab4 = st.tabs('RFP PDF', 'RFP Research', 'Draft', 'Create Word')
    modeloptions1 = ["gpt-4o-2", "gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo"]
    imgfile = "temp1.jpg"
    # Create a dropdown menu using selectbox method
    selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
    count += 1
    # user_input = st.text_input("Enter the question to ask the AI model", "what are the personal protection i should consider in manufacturing?")
    if prompt := st.chat_input("what are the personal protection i should consider in manufacturing?", key="chat1"):
        # Call the extractproductinfo function
        #st.write("Searching for the query: ", prompt)
        st.chat_message("user").markdown(prompt, unsafe_allow_html=True)
        #st.session_state.chat_history.append({"role": "user", "message": prompt})
        starttime = datetime.datetime.now()
        result = asyncio.run(mfg_response(prompt))
        rfttopics, agenthistory = result
        endtime = datetime.datetime.now()
        #st.markdown(f"Time taken to process: {endtime - starttime}", unsafe_allow_html=True)
        rfttopics += f"\n Time taken to process: {endtime - starttime}"
        #st.session_state.chat_history.append({"role": "assistant", "message": rfttopics})
        st.chat_message("assistant").markdown(rfttopics, unsafe_allow_html=True)