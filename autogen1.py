import os
from PyPDF2 import PdfReader
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core.tools import Tool, FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from typing_extensions import Annotated
from dotenv import load_dotenv
load_dotenv()

pdf_file_path = "DeepSeekR1-2501.12948v1.pdf"

# client = AzureOpenAI(
#   azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_VISION"), 
#   api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),  
#   api_version="2024-10-21"
# )

# model_name = "gpt-4o-2"

model_client = AzureOpenAIChatCompletionClient(model="gpt-4o",
                                               azure_deployment="gpt-4o-2", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21",
                                               temperature=0.0,
                                               seed=42,
                                               maz_tokens=4096)

# Step 1: Define the PDF Reader Function
def extract_text_from_pdf(filename: Annotated[str, "The full path to the PDF file"]) -> str:
    """
    Extracts all text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    try:
        pdf_path = "DeepSeekR1-2501.12948v1.pdf"

        if filename != "":
            filename = pdf_path
        # Check if the file exists
        if not os.path.exists(filename):
            return f"Error: File '{filename}' does not exist."

        # Create a PdfReader object
        reader = PdfReader(filename)
        
        # Initialize an empty string to store the extracted text
        extracted_text = ""
        
        # Loop through all pages in the PDF and extract text
        for page in reader.pages:
            extracted_text += page.extract_text() + "\n"  # Add newline for separation between pages
        
        return extracted_text.strip()
    except Exception as e:
        return f"An error occurred: {e}"



# Step 4: Test the Agent with the Tool
if __name__ == "__main__":
    # Example usage of the tool directly
    pdf_file_path = "DeepSeekR1-2501.12948v1.pdf"  # Replace with your actual PDF file path
    
    print("Testing the PDF Reader Tool:")
    print(extract_text_from_pdf(pdf_file_path))

    # Example usage of the agent calling the tool
    print("\nTesting Agent with Tool:")
    # Step 2: Wrap the Function as a Tool Using FunctionTool
    pdf_reader_tool = FunctionTool(
        func=extract_text_from_pdf,
        description="Extracts text from a given PDF file. Provide the full file path as input.",
        name="pdf_reader"
    )

    # Step 3: Define an Agent and Add the Tool
    agent = AssistantAgent(
        name="assistant_with_pdf_reader",
        model_client=AzureOpenAIChatCompletionClient(model="gpt-4",
                                                     azure_deployment="gpt-4-2",
                                                     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                                     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                                     api_version="2024-10-21",
                                                     temperature=0.0,
                                                     seed=42,
                                                     max_tokens=4096),
        tools=[pdf_reader_tool],  # Add the tool to the agent's list of tools
        handoffs=["val_agent"],  # No handoffs for this agent
    )

    val_agent = AssistantAgent(
        name="val_agent",
        model_client=model_client,
        handoffs=["quality_agent"],
        system_message=(
            "You are the Content Reviewer AI. Validate the output."
        ),
    )
    # Quality Agent: updates user stories based on progress.
    quality_agent = AssistantAgent(
        name="quality_agent",
        model_client=model_client,
        # It can either ask adf_agent for more detail or, when ready, hand off to the next agent.
        handoffs=["adf_agent"],
        system_message=(
            "You are the Quality Agent. Your task is to update and maintain user stories from the progress reports of adf_agent. "
            "When you receive an update, evaluate whether a new user story is needed or if an existing one should be revised. "
            "If you require additional details for clarification or validation, request adf_agent to provide them. "
            "Once you confirm that unit tests offer 100% coverage of the current functionality, signal that the analysis is complete by handing off to 'adf_agent'."
        ),
    )
    # Example usage of the agent calling the tool
    print("\nTesting Agent with Tool:")
    
    # response = agent.chat(query)
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination
    team = RoundRobinGroupChat([agent, val_agent], termination_condition=termination, max_turns=1)
    query = f"Read and extract text from this file: DeepSeekR1-2501.12948v1.pdf"
    # Extract the generated code
    #query = "Write a Python function that to chat last 6 months of Tesla stock price using yfinance library and print as table."
    #result = await Console(team.run_stream(task=query))
    response = team.run(task=query)
    print(response)

    print(team.dump_component().model_dump_json())
