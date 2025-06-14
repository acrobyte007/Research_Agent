from fastmcp import FastMCP
from search import query_arxiv
from llm_utils import initialize_llm, get_text_splitter, summarize_pdf
from typing import List, Dict, Any
import asyncio
import threading

# Initialize the main MCP server
main_mcp = FastMCP(name="ResearchAssistant")

# Initialize LLM and text splitter for PDF summarization
llm = initialize_llm()
text_splitter = get_text_splitter()

@main_mcp.tool
async def search_arxiv(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search for academic papers on arXiv.org based on a query string.

    Args:
        query (str): The search query for arXiv papers (e.g., "machine learning").
        max_results (int): Maximum number of results to return (default: 10).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing paper metadata, including title,
                              authors, abstract, and PDF URL. Returns an error dictionary if the search fails.

    Example:
        search_arxiv("quantum computing", 5) -> [{"title": ..., "authors": ..., "abstract": ..., "pdf_url": ...}, ...]
    """
    result = query_arxiv(query, max_results)
    if isinstance(result, dict) and "error" in result:
        return [{"error": result["error"]}]
    return result

@main_mcp.tool
async def summarize_pdf_tool(pdf_url: str) -> Dict[str, str]:
    """
    Download a PDF from a given URL, extract its text, split it into chunks, and generate a summary.

    Args:
        pdf_url (str): The URL of the PDF file to summarize.

    Returns:
        Dict[str, str]: A dictionary containing the summary of the PDF or an error message if processing fails.

    Example:
        summarize_pdf_tool("https://arxiv.org/pdf/1234.5678.pdf") -> {"summary": "This paper discusses...", "status": "success"}
    """
    print(f"Received request to summarize PDF: {pdf_url}")
    result = await summarize_pdf(pdf_url, llm, text_splitter)
    print("Request processing complete")
    return result

def start_server():
    """
    Start the ResearchAssistant MCP server to handle both arXiv search and PDF summarization requests.
    The server uses streamable-http transport and runs on localhost:4200.
    """
    print("Starting ResearchAssistant server...")
    try:
        # Try to get the running event loop
        try:
            loop = asyncio.get_running_loop()
            # If a loop is running, start server in a new thread
            server_thread = threading.Thread(
                target=lambda: asyncio.run(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4200))
            )
            server_thread.daemon = True
            server_thread.start()
            print("Server started in a new thread")
        except RuntimeError:
            # No running loop; create or use a new loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4200))
            print("Server started in a new event loop")
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        # Fallback to running the server in a new loop
        asyncio.run(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4200))

if __name__ == "__main__":
    start_server()