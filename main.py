import os
import asyncio
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
import httpx

def initialize_llm():
    load_dotenv()
    llm_model = os.getenv("LLM_MODEL", "llama3-8b-8192")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")
    return ChatGroq(model=llm_model, groq_api_key=api_key, temperature=0.0)

async def main():
    http_client = httpx.AsyncClient(timeout=3600.0)
    client = MultiServerMCPClient(
        {
            "research_assistant": {
                "url": "http://127.0.0.1:4200/mcp/",
                "transport": "streamable_http",
            }
        }
    )
    try:
        tools = await client.get_tools()
        llm = initialize_llm()
        agent = create_react_agent(llm, tools)
        response = await agent.ainvoke({"messages": "Search for papers on 'machine learning' and summarize the first result"})
        print(response)
    finally:
        await http_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())