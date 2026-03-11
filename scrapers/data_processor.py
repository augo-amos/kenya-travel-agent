import json
import pandas as pd
import re
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DataProcessor:
    """
    Process and clean scraped data
    """
    
    def __init__(self, raw_data_path=None):
        self.raw_data_path = raw_data_path
        self.processed_data = []
        
    def load_raw_data(self, filepath):
        """
        Load raw JSON data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clean_text(self, text):
        """
        Clean text data
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\']', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_entities(self, text):
        """
        Extract basic entities from text (simplified)
        """
        entities = {
            'locations': [],
            'activities': [],
            'prices': []
        }
        
        # Find potential prices
        price_pattern = r'\$?\d+(?:\.\d{2})?\s*(?:USD|KES|shillings)?'
        entities['prices'] = re.findall(price_pattern, text, re.IGNORECASE)
        
        # Find potential locations (capitalized words)
        location_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_locations = re.findall(location_pattern, text)
        entities['locations'] = list(set(potential_locations))[:10]
        
        return entities
    
    def create_training_examples(self, data):
        """
        Convert scraped data into training examples for the LLM
        """
        examples = []
        
        for item in data:
            # Create Q&A pairs from content
            if 'paragraphs' in item and item['paragraphs']:
                for i, para in enumerate(item['paragraphs']):
                    if len(para) > 100:  # Only use substantial paragraphs
                        # Create a question based on the paragraph
                        question = self.generate_question(para, item)
                        
                        example = {
                            'id': f"{item.get('destination', 'unknown')}_{i}",
                            'source': item.get('source', 'web'),
                            'destination': item.get('destination', ''),
                            'context': para,
                            'question': question,
                            'answer': para,
                            'metadata': {
                                'url': item.get('url', ''),
                                'scrape_date': item.get('scrape_date', ''),
                                'type': item.get('type', 'general')
                            }
                        }
                        examples.append(example)
        
        return examples
    
    def generate_question(self, text, item):
        """
        Generate a plausible question for the text
        """
        # Simple question generation based on content type
        text_lower = text.lower()
        
        if 'price' in text_lower or 'cost' in text_lower:
            return f"What are the prices for visiting {item.get('destination', 'this place')}?"
        elif 'hour' in text_lower or 'open' in text_lower:
            return f"What are the opening hours for {item.get('destination', 'this attraction')}?"
        elif 'location' in text_lower or 'where' in text_lower:
            return f"Where is {item.get('destination', 'this place')} located?"
        elif 'best time' in text_lower or 'when' in text_lower:
            return f"What is the best time to visit {item.get('destination', 'this place')}?"
        else:
            return f"Tell me about {item.get('destination', 'this travel destination')}."
    
    def create_csv_dataset(self, examples, filename):
        """
        Create CSV dataset for training
        """
        df = pd.DataFrame(examples)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        df.to_csv(filename, index=False)
        print(f"Created CSV dataset with {len(df)} examples at {filename}")
        return filename
    
    def create_jsonl_dataset(self, examples, filename):
        """
        Create JSONL dataset for fine-tuning
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            for example in examples:
                # Format for fine-tuning
                fine_tune_example = {
                    "messages": [
                        {"role": "system", "content": "You are a helpful Kenyan travel assistant."},
                        {"role": "user", "content": example['question']},
                        {"role": "assistant", "content": example['answer']}
                    ]
                }
                f.write(json.dumps(fine_tune_example) + '\n')
        
        print(f"Created JSONL dataset with {len(examples)} examples at {filename}")
        return filename
    
    def process_all_files(self, raw_data_dir='data/raw', processed_dir='data/processed'):
        """
        Process all raw data files
        """
        all_examples = []
        
        # Get all JSON files in raw data directory
        raw_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
        
        for raw_file in raw_files:
            print(f"Processing {raw_file}...")
            
            # Load raw data
            data = self.load_raw_data(os.path.join(raw_data_dir, raw_file))
            
            # Clean and process
            for item in data:
                if isinstance(item, dict):
                    # Clean text fields
                    for key in ['full_text', 'description', 'paragraphs']:
                        if key in item:
                            if isinstance(item[key], str):
                                item[key] = self.clean_text(item[key])
                            elif isinstance(item[key], list):
                                item[key] = [self.clean_text(t) for t in item[key]]
            
            # Create training examples
            examples = self.create_training_examples(data)
            all_examples.extend(examples)
        
        # Save processed data
        if all_examples:
            # Save as CSV
            csv_file = os.path.join(processed_dir, f'training_data_{datetime.now().strftime("%Y%m%d")}.csv')
            self.create_csv_dataset(all_examples, csv_file)
            
            # Save as JSONL for fine-tuning
            jsonl_file = os.path.join(processed_dir, f'fine_tune_data_{datetime.now().strftime("%Y%m%d")}.jsonl')
            self.create_jsonl_dataset(all_examples, jsonl_file)
            
            # Save processed examples as JSON
            processed_json = os.path.join(processed_dir, f'processed_{datetime.now().strftime("%Y%m%d")}.json')
            with open(processed_json, 'w', encoding='utf-8') as f:
                json.dump(all_examples, f, ensure_ascii=False, indent=2)
            
            print(f"Total processed examples: {len(all_examples)}")
        
        return all_examples

# Run processing
if __name__ == "__main__":
    processor = DataProcessor()
    examples = processor.process_all_files()
    print(f"Data processing complete! Created {len(examples)} examples.")