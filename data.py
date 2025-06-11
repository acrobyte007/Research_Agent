import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def query_arxiv(user_query, max_results=1):
    """
    Query the arXiv API with a user-provided query and max_results, return parsed results.
    
    Args:
        user_query (str): The search query (e.g., 'all:quantum computing' or 'id_list:1605.08386')
        max_results (int): Maximum number of results to return
    
    Returns:
        None: Prints the title, summary, and arXiv ID of the papers or an error message
    """
    # Validate max_results
    try:
        max_results = int(max_results)
        if max_results < 1:
            raise ValueError("max_results must be at least 1")
    except ValueError as e:
        print(f"Invalid max_results: {e}")
        return

    # Encode the query to handle spaces and special characters
    encoded_query = urllib.parse.quote(user_query, safe='')

    # Construct the arXiv API query URL
    base_url = 'http://export.arxiv.org/api/query'
    query_params = f'?search_query={encoded_query}&start=0&max_results={max_results}'
    url = base_url + query_params

    try:
        # Make the API request
        with urllib.request.urlopen(url) as response:
            # Read and decode the response
            data = response.read().decode('utf-8')
            
            # Parse XML response
            root = ET.fromstring(data)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            if not entries:
                print("No results found for the query.")
                return
            
            # Print details for each entry
            for entry in entries:
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                
                # Check for None to handle malformed entries
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No title available"
                summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else "No summary available"
                arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None and id_elem.text else "No ID available"
                
                print(f"arXiv ID: {arxiv_id}")
                print(f"Title: {title}")
                print(f"Summary: {summary}")
                
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}")
    except ET.ParseError:
        print("Error parsing the API response.")

# Get user input for the query and max_results
try:
    user_query = input("Enter your arXiv query (e.g., 'all:quantum computing' or 'id_list:1605.08386'): ")
    max_results_input = input("Enter the maximum number of results (e.g., 1, 5, 10): ")
    
    # Execute the query
    query_arxiv(user_query, max_results_input)
except KeyboardInterrupt:
    print("\nQuery interrupted by user.")