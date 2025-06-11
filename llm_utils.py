from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os
import requests
import PyPDF2
from io import BytesIO
from typing import Dict

def initialize_llm():
    print("Initializing LLM...")
    load_dotenv()
    llm_provider = os.getenv("LLM_PROVIDER", "groq")
    llm_model = os.getenv("LLM_MODEL", "llama3-8b-8192")
    api_key = os.getenv(f"{llm_provider.upper()}_API_KEY")
    print(f"Using LLM provider: {llm_provider}, model: {llm_model}")

    if llm_provider == "groq":
        llm = ChatGroq(model=llm_model, groq_api_key=api_key, temperature=0.0)
    elif llm_provider == "openai":
        llm = ChatOpenAI(model=llm_model, api_key=api_key, temperature=0.0)
    elif llm_provider == "anthropic":
        llm = ChatAnthropic(model=llm_model, api_key=api_key, temperature=0.0)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    print("LLM initialized successfully")
    return llm

def get_text_splitter():
    print("Initializing text splitter...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    print("Text splitter initialized with chunk_size=1000, chunk_overlap=200")
    return text_splitter

async def summarize_pdf(pdf_url: str, llm, text_splitter) -> Dict[str, str]:
    """Download PDF, extract text, split it, and summarize it with logging."""
    try:
        # Step 1: Download the PDF
        print(f"Downloading PDF from {pdf_url}...")
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        print(f"PDF downloaded successfully, size: {len(response.content)} bytes")

        # Step 2: Extract text from PDF
        print("Extracting text from PDF...")
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text() or ""
            text += page_text
            print(f"Extracted text from page {page_num} (length: {len(page_text)} characters)")
        print(f"Total extracted text length: {len(text)} characters")

        # Step 3: Split text into chunks
        print("Splitting text into chunks...")
        chunks = text_splitter.split_text(text)
        print(f"Text split into {len(chunks)} chunks")

        # Step 4: Summarize each chunk
        print("Summarizing chunks...")
        summaries = []
        for i, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {i}/{len(chunks)} (length: {len(chunk)} characters)")
            prompt = f"Summarize the following text in 50-75 words:\n\n{chunk}"
            summary = llm.invoke(prompt).content
            summaries.append(summary)
            print(f"Chunk {i} summarized (summary length: {len(summary)} characters)")

        # Step 5: Combine summaries into a final summary
        print("Combining summaries...")
        combined_text = "\n".join(summaries)
        final_prompt = f"Combine these summaries into a cohesive summary of 100-150 words:\n\n{combined_text}"
        final_summary = llm.invoke(final_prompt).content
        print(f"Final summary generated (length: {len(final_summary)} characters)")

        return {"summary": final_summary}
    except Exception as e:
        print(f"Error during PDF summarization: {str(e)}")
        return {"error": str(e)}