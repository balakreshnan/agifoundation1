import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference.models import UserMessage
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load .env file
load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.getenv("PROJECT_CONNECTION_STRING"),
)

connections = project_client.connections.list()
for connection in connections:
    print(connection)

# inference_client = project_client.inference.get_chat_completions_client()

# response = inference_client.complete(
#     model="gpt-4o-2", # Model deployment name
#     #connection="aoaieu1",
#     messages=[UserMessage(content="How many feet are in a mile?")]
# )

# print(response.choices[0].message.content)

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
# model_deployment_name = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
model_deployment_name = "gpt-4o-2024-08-06"

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    # Enable Azure Monitor tracing
    application_insights_connection_string = project_client.telemetry.get_connection_string()
    if not application_insights_connection_string:
        print("Application Insights was not enabled for this project.")
        print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
        exit()

    # Enable additional instrumentations for openai and langchain
    # which are not included by Azure Monitor out of the box
    project_client.telemetry.enable()
    configure_azure_monitor(connection_string=application_insights_connection_string)

    # Get an authenticated OpenAI client for your default Azure OpenAI connection:
    with project_client.inference.get_azure_openai_client(api_version="2024-10-21") as client:
        print("Authenticated to Azure OpenAI.", client.models.list())

        response = client.chat.completions.create(
            model=model_deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": "How many feet are in a mile?",
                },
            ],
        )

        print(response.choices[0].message.content)