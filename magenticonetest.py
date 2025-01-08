import asyncio
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_agentchat.ui import Console
import os

from dotenv import load_dotenv
# Load .env file
load_dotenv()


async def main() -> None:
    #model_client = OpenAIChatCompletionClient(model="gpt-4o")
    model_client = AzureOpenAIChatCompletionClient(model="gpt-4o", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21")

    assistant = AssistantAgent(
        "Assistant",
        model_client=model_client,
    )
    surfer = MultimodalWebSurfer(
        "WebSurfer",
        model_client=model_client,
    )
    team = MagenticOneGroupChat([surfer], model_client=model_client)
    #await Console(team.run_stream(task="Provide a different proof for Fermat's Last Theorem"))
    await Console(team.run_stream(task="What is the UV index in delhi today?"))


asyncio.run(main())