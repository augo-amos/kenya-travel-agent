#!/usr/bin/env python3
"""
Master script to run all scrapers and process data
"""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.basic_scraper import KenyaTravelScraper
from scrapers.advanced_scraper import AdvancedKenyaScraper
from scrapers.data_processor import DataProcessor

def main():
    """
    Run complete scraping pipeline
    """
    print("="*60)
    print(f"KENYA TRAVEL DATA SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # Ensure directories exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # STEP 1: Basic scraping
    print("\n[STEP 1] Running basic web scrapers...")
    basic_scraper = KenyaTravelScraper()
    
    # Kenyan destinations to scrape
    destinations = [
        {'name': 'Masai Mara', 'url': 'https://www.masaimara.com/'},
        {'name': 'Diani Beach', 'url': 'https://www.dianibeach.com/'},
        {'name': 'Amboseli', 'url': 'https://www.amboselipark.org/'},
        {'name': 'Nairobi National Park', 'url': 'https://www.kws.go.ke/content/nairobi-national-park'},
        {'name': 'Tsavo National Park', 'url': 'https://www.tsavonationalparkkenya.com/'},
        {'name': 'Lamu Island', 'url': 'https://www.lamu.org/'},
        {'name': 'Malindi', 'url': 'https://www.malindikenya.net/'},
        {'name': 'Mount Kenya', 'url': 'https://www.mountkenya.org/'}
    ]
    
    basic_data = basic_scraper.scrape_multiple(destinations)
    basic_file = basic_scraper.save_data(f"data/raw/basic_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print(f"✓ Basic scraping complete: {len(basic_data)} items")
    
    # STEP 2: Advanced scraping with Selenium
    print("\n[STEP 2] Running advanced scrapers (with Selenium)...")
    advanced_scraper = AdvancedKenyaScraper(headless=True)
    
    try:
        # Scrape TripAdvisor for key locations
        locations = ['Nairobi', 'Mombasa', 'Masai Mara', 'Diani', 'Amboseli']
        for location in locations:
            print(f"  Scraping TripAdvisor for {location}...")
            advanced_scraper.scrape_tripadvisor(location)
            time.sleep(3)
        
        # Scrape Wikipedia for Kenyan topics
        topics = [
            'Maasai_Mara',
            'Mount_Kenya',
            'Lamu',
            'Kenyan_cuisine',
            'Culture_of_Kenya',
            'History_of_Kenya',
            'Wildlife_of_Kenya',
            'Nairobi',
            'Mombasa',
            'Kisumu'
        ]
        
        for topic in topics:
            print(f"  Scraping Wikipedia for {topic}...")
            wiki_data = advanced_scraper.scrape_wikipedia(topic)
            if wiki_data:
                advanced_scraper.data.append(wiki_data)
            time.sleep(2)
        
        # Save advanced data
        advanced_file = advanced_scraper.save_all_data()
        print(f"✓ Advanced scraping complete: {len(advanced_scraper.data)} items")
        
    finally:
        advanced_scraper.close()
    
    # STEP 3: Process all data
    print("\n[STEP 3] Processing and cleaning data...")
    processor = DataProcessor()
    examples = processor.process_all_files('data/raw', 'data/processed')
    
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE!")
    print(f"Raw data files: {len(os.listdir('data/raw'))}")
    print(f"Processed examples: {len(examples)}")
    print(f"Data saved in: data/processed/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()