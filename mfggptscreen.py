from datetime import datetime
import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
import json
from mfgdata import extractmfgresults
import datetime

# Helper function to read text files
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Helper function to read PDF files
def read_pdf_file(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to fetch content of the source
def fetch_source_content(file_name):
    file_path = os.path.join('sources', file_name)
    if file_name.endswith('.txt'):
        return read_text_file(file_path)
    elif file_name.endswith('.pdf'):
        return read_pdf_file(file_path)
    return "Unsupported file format."

# Streamlit App
def main():
    st.title("LLM Chat with Citations")

    
    if prompt := st.chat_input("what are the personal protection i should consider in manufacturing?", key="chat1"):
        # Call the extractproductinfo function
        #st.write("Searching for the query: ", prompt)
        st.chat_message("user").markdown(prompt, unsafe_allow_html=True)
        starttime = datetime.datetime.now()
        rfttopics = extractmfgresults(prompt)
        endtime = datetime.datetime.now()

        #st.markdown(f"Time taken to process: {endtime - starttime}", unsafe_allow_html=True)
        rfttopics += f"\n Time taken to process: {endtime - starttime}"
        st.chat_message("assistant").markdown(rfttopics, unsafe_allow_html=True)

if __name__ == "__main__":
    main()