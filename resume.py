import streamlit as st
from openai import AzureOpenAI
import fitz  # PyMuPDF for PDF processing
import docx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Azure OpenAI model deployment name

# openai.api_type = "azure"
# openai.api_base = AZURE_OPENAI_ENDPOINT
# openai.api_version = "2024-10-21"
# openai.api_key = AZURE_OPENAI_API_KEY

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_VISION"), 
  api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),  
  api_version="2024-10-21"
)

model_name = "gpt-4o-2"

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file."""
    doc = docx.Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def analyze_resume(job_desc, resume_text):
    """Analyze resume against job description using Azure OpenAI."""
    prompt = f"""
    Given the following job description and resume, analyze the match:
    
    Job Description:
    {job_desc}
    
    Resume:
    {resume_text}
    
    Provide a short analysis on strengths, gaps, and improvements needed to better fit this job.
    """
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=1500,
    )
    
    return response.choices[0].message.content

def generate_optimized_resume(job_desc, resume_text):
    """Generate an optimized, ATS-friendly resume using Azure OpenAI."""
    prompt = f"""
    Rewrite the following resume to be optimized for ATS bots, making it stand out for HR recruiters. 
    Keep it within 2 pages and ensure it strongly aligns with the job description.
    
    Job Description:
    {job_desc}
    
    Original Resume:
    {resume_text}
    
    Optimized Resume:
    """
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "system", "content": "You are an expert in resume optimization and ATS-friendly writing."},
                  {"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=1500,
    )
    
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="AI Resume Optimizer", layout="wide")
st.title("📄 AI Resume Optimizer using Azure OpenAI")
st.write("🚀 Optimize your resume to bypass ATS bots and catch HR recruiters' attention!")

# Job description input
job_desc = st.text_area("Paste the job description here:", height=200)

# Resume upload
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX):", type=["pdf", "docx"])

if uploaded_file and job_desc:
    st.success("✅ Resume uploaded successfully!")
    
    # Extract resume text
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    st.subheader("📊 Resume Analysis")
    analysis = analyze_resume(job_desc, resume_text)
    st.write(analysis)

    st.subheader("🎯 Optimized Resume")
    optimized_resume = generate_optimized_resume(job_desc, resume_text)
    st.text_area("Your optimized ATS-friendly resume:", optimized_resume, height=400)

    # Download option
    st.download_button(
        label="⬇ Download Optimized Resume",
        data=optimized_resume,
        file_name="Optimized_Resume.txt",
        mime="text/plain"
    )
