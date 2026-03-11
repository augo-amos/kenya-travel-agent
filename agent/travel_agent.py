#!/usr/bin/env python3
"""
Kenya Travel Agent - Full Version with LangChain
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# LangChain imports
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Local imports
from models.vector_store import TravelVectorStore

from dotenv import load_dotenv
load_dotenv()

class KenyaTravelAgent:
    """
    AI Travel Agent for Kenyan tourism - Full Version
    """
    
    def __init__(self, vector_store_path="data/embeddings/latest"):
        """
        Initialize the travel agent
        """
        print("="*60)
        print("INITIALIZING KENYA TRAVEL AGENT - FULL VERSION")
        print("="*60)
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        print("✓ Memory initialized")
        
        # Initialize embeddings
        print("\nLoading embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✓ Embeddings loaded")
        
        # Initialize vector store
        self.vector_store = None
        try:
            if os.path.exists(vector_store_path):
                self.vector_store = FAISS.load_local(
                    vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("✓ Knowledge base loaded")
            else:
                print(f"Vector store not found at {vector_store_path}")
                print("Please run: python models/vector_store.py")
        except Exception as e:
            print(f"Could not load vector store: {e}")
        
        # Initialize LLM with Flan-T5 (better for Q&A)
        print("\nInitializing AI model with Flan-T5...")
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
            
            model_name = "google/flan-t5-base"  # Better for Q&A tasks
            print(f"  Loading {model_name} (this may take a minute)...")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # Create pipeline for text2text-generation
            pipe = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True
            )
            
            self.llm = HuggingFacePipeline(pipeline=pipe)
            print("✓ AI model loaded")
        except Exception as e:
            print(f"Could not load AI model: {e}")
            self.llm = None
        
        # Create QA chain if everything loaded
        self.qa_chain = self._create_qa_chain()
        
        # Conversation history
        self.conversation_history = []
        
        print("\n✓ Travel Agent ready!")
        print("="*60)
    
    def _create_qa_chain(self):
        """Create the QA chain"""
        if not self.vector_store or not self.llm:
            return None
        
        # Improved prompt template for instruct models
        prompt_template = """You are an expert Kenyan travel assistant. Answer the question based on the context provided.

Context: {context}

Question: {question}

Answer the question in a helpful, friendly way. If the context doesn't contain the answer, say you don't have that information.

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create chain
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        return chain
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Ask a question and get a tailored response"""
        print(f"\nTourist: {question}")
        
        if self.qa_chain:
            # Get response from vector store + LLM
            result = self.qa_chain.invoke({"query": question})
            answer = result['result']
            sources = [doc.metadata.get('source', 'unknown') for doc in result['source_documents']]
            print(f"Agent: {answer[:150]}...")
        else:
            # Fallback to rule-based responses
            answer = self._fallback_response(question)
            sources = []
            print(f"Agent: {answer[:150]}...")
        
        # Store in history
        self.conversation_history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def _fallback_response(self, question: str) -> str:
        """Fallback responses when vector store isn't available"""
        q = question.lower()
        
        if "masai mara" in q:
            return "The Masai Mara is Kenya's most famous game reserve, known for its spectacular wildlife and the Great Migration. To give you specific, detailed information, please run the vector store first with: python models/vector_store.py"
        elif "diani" in q or "beach" in q:
            return "Diani Beach is a stunning coastal destination with white sands and turquoise waters. For detailed information about accommodations and activities, please run: python models/vector_store.py"
        elif "amboseli" in q:
            return "Amboseli National Park is famous for its large elephant herds and stunning views of Mount Kilimanjaro. For specific information about wildlife and best visiting times, please run: python models/vector_store.py"
        elif "nairobi" in q:
            return "Nairobi National Park is unique for being a wildlife park so close to a capital city. To get detailed information about game viewing and access, please run: python models/vector_store.py"
        elif "tsavo" in q:
            return "Tsavo is Kenya's largest national park, divided into Tsavo East and West. For specific details about the parks' attractions and accommodations, please run: python models/vector_store.py"
        elif "lamu" in q:
            return "Lamu is a historic Swahili island town known for its rich culture and traditional architecture. For detailed information about getting there and places to stay, please run: python models/vector_store.py"
        elif "malindi" in q:
            return "Malindi is a coastal town with beautiful beaches, historical sites, and the nearby Watamu Marine Park. For specific information, please run: python models/vector_store.py"
        elif "mountain" in q or "mount kenya" in q:
            return "Mount Kenya is Africa's second-highest peak and offers incredible hiking and climbing opportunities. For detailed route information and preparation tips, please run: python models/vector_store.py"
        else:
            return "I can give you tailored responses once the knowledge base is loaded with your scraped travel data. Please run: python models/vector_store.py"
    
    def chat(self):
        """Interactive chat mode"""
        print("\n" + "="*60)
        print("KENYA TRAVEL AGENT - Interactive Mode")
        print("="*60)
        print("Type 'exit' to quit\n")
        
        while True:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['exit', 'quit']:
                print("\nAgent: Kwaheri! Goodbye!")
                break
            
            if question:
                result = self.ask(question)
                print(f"\nAgent: {result['answer']}")
                if result['sources']:
                    print(f"\nSources: {', '.join(result['sources'][:3])}")

# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Kenya Travel Agent - Full Version')
    parser.add_argument('--query', type=str, help='Single query mode')
    
    args = parser.parse_args()
    
    agent = KenyaTravelAgent()
    
    if args.query:
        result = agent.ask(args.query)
        print(f"\nAnswer: {result['answer']}")
        if result['sources']:
            print(f"\nSources: {', '.join(result['sources'][:3])}")
    else:
        agent.chat()