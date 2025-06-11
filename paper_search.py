from fastmcp import FastMCP
from search import query_arxiv
from typing import List, Dict, Any
import asyncio
import threading

main_mcp = FastMCP(name="PaperSearch")

@main_mcp.tool
async def search(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Search for papers on arxiv.org"""
    result = query_arxiv(query, max_results)
    if isinstance(result, dict) and "error" in result:
        return [{"error": result["error"]}]
    return result

def start_server():
    try:
        # Check if there's an existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a new thread to run the server
            server_thread = threading.Thread(target=lambda: asyncio.run(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4200)))
            server_thread.daemon = True
            server_thread.start()
        else:
            # Use the existing loop to run the server
            loop.run_until_complete(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4200))
    except RuntimeError:
        # If no loop exists, create a new one
        asyncio.run(main_mcp.run(transport="streamable-http", host="127.0.0.1", port=4200))

if __name__ == "__main__":
    start_server()