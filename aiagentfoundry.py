import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool
from dotenv import load_dotenv

# Load .env file
load_dotenv()

connection_string = os.environ["PROJECT_CONNECTION_STRING_EASTUS2"] 

print(f"Connection string: {connection_string}")

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=connection_string,
)

def main():
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
    print(f"Messages: {messages}")
        
    assistant_message = ""
    for message in messages.data:
        if message["role"] == "assistant":
            assistant_message = message["content"][0]["text"]["value"]

    # Get the last message from the sender
    print(f"Assistant response: {assistant_message}")

if __name__ == "__main__":
    main()