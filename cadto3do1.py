import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import base64
import requests
import io

# Load .env file
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_O1_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_O1_KEY"),  
  api_version="2024-10-21"
)

model_name = "o1-preview"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def processimage(base64_image, imgprompt, model_name="o1-preview"):
    response = client.chat.completions.create(
    model=model_name,
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": f"{imgprompt}"},
            {
            "type": "image_url",
            "image_url": {
                "url" : f"data:image/jpeg;base64,{base64_image}",
            },
            },
        ],
        }
    ],
    max_completion_tokens=4000,
    #temperature=0,
    #top_p=1,
    #seed=105,
    )

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def process_image(uploaded_file, selected_optionmodel, user_input):
    returntxt = ""

    if uploaded_file is not None:
        #image = Image.open(os.path.join(os.getcwd(),"temp.jpeg"))
        img_path = os.path.join(os.getcwd(),"temp1.jpeg")
        # Open the image using PIL
        # image_bytes = uploaded_file.read()
        #image = Image.open(io.BytesIO(image_bytes))

        base64_image = encode_image(img_path)
        #base64_image = base64.b64encode(uploaded_file).decode('utf-8') #uploaded_image.convert('L')
        imgprompt = f"""You are a AutoCAD drawing AI Agent. You are an expert in Auto CAD Architecture drawings.
        Based on the question asked, analyze the drawings and get all the insights.

        Question:
        {user_input} 
        """

        # Get the response from the model
        result = processimage(base64_image, imgprompt)

        #returntxt += f"Image uploaded: {uploaded_file.name}\n"
        returntxt = result

    return returntxt

def autocadinsightso1():
    count = 0
    temp_file_path = ""

    #tab1, tab2, tab3, tab4 = st.tabs('RFP PDF', 'RFP Research', 'Draft', 'Create Word')
    modeloptions1 = ["gpt-4o-2", "gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo"]
    imgfile = "temp1.jpg"
    # Create a dropdown menu using selectbox method
    selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
    count += 1
    user_input = st.text_input("Enter the question to ask the AI model", "explain with details what is in the drawings")
    st.write("Upload a Auto CAD image file")
    img_file = st.file_uploader("Upload JPG", type=['jeg', 'jpeg', 'png', 'jpg'])
    if img_file is not None:
        # Read the uploaded file as bytes
        file_bytes = img_file.read()

        # Display the bytes as an image
        # Convert bytes to an Image object (using PIL for better compatibility)
        image = Image.open(io.BytesIO(file_bytes))
        
        # Display the uploaded image
        st.image(image, caption="Uploaded Image", use_container_width=True)
        image.convert('RGB').save('temp1.jpeg')
        returntxt = process_image(img_file, selected_optionmodel1, user_input)
        st.markdown(returntxt, unsafe_allow_html=True)