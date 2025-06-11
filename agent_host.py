from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastmcp import Client
import asyncio
import json
import logging
from datetime import datetime
import re
from typing import AsyncGenerator, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("agent_host.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Agent Host", description="Agent for interacting with PaperSearch and PDFSummarize MCP servers")

# Pydantic model for user input
class UserMessage(BaseModel):
    message: str

def serialize_response(response: Any) -> Any:
    """Manually clean and convert response objects to JSON-compatible formats."""
    logger.debug(f"Serializing response: type={type(response)}, value={str(response)[:100]}...")

    # Handle list responses from PaperSearch
    if isinstance(response, list) and len(response) == 1 and isinstance(response[0], dict):
        item = response[0]
        if 'text' in item and item.get('type') == 'text':
            text = item['text']
            logger.debug(f"Found text field: {text[:100]}...")
            try:
                # Manually parse the text as JSON array
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    logger.debug("Successfully parsed text as JSON array")
                    return parsed  # Return clean array of papers
                logger.warning("Parsed text is not a list; returning as-is")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse text as JSON: {str(e)}")
                return {"error": f"Invalid response format: {str(e)}"}

    # Handle dictionaries
    if isinstance(response, dict):
        return {key: serialize_response(value) for key, value in response.items()}

    # Handle lists
    if isinstance(response, list):
        return [serialize_response(item) for item in response]

    # Handle standard JSON-serializable types
    if isinstance(response, (str, int, float, bool, type(None))):
        return response

    # Fallback: convert unknown types to string
    logger.warning(f"Converting unknown type {type(response)} to string")
    return str(response)

def decide_tool_and_args(message: str) -> Dict[str, Any]:
    """Use rule-based logic to decide which MCP tool to call and clean arguments."""
    message = message.strip().lower()
    logger.info(f"Processing message: {message}")

    # Rule 1: Check for PDF URL or 'summarize'
    pdf_url_pattern = r"(https?://[^\s]+\.pdf)"
    pdf_url_match = re.search(pdf_url_pattern, message)
    if pdf_url_match or "summarize" in message:
        pdf_url = pdf_url_match.group(1) if pdf_url_match else None
        if not pdf_url:
            logger.error("No valid PDF URL found")
            return {"tool": None, "args": {}, "reason": "No valid PDF URL provided"}
        return {
            "tool": "summarize_pdf_tool",
            "args": {"pdf_url": pdf_url},
            "reason": "Message contains a PDF URL or 'summarize' keyword"
        }

    # Rule 2: Treat other messages as search queries
    query = message.replace("search", "").strip()
    # Clean query: replace 're' with 'related' if it appears to be a typo
    query = re.sub(r'\bre\b', 'related', query)
    logger.debug(f"Cleaned query: {query}")
    arxiv_id_pattern = r"(\d{4}\.\d{5})"
    if re.search(arxiv_id_pattern, query):
        query = f"id_list:{query}"
    if not query:
        logger.error("No valid search query provided")
        return {"tool": None, "args": {}, "reason": "No valid search query"}
    return {
        "tool": "search",
        "args": {"query": query, "max_results": 5},
        "reason": "Message interpreted as search query or arXiv ID"
    }

async def call_tool(tool: str, args: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Call the MCP tool and stream responses."""
    start_time = datetime.now()
    logger.info(f"Calling {tool}, args: {args}, start_time: {start_time}")

    client_url = (
        "http://127.0.0.1:4200/mcp/" if tool == "search" else
        "http://127.0.0.1:4201/mcp/" if tool == "summarize_pdf_tool" else None
    )
    if not client_url:
        logger.error(f"Invalid tool: {tool}")
        yield f"data: {json.dumps({'error': f'Invalid tool: {tool}'})}\n\n"
        return

    try:
        async with Client(client_url) as client:
            yield f"data: {json.dumps({'status': f'Calling {tool} with args {args}'})}\n\n"
            result = await client.call_tool(tool, args)
            serialized_result = serialize_response(result)
            yield f"data: {json.dumps({'result': serialized_result})}\n\n"
            logger.info(f"Completed {tool}, end_time: {datetime.now()}, duration: {(datetime.now() - start_time).total_seconds()}s")
    except Exception as e:
        error_msg = f"Error calling {tool} at {client_url}: {str(e)}"
        logger.error(error_msg)
        yield f"data: {json.dumps({'error': error_msg})}\n\n"

@app.post("/process_message", response_model=None)
async def process_message(user_message: UserMessage) -> StreamingResponse:
    """
    Process a user message and stream responses from the selected MCP server.

    Example:
    ```bash
    curl -X POST http://127.0.0.1:8000/process_message -H "Content-Type: application/json" -d '{"message": "Summarize http://arxiv.org/pdf/1909.03550v1"}'
    ```
    Response (streamed):
    ```
    data: {"status": "Calling summarize_pdf_tool with args {\"pdf_url\": \"http://arxiv.org/pdf/1909.03550v1\"}"}
    data: {"result": {"summary": "This paper discusses..."}}}
    ```

    Example:
    ```bash
    curl -X POST http://127.0.0.1:8000/process_message -H "Content-Type: application/json" -d '{"message": "Search machine learning re papers"}'
    ```
    Response (streamed):
    ```
    data: {"status": "Calling search with args {\"query\": \"machine learning related papers\", \"max_results\": 5}"}
    data: {"result": [{"title": "...", "authors": [...], "pdf_url": "..."}]}
    ```
    """
    logger.info(f"Received user message: {user_message.message}")
    
    decision = decide_tool_and_args(user_message.message)
    if not decision["tool"]:
        logger.error("No valid tool selected")
        raise HTTPException(status_code=400, detail=decision["reason"])

    return StreamingResponse(
        call_tool(decision["tool"], decision["args"]),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    """
    Check if the Agent Host is running.

    Example:
    ```bash
    curl http://127.0.0.1:8000/health
    ```
    Response:
    ```
    {"status": "healthy"}
    ```
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)