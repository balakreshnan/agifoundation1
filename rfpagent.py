import os
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from semantic_kernel import Kernel
# from semantic_kernel.ai.openai_chat_autogen import OpenAIChat
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
#from semantic_kernel.ai.openai_chat_autogen import OpenAIChat
import streamlit as st
from dotenv import load_dotenv
import os
import logging
import openai

# Load .env file
load_dotenv()

# Set up Azure Search Client
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX")
AZURE_SEARCH_KEY = os.getenv("AZURE_AI_SEARCH_KEY")

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX_NAME,
    credential=AZURE_SEARCH_KEY
)

# Semantic Kernel Setup
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Set the logging level for  semantic_kernel.kernel to DEBUG.
logging.basicConfig(
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("kernel").setLevel(logging.DEBUG)

# Initialize the kernel
kernel = Kernel()

# Add Azure OpenAI chat completion
chat_completion = AzureChatCompletion(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
kernel.add_service(chat_completion)

def generate_embedding(user_input):
    """Generates embedding for the given user input using OpenAI embeddings."""
    response = openai.embeddings.create(
        input=user_input,
        model="text-embedding-ada-002"  # Specify the embedding model deployed in Azure OpenAI
    )
    return response.data[0].embedding

# Define function to chat with RFQ
def chat_with_rfq(user_input):
    """Processes RFQ chat-based queries."""
    # Generate embedding for the user query
    embedding_query = generate_embedding(user_input)

    # Query Azure Search Index with vector search
    search_results = search_client.search(
        search_text="",  # Empty since we use vector search
        vectors=[{
            "value": embedding_query,
            "fields": ["contentVector"],  # The field storing embeddings in Azure Search
            "k": 5  # Top 5 results
        }],
        query_type=QueryType.SEMANTIC,
        query_language="en-us",
        semantic_configuration_name="default"
    )

    top_answers = []
    for result in search_results:
        top_answers.append(result["content"])

    # Combine results and build prompt for OpenAI
    prompt = "\n".join(["### Source:", *top_answers]) + f"\n\nGiven the above information, answer the question: {user_input}"

    # Get response from OpenAI
    chat_response = chat_completion.completion(prompt)
    return chat_response

# Streamlit App for Chat UI
st.title("RFQ Response Chat System")

user_query = st.text_input("Enter your RFQ query:", "Show me profiles of rail road experience.")

if st.button("Submit"):
    if user_query:
        try:
            response = chat_with_rfq(user_query)
            st.success("Response:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a query.")
