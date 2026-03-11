from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AdvancedKenyaScraper:
    """
    Advanced scraper using Selenium for JavaScript-heavy websites
    """
    
    def __init__(self, headless=True):
        """
        Initialize the scraper with Chrome options
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set up the driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.data = []
        
    def scrape_tripadvisor(self, location):
        """
        Scrape TripAdvisor for reviews and attractions
        """
        try:
            # Construct search URL
            search_url = f"https://www.tripadvisor.com/Search?q={location.replace(' ', '+')}+Kenya"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Find attraction links
            attractions = []
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="Attraction"]')[:5]
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and 'Attraction' in href:
                        attractions.append(href)
                except:
                    continue
            
            # Scrape each attraction
            for attraction_url in attractions:
                attraction_data = self.scrape_attraction_page(attraction_url)
                if attraction_data:
                    self.data.append(attraction_data)
                    
        except Exception as e:
            print(f"Error scraping TripAdvisor for {location}: {e}")
    
    def scrape_attraction_page(self, url):
        """
        Scrape individual attraction page
        """
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # Wait for content to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract attraction name
            name_elem = soup.find('h1', {'data-automation': 'mainH1'})
            name = name_elem.text.strip() if name_elem else 'Unknown'
            
            # Extract description
            desc_elem = soup.find('div', {'class': 'fIrGe'})
            description = desc_elem.text.strip() if desc_elem else ''
            
            # Extract reviews
            reviews = []
            review_elems = soup.find_all('div', {'class': 'review-container'})[:5]
            
            for review in review_elems:
                review_text = review.find('q', {'class': 'review-text'})
                if review_text:
                    reviews.append(review_text.text.strip())
            
            # Extract practical info
            practical_info = {}
            info_sections = soup.find_all('div', {'class': 'section'})
            for section in info_sections:
                heading = section.find('h2')
                if heading and 'practical' in heading.text.lower():
                    practical_info[heading.text] = section.text
            
            return {
                'source': 'TripAdvisor',
                'type': 'attraction',
                'name': name,
                'description': description,
                'reviews': reviews,
                'practical_info': practical_info,
                'url': url,
                'scrape_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error scraping attraction {url}: {e}")
            return None
    
    def scrape_instagram_hashtag(self, hashtag, max_posts=10):
        """
        Scrape Instagram posts by hashtag (requires login in real implementation)
        Note: This is a simplified version - actual Instagram scraping requires authentication
        """
        try:
            # This is a placeholder - Instagram scraping requires proper authentication
            # Use Instagram API or third-party services for production
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            self.driver.get(url)
            time.sleep(3)
            
            # Scroll to load more posts
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract post data (simplified)
            posts = []
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article a')[:max_posts]
            
            for post in post_elements:
                try:
                    post.click()
                    time.sleep(2)
                    
                    # Extract caption
                    caption_elem = self.driver.find_element(By.CSS_SELECTOR, 'div.C4VMK span')
                    caption = caption_elem.text if caption_elem else ''
                    
                    posts.append({
                        'source': 'Instagram',
                        'hashtag': hashtag,
                        'caption': caption[:500],
                        'scrape_date': datetime.now().isoformat()
                    })
                    
                    # Close modal
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="Close"]')
                    close_btn.click()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error extracting post: {e}")
                    continue
            
            self.data.extend(posts)
            
        except Exception as e:
            print(f"Error scraping Instagram hashtag #{hashtag}: {e}")
    
    def scrape_wikipedia(self, topic):
        """
        Scrape Wikipedia for Kenyan topics
        """
        try:
            url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
            self.driver.get(url)
            time.sleep(2)
            
            # Wait for content
            self.wait.until(EC.presence_of_element_located((By.ID, "content")))
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            
            if content_div:
                # Get paragraphs
                paragraphs = []
                for p in content_div.find_all('p')[:10]:
                    p_text = p.get_text().strip()
                    if p_text and len(p_text) > 50:
                        paragraphs.append(p_text)
                
                # Get sections
                sections = []
                for heading in content_div.find_all(['h2', 'h3'])[:5]:
                    section_title = heading.get_text().strip()
                    section_content = []
                    
                    next_elem = heading.find_next_sibling()
                    while next_elem and next_elem.name not in ['h2', 'h3']:
                        if next_elem.name == 'p':
                            section_content.append(next_elem.get_text().strip())
                        next_elem = next_elem.find_next_sibling()
                    
                    sections.append({
                        'title': section_title,
                        'content': section_content[:5]
                    })
                
                return {
                    'source': 'Wikipedia',
                    'topic': topic,
                    'paragraphs': paragraphs,
                    'sections': sections,
                    'url': url,
                    'scrape_date': datetime.now().isoformat()
                }
            
        except Exception as e:
            print(f"Error scraping Wikipedia for {topic}: {e}")
            return None
    
    def close(self):
        """
        Close the browser
        """
        self.driver.quit()
    
    def save_all_data(self):
        """
        Save all collected data to JSON
        """
        filename = f"data/raw/advanced_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.data)} items to {filename}")
        return filename

# Example usage
if __name__ == "__main__":
    scraper = AdvancedKenyaScraper(headless=True)
    
    try:
        # Scrape TripAdvisor for Nairobi
        print("Scraping TripAdvisor...")
        scraper.scrape_tripadvisor("Nairobi")
        
        # Scrape Wikipedia for Kenyan topics
        print("Scraping Wikipedia...")
        kenyan_topics = [
            "Maasai_Mara",
            "Mount_Kenya",
            "Lamu_Island",
            "Kenyan_cuisine",
            "Culture_of_Kenya"
        ]
        
        for topic in kenyan_topics:
            print(f"Scraping Wikipedia: {topic}")
            data = scraper.scrape_wikipedia(topic)
            if data:
                scraper.data.append(data)
            time.sleep(2)
        
        # Save all data
        scraper.save_all_data()
        
    finally:
        scraper.close()