import datetime
import streamlit as st

import os  
import base64
from openai import AzureOpenAI  


endpoint = os.getenv("ENDPOINT_URL", "https://genaistudio1585814938.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "o3-mini")  
subscription_key = os.getenv("AZURE_OPENAI_O3_KEY")  

# Initialize Azure OpenAI Service client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-12-01-preview",
)
    
    
def processo3(query: str):
    #IMAGE_PATH = "YOUR_IMAGE_PATH"
    #encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
    returntxt = ""

    #Prepare the chat prompt 
    chat_prompt = [
        {
            "role": "developer",
            "content": [
                {
                    "type": "text",
                    "text": "You are an AI assistant that helps people find information."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""{query}"""
                }
            ]
        }
    ] 
        
    # Include speech result if speech is enabled  
    messages = chat_prompt  
        
    # Generate the completion  
    completion = client.chat.completions.create(  
        model=deployment,
        messages=messages,
        max_completion_tokens=100000,
        stop=None,  
        stream=False
    )

    # print(completion.to_json())  

    #print(completion)

    # Corrected access method
    #print(completion.choices[0].message.content)

    returntxt = completion.choices[0].message.content

    returntxt = returntxt + " \nCompletion Token: " + str(completion.usage.completion_tokens) + "\n"
    returntxt = returntxt + " Prompt Token: " + str(completion.usage.prompt_tokens) + "\n"
    returntxt = returntxt + " Total Token: " + str(completion.usage.total_tokens) + "\n"


    return returntxt

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def showo3():
    st.header("o3-mini Test")

    
    if prompt := st.chat_input("describe quantum computing in detail and create a new design?", key="chat1"):
        # Call the extractproductinfo function
        #st.write("Searching for the query: ", prompt)
        st.chat_message("user").markdown(prompt, unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "user", "message": prompt})
        starttime = datetime.datetime.now()
        rfttopics = processo3(prompt)
        endtime = datetime.datetime.now()

        #st.markdown(f"Time taken to process: {endtime - starttime}", unsafe_allow_html=True)
        rfttopics += f"\n Time taken to process: {endtime - starttime}"
        st.session_state.chat_history.append({"role": "assistant", "message": rfttopics})
        st.chat_message("assistant").markdown(rfttopics, unsafe_allow_html=True)

        # Keep only the last 10 messages
        if len(st.session_state.chat_history) > 20:  # 10 user + 10 assistant
            st.session_state.chat_history = st.session_state.chat_history[-20:]
if __name__ == "__main__":
    showo3()