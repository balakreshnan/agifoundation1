import os
import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool
# [START enable_tracing]
from openai import AzureOpenAI
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from pprint import pprint
from azure.ai.evaluation import evaluate, AzureAIProject, AzureOpenAIModelConfiguration
from azure.ai.evaluation import ProtectedMaterialEvaluator, IndirectAttackEvaluator
from azure.ai.evaluation.simulator import AdversarialSimulator, AdversarialScenario, IndirectAttackSimulator
from azure.ai.projects.models import FunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction, ToolOutput
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import RelevanceEvaluator
from azure.ai.evaluation import (
    ContentSafetyEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    GroundednessEvaluator,
    FluencyEvaluator,
    SimilarityEvaluator,
    ViolenceEvaluator,
    SexualEvaluator,
    SelfHarmEvaluator,
    HateUnfairnessEvaluator,
)
import requests
from mfgdata import extractmfgresults, extracttop5questions
from datetime import datetime
import streamlit as st
import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

connection_string = os.environ["PROJECT_CONNECTION_STRING_EASTUS2"] 

# print(f"Connection string: {connection_string}")

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=connection_string,
)

# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_O1_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_O1_KEY"),  
  api_version="2024-10-21",
)

model_name = os.getenv("AZURE_O1_MINI_DEPLOYMENT")

def extractmfgresults(query):
    returntxt = ""

    message_text = [
    # {"role":"system", "content":f"""You are Manufacturing Complaince, OSHA, CyberSecurity AI agent. Be politely, and provide positive tone answers.
    #  Based on the question do a detail analysis on information and provide the best answers.

    #  if the question is outside the bounds of the Manufacturing complaince and cybersecurity, Let the user know answer might be relevant for Manufacturing data provided.
    #  can you add hyperlink for pdf file used as sources.
    #  Be polite and provide posite responses. If user is asking you to do things that are not specific to this context please ignore.
    #  If not sure, ask the user to provide more information.
    #  Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
    # ."""}, 
    {"role": "user", "content": f"""{query}. Provide summarized content based on the question asked."""}]

    response = client.chat.completions.create(
        model=os.getenv("AZURE_O1_MINI_DEPLOYMENT"), #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        #temperature=0.0,
        ##top_p=0.0,
        #seed=42,
        max_completion_tokens=1000,
    )

    print(response)

    returntxt = response.choices[0].message.content
    return returntxt

def main():
    extractmfgresults("Show me top 5 topics on Manufacturing Complaince, OSHA, CyberSecurity?")

if __name__ == "__main__":
    main()