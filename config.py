import base64
import io
import json
import os
import uuid
from PyPDF2 import PdfReader
import PyPDF2
import requests
import streamlit as st
import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

# Azure Search Service Information
service_name = os.getenv("AZURE_AI_SEARCH_ENDPOINT_NAME") 
index_name = "mfggptdata"
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
new_index_name = "cogsrch-index-profile-vector-large"

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_VISION"), 
  api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),  
  api_version="2024-10-01-preview"
)

model_name = "gpt-4o-g"

def delete_index(cust_index_name):
    #url = '{0}/indexes/{1}/?api-version=2021-04-30-Preview'.format(self.endpoint, self.index)
    endpoint = "https://{}.search.windows.net/".format(service_name)
    url = '{0}/indexes/{1}/?api-version=2024-07-01'.format(endpoint, cust_index_name)  

    headers = {
    'api-key': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("DELETE", url, headers=headers)
    print(response.text)


    return True

def create_index_semantic(cust_index_name):

    #url = '{0}/indexes/{1}/?api-version=2021-04-30-Preview'.format(self.endpoint, self.index)
    endpoint = "https://{}.search.windows.net/".format(service_name)
    url = '{0}/indexes/{1}/?api-version=2024-07-01'.format(endpoint, cust_index_name)    
    print(url)

    payload = json.dumps({
    "name": cust_index_name,
    "defaultScoringProfile": "",
    "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "stored": True,
      "sortable": True,
      "facetable": True,
      "key": True,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": None,
      "vectorSearchProfile": None,
      "vectorEncoding": None,
      "synonymMaps": []
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "stored": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": None,
      "vectorSearchProfile": None,
      "vectorEncoding": None,
      "synonymMaps": []
    },
    {
      "name": "chunk",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "stored": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": None,
      "vectorSearchProfile": None,
      "vectorEncoding": None,
      "synonymMaps": []
    },
    {
      "name": "chunkVector",
      "type": "Collection(Edm.Single)",
      "searchable": True,
      "filterable": False,
      "retrievable": True,
      "stored": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": 3072,
      "vectorSearchProfile": "vector-profile-1",
      "vectorEncoding": None,
      "synonymMaps": []
    },
    {
      "name": "name",
      "type": "Edm.String",
      "searchable": True,
      "filterable": False,
      "retrievable": True,
      "stored": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": None,
      "vectorSearchProfile": None,
      "vectorEncoding": None,
      "synonymMaps": []
    },
    {
      "name": "location",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": True,
      "stored": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": None,
      "vectorSearchProfile": None,
      "vectorEncoding": None,
      "synonymMaps": []
    },
    {
      "name": "page_num",
      "type": "Edm.Int32",
      "searchable": False,
      "filterable": True,
      "retrievable": True,
      "stored": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "dimensions": None,
      "vectorSearchProfile": None,
      "vectorEncoding": None,
      "synonymMaps": []
    }
  ],
  "scoringProfiles": [],
  "corsOptions": None,
  "suggesters": [],
  "analyzers": [],
  "tokenizers": [],
  "tokenFilters": [],
  "charFilters": [],
  "encryptionKey": None,
  "similarity": {
    "@odata.type": "#Microsoft.Azure.Search.BM25Similarity",
    "k1": None,
    "b": None
  },
  "semantic": {
    "defaultConfiguration": None,
    "configurations": [
      {
        "name": "my-semantic-config",
        "prioritizedFields": {
          "titleField": {
            "fieldName": "title"
          },
          "prioritizedContentFields": [
            {
              "fieldName": "chunk"
            }
          ],
          "prioritizedKeywordsFields": []
        }
      }
    ]
  },
  "vectorSearch": {
    "algorithms": [
      {
        "name": "vectorConfig",
        "kind": "hnsw",
        "hnswParameters": {
          "metric": "cosine",
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500
        },
        "exhaustiveKnnParameters": None
      }
    ],
    "profiles": [{
                "name": "vector-profile-1",
                "algorithm": "vectorConfig"
            }],
    "vectorizers": [],
    "compressions": []
  }
    })
    headers = {
    'api-key': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)

    if response.status_code == 201 or response.status_code == 204:
        print('good')
        return response, True
    else:
        # print('************************')
        # print(response.status_code)
        # print(response.text)
        return response, False

# Function to get embedding
def get_embedding_large(text, model="text-embedding-3-large"):
    # In newer versions, the embedding endpoint has been updated
    #embedding = openai.embeddings.create(input=text, model=model)['data'][0]['embedding']
    response = openai.embeddings.create(input=text, model=model)
    embedding = response.data[0].embedding
    return embedding

def chunkpdf(pdf_bytes, chunk_size=2000, cust_index_name="mfgsrptest1", filename="uploaded_pdf.pdf"):
    # Convert the bytes into a PDF file
    pdf = PdfReader(io.BytesIO(pdf_bytes))
    #num_pages = pdf.getNumPages()
    num_pages = len(pdf.pages)
    print(f"Number of pages in the PDF: {num_pages}")
    # Chunk the PDF file
    endpoint = "https://{}.search.windows.net/".format(service_name)
    url = '{0}indexes/{1}/docs/search?api-version=2024-07-01'.format(endpoint, cust_index_name)

    chunks = []
    i = 0
    #for i in range(0, num_pages, chunk_size):
    for page_num in range(num_pages):
        #chunk = pdf.pages[i:i + chunk_size]
        page = pdf.pages[page_num]
        chunk = page.extract_text()
        chunks.append(chunk)
        
        relevant_data = []
        lst_embeddings_text = []
        lst_embeddings = []
        lst_file_name = []
        count = 0
        title = filename
        chunk = chunk
        id = uuid.uuid4()
        title = "pdf_page_" + str(page_num)
        name = "pdf_page_" + str(page_num)
        location = str(page_num) + "_" + filename
        page_num1 =page_num
        # print(f"Document ID: {doc_id}, Embeddings: {embeddings}")
        #print(f"Document ID: {doc_id}, Chunk: {chunk}, Title: {title}, Name: {name}, Location: {location}, Page Number: {page_num} \n")
        embeddingsnew = get_embedding_large(chunk)

        endpoint = "https://{}.search.windows.net/".format(service_name)
        url = '{0}/indexes/{1}/docs/index?api-version=2024-07-01'.format(endpoint, cust_index_name)
        payload = json.dumps({
            "value" : [
                {
                    "@search.action": "mergeOrUpload",
                    "id": str(id),
                    "title": title,
                    "chunk": chunk,
                    "chunkVector": embeddingsnew,
                    "name": name,
                    "location": location,
                    "page_num": page_num1
                }
            ]
        })
        headers = {
        'api-key': '{0}'.format(api_key),
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
    print("Index Updated successfully")
    st.markdown("Index Updated successfully")

    return True

def extractsamplequestions(user_input1, selected_optionmodel1, pdf_bytes):
    returntxt = ""

    rfttext = ""

    if pdf_bytes:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        st.write(f"Number of pages in the PDF: {num_pages}")
        # Extract and display text from the first page
        if num_pages > 0:
            for page_num in range(num_pages):
                page = reader.pages[page_num]  # Get each page
                text = page.extract_text()  # Extract text from the page
                rfttext += f"### Page {page_num + 1}\n{text}\n\n"  # Accumulate text from each page

    # print('RFP Text:', rfttext)

    message_text = [
    {"role":"system", "content":f"""You are AI agent. Be politely, and provide positive tone answers.
     Here is the PDF text tha was provided:
     {rfttext}

     Only provide answers from the content of the RFP.
     If not sure, ask the user to provide more information."""}, 
    {"role": "user", "content": f"""{user_input1}. Create 5 questions from provided PDF content."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=0.0,
        seed=105,
    )

    returntxt = response.choices[0].message.content
    return returntxt

def configmain():
    count = 0
    temp_file_path = ""
    pdf_bytes = None
    rfpcontent = {}
    rfplist = []
    #tab1, tab2, tab3, tab4 = st.tabs('RFP PDF', 'RFP Research', 'Draft', 'Create Word')
    modeloptions1 = ["gpt-4o-2", "gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo"]



    # Create a dropdown menu using selectbox method
    selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
    count += 1

    indexname = st.text_input("Index Name", "mfgsrptest1")

    tabs = st.tabs(["Upload", "Sample Questions"])

    with tabs[0]:
        st.write("Upload RFP PDF file")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="pdf_file0")
        if uploaded_file is not None:
            # Display the PDF in an iframe
            pdf_bytes = uploaded_file.read()  # Read the PDF as bytes
            st.download_button("Download PDF", pdf_bytes, file_name="uploaded_pdf.pdf")

            # Convert to base64
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            # Embedding PDF using an HTML iframe
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="700" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            # Save the PDF file to the current folder
            file_path = os.path.join(os.getcwd(), uploaded_file.name)  # Save in the current directory
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())  # Write the uploaded file to disk
            
            # Display the path where the file is stored
            # st.write(f"File saved to: {file_path}")
            temp_file_path = file_path

            if st.button("Create Index"):
                try:
                    delete_index(indexname)
                except:
                    pass
                response, status = create_index_semantic(indexname)
                if status:
                    st.write("Index created successfully")
                    chunkpdf(pdf_bytes, 2000, indexname, uploaded_file.name)
                else:
                    st.write("Index creation")
    with tabs[1]:
        st.write("Sample questions from PDF") 
        if st.button("Extract Sample Questions"):
            if uploaded_file is not None:
              returntxt = extractsamplequestions("Create 5 questions from provided PDF content.", selected_optionmodel1, pdf_bytes)
              st.markdown(returntxt, unsafe_allow_html=True)
