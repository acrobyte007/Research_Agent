from fastmcp import FastMCP
from llm_utils import initialize_llm, get_text_splitter, summarize_pdf
from typing import Dict
import asyncio
import threading

main_mcp = FastMCP(name="PDFSummarize")
llm = initialize_llm()
text_splitter = get_text_splitter()

@main_mcp.tool
async def summarize_pdf_tool(pdf_url: str) -> Dict[str, str]:
    """Download PDF from url, extract text, split it, and summarize it."""
    print(f"Received request to summarize PDF: {pdf_url}")
    result = await summarize_pdf(pdf_url, llm, text_splitter)
    print("Request processing complete")
    return result

def start_server():
    print("Starting PDFSummarize server...")
    try:
        # Try to get the running loop, if any
        try:
            loop = asyncio.get_running_loop()
            # If a loop is running, start server in a new thread
            server_thread = threading.Thread(target=lambda: asyncio.run(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4201)))
            server_thread.daemon = True
            server_thread.start()
            print("Server started in a new thread")
        except RuntimeError:
            # No running loop; create or use a new loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4201))
            print("Server started in a new event loop")
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        asyncio.run(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4201))

if __name__ == "__main__":
    start_server()