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
from azure.ai.evaluation import ProtectedMaterialEvaluator, IndirectAttackEvaluator
from azure.ai.evaluation import evaluate, AzureAIProject, AzureOpenAIModelConfiguration, F1ScoreEvaluator
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
from azure.ai.evaluation import BleuScoreEvaluator, GleuScoreEvaluator, RougeScoreEvaluator, MeteorScoreEvaluator, RougeType
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
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-10-21",
)

model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Function to parse the JSON data
def parse_json(data):
    # Print Relevance Score
    print(f"Overall GPT Relevance: {data.get('relevance.gpt_relevance', 'N/A')}")
    
    # Print Rows
    rows = data.get('rows', [])
    print("\nRows:")
    for row in rows:
        context = row.get('inputs.context')
        query = row.get('inputs.query')
        response = row.get('inputs.response')
        output = row.get('outputs.output')
        relevance = row.get('outputs.relevance.gpt_relevance')
        
        print(f"Context: {context}")
        print(f"Query: {query}")
        print(f"Response: {response}")
        print(f"Output: {output}")
        print(f"Relevance: {relevance}")
        print("-" * 50)
# Bing Search Configuration
BING_API_KEY = os.getenv("BING_KEY")

def bing_search(query: str):
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3}
    response = requests.get(endpoint, headers=headers, params=params)
    return [result["snippet"] for result in response.json().get("webPages", {}).get("value", [])]

def evalmetrics():
    
    # Load .env file
    # load_dotenv()
    #citationtxt = extractrfpresults("Provide summary of Resources for Railway projects with 200 words?")

    #print('Citation Text:', citationtxt)
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    model_config = {
        "azure_endpoint": azure_endpoint,
        "api_key": api_key,
        "azure_deployment": azure_deployment,
        "api_version": api_version,
    }


    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        print(ex)

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group_name = os.getenv("AZURE_RESOURCE_GROUP")
    project_name = os.getenv("AZUREAI_PROJECT_NAME")
    print(subscription_id, resource_group_name, project_name)
    azure_ai_project = AzureAIProject(subscription_id=subscription_id, 
                                      resource_group_name=resource_group_name, 
                                      project_name=project_name, 
                                      azure_crendential=credential)
    
    azure_ai_project_dict = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "project_name": project_name,
        "azure_credential": credential
    }
    
    # prompty_path = os.path.join("./", "rfp.prompty")
    content_safety_evaluator = ContentSafetyEvaluator(azure_ai_project=azure_ai_project_dict, credential=credential)
    relevance_evaluator = RelevanceEvaluator(model_config)
    coherence_evaluator = CoherenceEvaluator(model_config)
    groundedness_evaluator = GroundednessEvaluator(model_config)
    fluency_evaluator = FluencyEvaluator(model_config)
    # similarity_evaluator = SimilarityEvaluator(model_config)
    f1_evaluator = F1ScoreEvaluator()
    bleu_evaluator = BleuScoreEvaluator()
    gleu_evaluator = GleuScoreEvaluator()
    meteor_evaluator = MeteorScoreEvaluator(alpha=0.8)
    rouge_evaluator = RougeScoreEvaluator(rouge_type=RougeType.ROUGE_4)

    results = evaluate(
        evaluation_name="rfpevaluation",
        data="datarfp.jsonl",
        target=extractmfgresults,
        #evaluators={
        #    "relevance": relevance_evaluator,
        #},
        #evaluator_config={
        #    "relevance": {"response": "${target.response}", "context": "${data.context}", "query": "${data.query}"},
        #},
        evaluators={
            "content_safety": content_safety_evaluator,
            "coherence": coherence_evaluator,
            "relevance": relevance_evaluator,
            "groundedness": groundedness_evaluator,
            "fluency": fluency_evaluator,
        #    "similarity": similarity_evaluator,
            "f1": f1_evaluator,
            "bleu": bleu_evaluator,
            "gleu": gleu_evaluator,
            "meteor": meteor_evaluator,
            "rouge": rouge_evaluator,
        },        
        evaluator_config={
            "content_safety": {"query": "${data.query}", "response": "${target.response}"},
            "coherence": {"response": "${target.response}", "query": "${data.query}"},
            "relevance": {"response": "${target.response}", "context": "${data.context}", "query": "${data.query}"},
            "groundedness": {
                "response": "${target.response}",
                "context": "${data.context}",
                "query": "${data.query}",
            },
            "fluency": {"response": "${target.response}", "context": "${data.context}", "query": "${data.query}"},
            "similarity": {"response": "${target.response}", "context": "${data.context}", "query": "${data.query}"},
            "f1": {"response": "${target.response}", "ground_truth": "${data.ground_truth}"},
            "bleu": {"response": "${target.response}", "ground_truth": "${data.ground_truth}"},
            "gleu": {"response": "${target.response}", "ground_truth": "${data.ground_truth}"},
            "meteor": {"response": "${target.response}", "ground_truth": "${data.ground_truth}"},
            "rouge": {"response": "${target.response}", "ground_truth": "${data.ground_truth}"},
        },
        azure_ai_project=azure_ai_project,
        output_path="./rsoutputmetrics.json",
    )
    # pprint(results)
    # parse_json(results)
    print("Done")

def classify_query(user_query: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"), 
        messages=[
            {
                "role": "system",
                "content": """
                Classify the user's query into one of these categories:
                - "rag": Requires internal/structured data (e.g., company docs, private databases).
                - "bing": Requires real-time/public web data (e.g., news, trends, external facts).
                Respond ONLY with "rag" or "bing".
                """
            },
            {"role": "user", "content": user_query}
        ],
        temperature=0.0,
        top_p=0.0,
        seed=42,
        max_tokens=50,
    )
    return response.choices[0].message.content.strip().lower()

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def processagents(prompt):
    returntxt = ""

    with tracer.start_as_current_span(scenario):
        conn_list = project_client.connections.list()
        conn_id = ""
        for conn in conn_list:
            if conn.connection_type == "CognitiveSearch":
                # print(f"Connection ID: {conn.id}")
                conn_id = conn.id

        print(f"Connection ID: {conn_id}")
        ai_search = AzureAISearchTool(conn_id, "mfggptdata")
        # ai_search.add_index(conn_id, "mfggptdata")

        #print('AI Search:', ai_search)
        # Debugging and validation logic for ai_search.definitions and ai_search.resources
        print("AI Search Definitions:")
        pprint(ai_search.definitions)

        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="mfgcompliance-agent",
            instructions=f"""You are Manufacturing Complaince, OSHA, CyberSecurity AI agent. Be politely, and provide positive tone answers.
            Based on the question do a detail analysis on information and provide the best answers.

            Only answer from tools provided. 
            Data Source: Azure AI Search.
            Please provide Citation and References for the answers as url. [url1] [url2].

            Respond back as markdown format only Show all links as hyperlinks.
            """,
            tools=ai_search.definitions,
            tool_resources = ai_search.resources,
            headers={"x-ms-enable-preview": "true"},
        )
        print(f"Created agent, ID: {agent.id}")

         # Create the Bing Assistant
        # bing_assistant = project_client.agents.create_agent(
        #     model="gpt-4o",
        #     name="Bing Search Agent",
        #     instructions="Use Bing Search to find real-time web results. Please provide Citation and References for the answers as url.",
        #     tools=[{"type": "function", "function": {
        #         "name": "bing_search",
        #         "description": "Search Bing for up-to-date web results",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {"query": {"type": "string"}},
        #             "required": ["query"]
        #         }
        #     }}]
        # )

        # orchestrator = project_client.agents.create_agent(
        #     name="Orchestrator",
        #     instructions=f"""Coordinate between Azure AI Search and Bing agents. Combine results for final answers.
        #     Please provide Citation and References for the answers as url.""",
        #     model="gpt-4o"
        # )

        # Create a thread
        thread = project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        # bingthread = project_client.agents.create_thread()
        # print(f"Created thread, thread ID: {bingthread.id}")
        
        # Create a message
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        print(f"Created message, message ID: {message.id}")

        # bingmessage = project_client.agents.create_message(
        #     thread_id=bingthread.id,
        #     role="user",
        #     content=prompt
        # )

        # print(f"Created message, message ID: {bingmessage.id}")
            
        # Run the agent
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        print(f"Run finished with status: {run.status}")
        
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
            if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run")
                    project_client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                # tool_outputs = []
                # for tool_call in tool_calls:
                #     if isinstance(tool_call, RequiredFunctionToolCall):
                #         try:
                #             print(f"Executing tool call: {tool_call}")
                #             output = functions.execute(tool_call)
                #             tool_outputs.append(
                #                 ToolOutput(
                #                     tool_call_id=tool_call.id,
                #                     output=output,
                #                 )
                #             )
                #         except Exception as e:
                #             print(f"Error executing tool_call {tool_call.id}: {e}")

                # print(f"Tool outputs: {tool_outputs}")
                # if tool_outputs:
                #     project_client.agents.submit_tool_outputs_to_run(
                #         thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                #     )

        if run.status == "failed":
            # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")

        # Get messages from the thread 
        messages = project_client.agents.list_messages(thread_id=thread.id)
        # print(f"Messages: {messages}")

                  
        assistant_message = ""
        content = ""
        for message in messages.data:
            if message["role"] == "assistant":
                assistant_message = message["content"][0]["text"]["value"]
        
        print('messages:', messages)    

        # Filter messages from the assistant
        #assistant_messages = [msg for msg in messages if msg["role"] == 'assistant']
        #last_assistant_message = assistant_messages[-1].content
        # last_assistant_message = message.data[-1].content[-1].text.value
        # Extract the assistant messages
        assistant_messages = [msg for msg in messages['data'] if msg['role'] == 'assistant']

        # Get the last assistant message
        if assistant_messages:
            last_assistant_message = assistant_messages[-1]
            content = last_assistant_message['content'][0]['text']['value']
            print("Last assistant message content:")
            print(content)
        else:
            print("No assistant messages found.")

        if content:
            returntxt = content

        # Get the last message from the sender
        print(f"Assistant response: {assistant_message}")

        # # Run the Bing agent
        # bing_response = project_client.agents.create_and_process_run(thread_id=bingthread.id, assistant_id=bing_assistant.id)
        # print(f"Run finished with status: {bing_response.status}")
        
        # if bing_response.status == "failed":
        #     # Check if you got "Rate limit is exceeded.", then you want to get more quota
        #     print(f"Run failed: {bing_response.last_error}")

        # # Get messages from the thread 
        # bingmessages = project_client.agents.list_messages(thread_id=bingthread.id)
        # # print(f"Messages: {bingmessages}")
                  
        # bing_message = ""
        # bingcontent = ""
        # for message in bingmessages.data:
        #     if message["role"] == "assistant":
        #         bing_message = message["content"][0]["text"]["value"]
        
        # print('messages:', bingmessages)    

        # # Extract the assistant messages
        # bing_message = [msg for msg in bingmessages['data'] if msg['role'] == 'assistant']

        # # Get the last assistant message
        # if bing_message:
        #     last_assistant_message = bing_message[-1]
        #     bingcontent = last_assistant_message['content'][0]['text']['value']
        #     print("Last assistant message content:")
        #     print(bingcontent)
        # else:
        #     print("No assistant messages found.")

        # #if bingcontent:
        # #    returntxt = bingcontent

        # # Get the last message from the sender
        # print(f"Assistant response: {bing_message}")
        # print(f"Assistant response: {bingcontent}")

    return returntxt

def showagents():
    st.title("Azure AI Foundry Agents")

    if prompt := st.chat_input("what are the personal protection i should consider in manufacturing?", key="chat1"):
        st.chat_message("user").markdown(prompt, unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "user", "message": prompt})
        starttime = datetime.datetime.now()
        results = processagents(prompt)
        endtime = datetime.datetime.now()

        #st.markdown(f"Time taken to process: {endtime - starttime}", unsafe_allow_html=True)
        results += f"\n Time taken to process: {endtime - starttime}"
        # st.session_state.chat_history.append({"role": "assistant", "message": results + "\n" + bingcontent})
        st.session_state.chat_history.append({"role": "assistant", "message": results})
        st.chat_message("assistant").markdown(results, unsafe_allow_html=True)

        # Keep only the last 10 messages
        if len(st.session_state.chat_history) > 20:  # 10 user + 10 assistant
            st.session_state.chat_history = st.session_state.chat_history[-20:]

if __name__ == "__main__":
    showagents()
    # evalmetrics()