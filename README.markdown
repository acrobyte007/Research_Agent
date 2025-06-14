# Paper Summarization

This project is a FastAPI-based web application that summarizes academic papers using the `langchain_mcp_adapters` library to connect to paper search and summarization microservices, powered by a Grok language model via `langchain_groq`. The API exposes an endpoint to accept paper URLs and return summaries.

## Prerequisites

- **Python**: Version 3.8 or higher
- **pip**: Python package manager
- **Environment Variables**: A `.env` file with a `GROQ_API_KEY` for accessing the Grok API
- **Local Microservices**: Running services at `http://127.0.0.1:4200/mcp/` (paper search) and `http://127.0.0.1:4201/mcp/` (PDF summarization)

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up a Virtual Environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   Install the required Python packages:
   ```bash
   pip install fastapi uvicorn python-dotenv langgraph langchain-mcp-adapters langchain-groq
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root with the following content:
   ```plaintext
   GROQ_API_KEY=your_grok_api_key_here
   LLM_MODEL=llama3-8b-8192  # Optional: defaults to llama3-8b-8192 if not set
   ```
   Replace `your_grok_api_key_here` with your actual Grok API key from [xAI's API portal](https://x.ai/api).

5. **Set Up Microservices**
   Ensure the paper search and PDF summarization services are running locally:
   - Paper Search Service: `http://127.0.0.1:4200/mcp/`
   - PDF Summarization Service: `http://127.0.0.1:4201/mcp/`
   Refer to the documentation of `langchain_mcp_adapters` for instructions on setting up these services.

## Usage

1. **Run the FastAPI Application**
   Start the server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`. The interactive API documentation is accessible at `http://localhost:8000/docs`.

2. **Summarize a Paper**
   Send a POST request to the `/summarize` endpoint with a JSON body containing the paper URL. Example using `curl`:
   ```bash
   curl -X POST "http://localhost:8000/summarize" -H "Content-Type: application/json" -d '{"paper_url": "http://arxiv.org/pdf/1909.03550v1"}'
   ```
   Response:
   ```json
   {"summary": {...}}
   ```

   Alternatively, use Python with `requests`:
   ```python
   import requests
   response = requests.post("http://localhost:8000/summarize", json={"paper_url": "http://arxiv.org/pdf/1909.03550v1"})
   print(response.json())
   ```

## API Endpoints

- **POST /summarize**
  - **Request Body**: JSON object with a `paper_url` field (e.g., `{"paper_url": "http://arxiv.org/pdf/1909.03550v1"}`)
  - **Response**: JSON object containing the paper summary or an error message
  - **Status Codes**:
    - `200`: Successful response with the summary
    - `500`: Error during summarization (e.g., invalid URL or microservice failure)

## Project Structure

- `main.py`: The FastAPI application that defines the API endpoint and handles paper summarization.
- `.env`: Environment file for storing the Grok API key and model configuration.
- `README.md`: This file, providing project documentation.

## Dependencies

- `fastapi`: Web framework for building the API
- `uvicorn`: ASGI server for running the FastAPI application
- `python-dotenv`: Loads environment variables from `.env`
- `langgraph`: Provides the `create_react_agent` for building the agent
- `langchain-mcp-adapters`: Interfaces with paper search and summarization microservices
- `langchain-groq`: Integrates with the Grok API for language model capabilities

## Troubleshooting

- **GROQ_API_KEY Error**: Ensure the `.env` file exists and contains a valid `GROQ_API_KEY`.
- **Microservices Not Found**: Verify that the services at `http://127.0.0.1:4200/mcp/` and `http://127.0.0.1:4201/mcp/` are running. Check their logs for errors.
- **API Errors**: Check the server logs for detailed error messages if the `/summarize` endpoint returns a 500 status code.
- **Library Compatibility**: Ensure all dependencies are up-to-date:
  ```bash
  pip install --upgrade fastapi uvicorn python-dotenv langgraph langchain-mcp-adapters langchain-groq
  ```
