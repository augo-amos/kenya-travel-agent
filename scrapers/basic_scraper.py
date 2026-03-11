import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class KenyaTravelScraper:
    """
    Basic scraper for Kenyan travel websites
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []
        
    def scrape_website(self, url, destination_name):
        """
        Scrape a single website
        """
        try:
            print(f"Scraping {destination_name} from {url}")
            
            # Send request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract paragraphs (more structured content)
            paragraphs = []
            for p in soup.find_all('p'):
                p_text = p.get_text().strip()
                if p_text and len(p_text) > 50:  # Filter short paragraphs
                    paragraphs.append(p_text)
            
            # Create data entry
            entry = {
                'destination': destination_name,
                'url': url,
                'scrape_date': datetime.now().isoformat(),
                'full_text': text[:5000],  # Limit text size
                'paragraphs': paragraphs[:20],  # Limit paragraphs
                'title': soup.title.string if soup.title else 'No title'
            }
            
            self.data.append(entry)
            return entry
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_multiple(self, websites):
        """
        Scrape multiple websites
        """
        for website in websites:
            result = self.scrape_website(website['url'], website['name'])
            time.sleep(2)  # Be respectful to servers
        return self.data
    
    def save_data(self, filename=None):
        """
        Save scraped data to JSON file
        """
        if filename is None:
            filename = f"data/raw/scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {filename}")
        return filename

# Example usage
if __name__ == "__main__":
    # List of Kenyan travel websites to scrape
    websites_to_scrape = [
        {
            'name': 'Masai Mara',
            'url': 'https://www.masaimara.com/'
        },
        {
            'name': 'Diani Beach',
            'url': 'https://www.dianibeach.com/'
        },
        {
            'name': 'Amboseli National Park',
            'url': 'https://www.amboselipark.org/'
        }
    ]
    
    # Initialize scraper
    scraper = KenyaTravelScraper()
    
    # Scrape websites
    data = scraper.scrape_multiple(websites_to_scrape)
    
    # Save data
    scraper.save_data()
    
    print(f"Scraped {len(data)} websites successfully!")