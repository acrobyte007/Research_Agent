from fastmcp import Client
import asyncio
import requests
import os
from datetime import datetime
import httpx

async def test_pdf_summarize(pdf_url: str, download: bool = True):
    try:
        # Configure client with no timeout
        async with Client("http://127.0.0.1:4201/mcp/", timeout=None) as client:
            print(f"Attempting to summarize PDF: {pdf_url}")
            # Request summary from the server
            result = await client.call_tool("summarize_pdf_tool", {"pdf_url": pdf_url})
            print("PDFSummarize Result:", result)

            # Download the PDF if requested and summary is successful
            if download and "summary" in result:
                try:
                    print(f"Downloading PDF from {pdf_url}...")
                    response = requests.get(pdf_url, timeout=10)
                    response.raise_for_status()
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"downloaded_pdf_{timestamp}.pdf"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    print(f"PDF downloaded successfully as: {filename}")
                except requests.RequestException as e:
                    print(f"PDF Download Error: {str(e)}")
            return result
    except httpx.ConnectError:
        print("PDFSummarize Error: Could not connect to server. Ensure it is running on http://127.0.0.1:4201.")
        return None
    except Exception as e:
        print(f"PDFSummarize Error: {str(e)}")
        return None

async def main():
    pdf_url = "http://arxiv.org/pdf/1909.03550v1"
    await test_pdf_summarize(pdf_url, download=True)

if __name__ == "__main__":
    asyncio.run(main())