import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool
# [START enable_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from pprint import pprint
from azure.ai.evaluation import evaluate, AzureAIProject, AzureOpenAIModelConfiguration
from azure.ai.evaluation import ProtectedMaterialEvaluator, IndirectAttackEvaluator
from azure.ai.evaluation.simulator import AdversarialSimulator, AdversarialScenario, IndirectAttackSimulator
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
from mfgdata import extractmfgresults, extracttop5questions
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
        },
        azure_ai_project=azure_ai_project,
        output_path="./rsoutputmetrics.json",
    )
    # pprint(results)
    # parse_json(results)
    print("Done")

def main():
    with tracer.start_as_current_span(scenario):
        conn_list = project_client.connections.list()
        conn_id = ""
        for conn in conn_list:
            if conn.connection_type == "CognitiveSearch":
                print(f"Connection ID: {conn.id}")
                conn_id = conn.id

        ai_search = AzureAISearchTool(conn_id, "mfggptdata")
        #ai_search.add_index(conn_id, "mfggptdata")

        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="my-assistant",
            instructions="You are a helpful assistant",
            tools=ai_search.definitions,
            tool_resources = ai_search.resources,
        )
        print(f"Created agent, ID: {agent.id}")

        # Create a thread
        thread = project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")
        
        # Create a message
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="what are the personal protection i should consider in manufacturing?",
        )
        print(f"Created message, message ID: {message.id}")
            
        # Run the agent
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        print(f"Run finished with status: {run.status}")
        
        if run.status == "failed":
            # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")

        # Get messages from the thread 
        messages = project_client.agents.list_messages(thread_id=thread.id)
        # print(f"Messages: {messages}")
            
        assistant_message = ""
        for message in messages.data:
            if message["role"] == "assistant":
                assistant_message = message["content"][0]["text"]["value"]

        # Get the last message from the sender
        print(f"Assistant response: {assistant_message}")

        #now lets evaluate the output
        #evalmetrics()


if __name__ == "__main__":
    main()