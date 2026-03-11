import os
import sys
import json
from typing import List, Dict, Any
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# LangChain imports - CORRECT for version 0.1.0
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class TravelVectorStore:
    """Create and manage vector embeddings"""
    
    def __init__(self):
        print("Initializing vector store...")
        
        # Use HuggingFace embeddings (free)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        self.vector_store = None
    
    def load_documents(self, data_dir="data/processed"):
        """Load and split documents"""
        documents = []
        
        # Find all JSON files
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        for json_file in json_files:
            filepath = os.path.join(data_dir, json_file)
            print(f"Loading {json_file}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to documents
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        # Extract text content
                        text = item.get('context', '') or item.get('full_text', '') or item.get('description', '')
                        if text:
                            doc = Document(
                                page_content=text,
                                metadata={
                                    'source': item.get('source', 'unknown'),
                                    'destination': item.get('destination', 'unknown'),
                                    'file': json_file
                                }
                            )
                            documents.append(doc)
        
        print(f"Loaded {len(documents)} documents")
        
        # Split documents
        split_docs = self.text_splitter.split_documents(documents)
        print(f"Split into {len(split_docs)} chunks")
        
        return split_docs
    
    def create_vector_store(self, documents: List[Document], save_path: str = None):
        """Create FAISS vector store"""
        print("Creating embeddings (this may take a few minutes)...")
        
        self.vector_store = FAISS.from_documents(
            documents,
            self.embeddings
        )
        
        print(f"✓ Created vector store with {self.vector_store.index.ntotal} vectors")
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self.vector_store.save_local(save_path)
            print(f"✓ Saved to {save_path}")
        
        return self.vector_store
    
    def load_vector_store(self, path: str):
        """Load existing vector store"""
        self.vector_store = FAISS.load_local(
            path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"✓ Loaded vector store from {path}")
        return self.vector_store

# Main execution
if __name__ == "__main__":
    vs = TravelVectorStore()
    
    # Check if processed data exists
    if os.path.exists("data/processed") and os.listdir("data/processed"):
        documents = vs.load_documents()
        if documents:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            vs.create_vector_store(documents, f"data/embeddings/vector_store_{timestamp}")
            # Also save as latest
            vs.create_vector_store(documents, "data/embeddings/latest")
    else:
        print("No processed data found. Please run scrapers first:")
        print("python scrapers/run_scrapers.py")