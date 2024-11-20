from dotenv import load_dotenv
import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load .env file
load_dotenv()


# Create an AI Project Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_basics_with_console_tracing.py

def main():
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.getenv("PROJECT_CONNECTION_STRING"),
    )
    # print("Project connection string loaded", os.getenv("PROJECT_CONNECTION_STRING"))
    # [START enable_tracing]
    from opentelemetry import trace
    from azure.monitor.opentelemetry import configure_azure_monitor
    # Enable Azure Monitor tracing
    application_insights_connection_string = project_client.telemetry.get_connection_string()
    # print(f"Application Insights connection string: {application_insights_connection_string}")
    if not application_insights_connection_string:
        print("Application Insights was not enabled for this project.")
        print("Enable it via the 'Tracing' tab in your AI Studio project page.")
        exit()
    configure_azure_monitor(connection_string=application_insights_connection_string)

    scenario = os.path.basename(__file__)
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(scenario):
        with project_client:

            # [END enable_tracing]
            agent = project_client.agents.create_agent(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"), name="my-assistant", instructions="You are helpful assistant",
                temperature=0.0, top_p=1
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = project_client.agents.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = project_client.agents.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

            # poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(1)
                run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

                print(f"Run status: {run.status}")

            project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = project_client.agents.list_messages(thread_id=thread.id)
            print(f"messages: {messages}")

if __name__ == "__main__":
    main()