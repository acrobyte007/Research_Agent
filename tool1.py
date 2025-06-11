import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def query_arxiv(query, max_results=1):
    """
    Query the arXiv API with a string query and max_results.
    
    Args:
        query (str): The search query (e.g., 'all:quantum computing' or 'id_list:1605.08386')
        max_results (int): Maximum number of results to return
    
    Returns:
        list: List of dictionaries with 'title', 'authors', and 'pdf_url' for each paper
              or a dictionary with an error message
    """
    # Validate inputs
    if not isinstance(query, str):
        return {"error": "query must be a string"}
    try:
        max_results = int(max_results)
        if max_results < 1:
            raise ValueError("max_results must be at least 1")
    except (ValueError, TypeError):
        return {"error": "max_results must be a positive integer"}

    # Encode the query to handle spaces and special characters
    encoded_query = urllib.parse.quote(query, safe='')

    # Construct the arXiv API query URL
    base_url = 'http://export.arxiv.org/api/query'
    query_params = f'?search_query={encoded_query}&start=0&max_results={max_results}'
    url = base_url + query_params

    results = []
    try:
        # Make the API request
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            
            # Parse XML response
            root = ET.fromstring(data)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            if not entries:
                return results  # Empty list if no results
            
            # Process each entry
            for entry in entries:
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                pdf_link_elem = entry.find('{http://www.w3.org/2005/Atom}link[@type="application/pdf"]')
                
                # Extract authors
                author_elems = entry.findall('{http://www.w3.org/2005/Atom}author')
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text.strip()
                          for author in author_elems if author.find('{http://www.w3.org/2005/Atom}name') is not None]
                authors = authors if authors else ["No authors available"]
                
                # Extract title and PDF URL
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No title available"
                pdf_url = pdf_link_elem.get('href') if pdf_link_elem is not None else "No PDF available"
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "pdf_url": pdf_url
                })
                
        return results
                
    except urllib.error.URLError as e:
        return {"error": f"Error fetching data: {e}"}
    except ET.ParseError:
        return {"error": "Error parsing the API response"}

# Example usage
if __name__ == "__main__":
    try:
        query = input("Enter your arXiv query (e.g., 'all:quantum computing' or 'id_list:1605.08386'): ")
        max_results = input("Enter the maximum number of results (e.g., 1, 5, 10): ")
        result = query_arxiv(query, max_results)
        print("Query Result:", result)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")