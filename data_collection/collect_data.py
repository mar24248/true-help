import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os

def scrape_website(start_url, max_pages=100, output_file="scraped_text.txt"):
    """
    Scrape visible text content from a website and crawl linked URLs, saving text to a file.
    
    Args:
        start_url (str): The starting URL to scrape.
        max_pages (int): Maximum number of pages to scrape (default: 100).
        output_file (str): File to save scraped text (default: "scraped_text.txt").
    """
    # Set to keep track of visited URLs to avoid duplicates
    visited_urls = set()
    # Queue of URLs to crawl
    urls_to_visit = [start_url]
    # Counter for scraped pages
    pages_scraped = 0

    # Open output file in append mode
    with open(output_file, "a", encoding="utf-8") as f:
        while urls_to_visit and pages_scraped < max_pages:
            # Get the next URL to scrape
            current_url = urls_to_visit.pop(0)
            
            # Skip if already visited
            if current_url in visited_urls:
                continue

            try:
                # Send HTTP GET request
                print(f"Scraping {current_url} ({pages_scraped + 1}/{max_pages})...")
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text(separator='\n', strip=True)
                
                # Write text content to file with a separator
                f.write(f"\n\n=== Content from {current_url} ===\n")
                f.write(text)
                f.write("\n")
                
                # Mark as visited
                visited_urls.add(current_url)
                pages_scraped += 1
                
                # Extract all links on the page
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    # Convert relative URLs to absolute URLs
                    full_url = urljoin(current_url, href)
                    
                    # Filter to stay within the same domain (optional)
                    if urlparse(full_url).netloc == urlparse(start_url).netloc:
                        if full_url not in visited_urls and full_url not in urls_to_visit:
                            urls_to_visit.append(full_url)
                
                # Be polite: avoid overwhelming the server
                time.sleep(1)
                
            except requests.RequestException as e:
                print(f"Failed to scrape {current_url}: {e}")
                continue
    
    print(f"Scraping complete! Scraped {pages_scraped} pages. Text content saved to {output_file}")

def main():
    # Configuration
    start_url = "https://ca.gov/lafires"
    max_pages = 100  # Configurable limit
    output_file = "scraped_text.txt"
    
    # Clear the output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Run the scraper
    scrape_website(start_url, max_pages, output_file)

if __name__ == "__main__":
    main()