import json
import os
import time
from typing import Any, Callable, Set, Dict, List, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool
# [START enable_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from pprint import pprint
from azure.ai.projects.models import FunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction, ToolOutput, ToolSet
from dotenv import load_dotenv
import requests

# Load .env file
load_dotenv()

connection_string = os.environ["PROJECT_CONNECTION_STRING_EASTUS2"] 
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

def msgraphapi(query: str) -> str:
    returntxt = "Processing ... MS Graph Data"

    credential = DefaultAzureCredential()

    # Get an access token
    access_token = credential.get_token("https://graph.microsoft.com/.default").token

    # Set up the headers for the API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    num_meetings = 10

    # Get the user's online meetings
    meetings_url = "https://graph.microsoft.com/v1.0/me/onlineMeetings"
    meetings_response = requests.get(meetings_url, headers=headers)
    meetings = meetings_response.json().get("value", [])

    if meetings:
        # Get the last few meeting IDs
        recent_meetings = meetings[-num_meetings:]

        for meeting in recent_meetings:
            meeting_id = meeting["id"]

            print(f"Processing meeting: {meeting_id}")

            # Get transcripts for the current meeting
            transcripts_url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts"
            transcripts_response = requests.get(transcripts_url, headers=headers)
            transcripts = transcripts_response.json().get("value", [])

            if transcripts:
                # Get the content of the last transcript for this meeting
                last_transcript_id = transcripts[-1]["id"]
                content_url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts/{last_transcript_id}/content"
                content_response = requests.get(content_url, headers=headers)

                if content_response.status_code == 200:
                    print(f"Transcript content for meeting {meeting_id}:")
                    print(content_response.text)
                    returntxt = returntxt + content_response.text
                else:
                    print(f"Failed to retrieve transcript content for meeting {meeting_id}")
                    returntxt = returntxt + f"Failed to retrieve transcript content for meeting {meeting_id}"
            else:
                print(f"No transcripts found for meeting {meeting_id}")
                returntxt = f"No transcripts found for meeting {meeting_id}"
            print("-" * 40)  # Separator between meetings
    else:
        print("No online meetings found")
        returntxt = "No online meetings found"

    return returntxt

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

        print(f"Here is the Start of Responsible AI Agent")
        user_functions: Set[Callable[..., Any]] = {
            msgraphapi,
        }
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)

        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="MSGraph-Agent",
            instructions="You are a MS Graph AI assistant. Run the toolset to evaluate the output.",
            toolset=toolset,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = project_client.agents.create_thread()
        print(f"Created thread, ID: {thread.id}")

        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="Sumamarize my last few teams meeting followups?",
        )
        print(f"Created message, ID: {message.id}")

        run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        print(f"Created run, ID: {run.id}")

        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run")
                    project_client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                tool_outputs = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredFunctionToolCall):
                        try:
                            print(f"Executing tool call: {tool_call}")
                            output = functions.execute(tool_call)
                            tool_outputs.append(
                                ToolOutput(
                                    tool_call_id=tool_call.id,
                                    output=output,
                                )
                            )
                        except Exception as e:
                            print(f"Error executing tool_call {tool_call.id}: {e}")

                print(f"Tool outputs: {tool_outputs}")
                if tool_outputs:
                    project_client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            print(f"Current MSGraph Agent run status: {run.status}")
        print(f"Run MSGraph Agent completed with status: {run.status}")

        # now runing the evaluation manually
        print("--------------------------------------------------------------------")



if __name__ == "__main__":
    main()
