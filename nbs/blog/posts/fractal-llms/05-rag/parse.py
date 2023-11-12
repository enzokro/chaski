import re
import time
import html
import json
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def fetch_page_content(url):
    """
    Fetch the HTML content of a webpage

    :param url: str, the URL of the webpage
    :return: str, the HTML content of the webpage
    """
    try:
        # Send a HTTP request to the URL
        response = requests.get(url)
    except requests.RequestException as e:
        # If there was an issue with the request, print the error
        print(f"An error occurred: {e}")
        return None
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve content from {url}, status code: {response.status_code}")
        return None


def parse_html(html_content):
    """
    Parse the HTML content of a webpage

    :param html_content: str, the HTML content of the webpage
    :return: BeautifulSoup object, the parsed HTML tree
    """
    try:
        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html_content, 'lxml')  # Using lxml's HTML parser
        return soup
    except Exception as e:
        # If there is any exception while parsing the HTML, print the error
        print(f"An error occurred while parsing HTML: {e}")
        return None


def extract_main_content(soup):
    """
    Extract the main content of a webpage from the parsed HTML

    :param soup: BeautifulSoup object, the parsed HTML tree
    :return: str, the extracted main content of the webpage
    """
    try:
        # Find the element(s) containing the main content based on inspection of the website structure
        # This is a hypothetical class name; you'll need to replace this with the actual class name or other selectors relevant to your website.
        main_content = soup.find('article', role='main')  

        if main_content:
            return main_content.get_text(separator='\n', strip=True)  # Extracts text while preserving line breaks
        else:
            print("Failed to find main content section")
            return None
    except Exception as e:
        # If there is any exception while extracting content, print the error
        print(f"An error occurred while extracting main content: {e}")
        return None


def clean_and_format_text(text):
    """
    Clean and format the extracted text

    :param text: str, the extracted text content of the webpage
    :return: str, the cleaned and formatted text
    """
    try:
        # Decode HTML entities
        text = html.unescape(text)

        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)

        # Clean up stray gapped spaces
        text = re.sub(r' \.', '\.', text)

        # Clean up spaces before periods, commas, and other punctuation marks
        text = re.sub(r'\s+([.,;?!])', r'\1', text)

        # Optionally, remove any special characters you don't want
        # text = re.sub(r'[^\w\s]', '', text)

        # Trim whitespace at the start and end
        text = text.strip()

        return text
    except Exception as e:
        # If there is any exception during cleaning, print the error
        print(f"An error occurred while cleaning and formatting text: {e}")
        return None
    

def find_all_links(url, domain, visited=None):
    """
    Recursively find all unique links within a domain.

    :param url: str, the URL to start crawling from
    :param domain: str, the domain to restrict the crawling
    :param visited: set, a set of URLs already visited
    :return: set, a set of unique URLs found
    """
    if visited is None:
        visited = set()

    # Add the initial URL to the visited set
    visited.add(str(url))

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        # Find all links on the page
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute URLs
            if href.startswith("/") or not href.startswith("http"):
                href = urljoin(domain, href)

            # Parse the URL to remove query parameters, fragments, etc.
            href_parsed = urlparse(href)
            href = href_parsed.scheme + "://" + href_parsed.netloc + href_parsed.path

            # We're only interested in links that are within the specified domain
            if href not in visited and href.startswith(domain):
                visited.add(str(href))
                print(f"Found a new page: {href}")

                # Recursively search for links on the newly found page
                # You might want to add some delay here with time.sleep
                time.sleep(1)  # Delay to respect server load
                find_all_links(href, domain, visited)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    return visited


def keep_valid_links(domain: str, links_path: str) -> None:
    """Quick check to only keep valid links that don't return a 404 error
    
    :param domain: str, the domain to restrict the crawling
    :param links_path: str, path to the json file containing the links
    :return: None
    """
    with open(links_path, 'r') as f:
        links = json.load(f)

    valid_links = []

    for link in links:
        if link.startswith(domain):
            if requests.get(link).status_code == 200:
                valid_links.append(link)

    with open('valid_links.json', 'w') as f:
        json.dump(valid_links, f, indent=4)

    return valid_links


def extract_text_from_url(url: str) -> str:
    """Extract text from a webpage
    
    :param url: str, the URL of the webpage
    :return: str, the extracted text
    """
    html_content = fetch_page_content(url)
    soup = parse_html(html_content)
    main_content = extract_main_content(soup)
    clean_text = clean_and_format_text(main_content)
    return clean_text



if __name__ == '__main__':

    # website to parse and extract text from
    url = "https://diataxis.fr/"

    # find all links for this website
    all_links = find_all_links(url, url)
    print(f"Found {len(all_links)} unique links.")
    # save out the links for convenience
    with open('links.json', 'w') as f:
        json.dump(list(all_links), f, indent=4)

    # small sanity check to only keep valid links
    valid_links = keep_valid_links(url, 'links.json')

    # extract text from all links, including the home page
    for link in valid_links:
        try:
            text = extract_text_from_url(link)
            print(f"Extracted {len(text)} characters from {link}")
            with open(f"content/{link.split('/')[-2]}.txt", 'w') as f:
                f.write(text)
        except:
            print(f"Failed to extract text from {link}")
            continue
