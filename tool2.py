import urllib.request
import os

def download_pdf(input_dict):
    """
    Download the PDF from the given URL and save it locally.
    
    Args:
        input_dict (dict): Dictionary with 'pdf_url' (str)
    
    Returns:
        dict: Status message indicating success or failure
    """
    if not isinstance(input_dict, dict) or 'pdf_url' not in input_dict:
        return {"error": "Input must be a dictionary with 'pdf_url' key"}
    pdf_url = input_dict.get('pdf_url')
    
    if not isinstance(pdf_url, str) or not pdf_url.startswith('http'):
        return {"error": "pdf_url must be a valid URL string"}

    try:
        
        arxiv_id = pdf_url.split('/')[-1].replace('.pdf', '') if '/pdf/' in pdf_url else 'paper'
        safe_filename = f"{arxiv_id.replace('/', '_')}.pdf"
        
        
        os.makedirs("arxiv_pdfs", exist_ok=True)
        file_path = os.path.join("arxiv_pdfs", safe_filename)
        
        
        with urllib.request.urlopen(pdf_url) as response:
            with open(file_path, 'wb') as f:
                f.write(response.read())
        return {"status": f"PDF downloaded successfully to {file_path}"}
        
    except urllib.error.URLError as e:
        return {"error": f"Error downloading PDF: {e}"}
    except OSError as e:
        return {"error": f"Error saving PDF: {e}"}

# Example usage
if __name__ == "__main__":
    try:
        pdf_input = {"pdf_url": "http://arxiv.org/pdf/1605.08386v1"}
        result = download_pdf(pdf_input)
        print("Download Result:", result)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")