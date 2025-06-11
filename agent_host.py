from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
import asyncio

app = FastAPI(title="Paper Summarization API")

class PaperRequest(BaseModel):
    paper_url: str

def initialize_llm():
    print("Initializing LLM...")
    load_dotenv()
    llm_model = os.getenv("LLM_MODEL", "llama3-8b-8192")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")
    print(f"Using model: {llm_model}")
    return ChatGroq(model=llm_model, groq_api_key=api_key, temperature=0.0)

@app.on_event("startup")
async def startup_event():
    global client, agent
    client = MultiServerMCPClient(
        {
            "paper_search": {
                "url": "http://127.0.0.1:4200/mcp/",
                "transport": "streamable_http",
            },
            "pdf_summarize": {
                "url": "http://127.0.0.1:4201/mcp/",
                "transport": "streamable_http",
            },
        }
    )
    try:
        tools = await client.get_tools()
        llm = initialize_llm()
        agent = create_react_agent(llm, tools)
    except Exception as e:
        print(f"Startup error: {e}")
        raise

@app.post("/summarize")
async def summarize_paper(request: PaperRequest):
    try:
        response = await agent.ainvoke({"messages": f"Summarize this paper: {request.paper_url}"})
        return {"summary": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing paper: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)