import unittest
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.travel_agent import KenyaTravelAgent
from agent.memory_manager import ConversationMemory
from models.vector_store import TravelVectorStore

class TestKenyaTravelAgent(unittest.TestCase):
    """Test cases for Kenya Travel Agent"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print("Setting up Travel Agent Tests")
        print("="*60)
        
        # Initialize agent with HuggingFace (free)
        cls.agent = KenyaTravelAgent(llm_type="huggingface")
        
        # Initialize memory
        cls.memory = ConversationMemory(user_id="test_user")
        
        # Test queries
        cls.test_queries = [
            "What is the best time to visit Masai Mara?",
            "Tell me about Diani Beach",
            "How much does a safari cost?",
            "What wildlife can I see in Amboseli?",
            "Do I need a visa for Kenya?",
            "What should I pack for a Kenya trip?"
        ]
    
    def test_01_agent_initialization(self):
        """Test that agent initializes correctly"""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.llm)
        print("✓ Agent initialization test passed")
    
    def test_02_basic_query(self):
        """Test basic query response"""
        query = "Tell me about Nairobi"
        result = self.agent.ask(query)
        
        self.assertIsNotNone(result)
        self.assertIn('answer', result)
        self.assertTrue(len(result['answer']) > 0)
        
        print(f"✓ Basic query test passed: {query}")
        print(f"  Response preview: {result['answer'][:100]}...")
    
    def test_03_multiple_queries(self):
        """Test multiple queries in sequence"""
        for i, query in enumerate(self.test_queries[:3]):
            result = self.agent.ask(query)
            self.assertIsNotNone(result)
            self.assertIn('answer', result)
            print(f"✓ Query {i+1} passed: {query[:30]}...")
    
    def test_04_memory_management(self):
        """Test conversation memory"""
        # Add messages
        self.memory.add_message("user", "I want to visit Masai Mara")
        self.memory.add_message("assistant", "Great choice! When are you planning to go?")
        self.memory.add_message("user", "Next July")
        
        # Get context
        context = self.memory.get_context()
        self.assertIsNotNone(context)
        self.assertIn('preferences', context)
        
        # Get recommendations
        recommendations = self.memory.get_recommendations()
        self.assertIsInstance(recommendations, list)
        
        print("✓ Memory management test passed")
        print(f"  Preferences: {context['preferences']}")
    
    def test_05_vector_store_search(self):
        """Test vector store search functionality"""
        if self.agent.vector_store and self.agent.vector_store.vector_store:
            query = "Kenyan beaches"
            results = self.agent.vector_store.search_similar(query, k=2)
            self.assertIsNotNone(results)
            self.assertTrue(len(results) > 0)
            print(f"✓ Vector store search test passed: found {len(results)} results")
        else:
            print("⚠️ Vector store not available, skipping test")
    
    def test_06_response_quality(self):
        """Test response quality for common queries"""
        quality_checks = {
            "Hello": ["hello", "jambo", "hi", "welcome"],
            "safari cost": ["cost", "price", "budget", "ksh", "dollar"],
            "visa requirements": ["visa", "eVisa", "passport", "entry"]
        }
        
        for query, keywords in quality_checks.items():
            result = self.agent.ask(query)
            response = result['answer'].lower()
            
            # Check if at least one keyword is present
            keyword_found = any(keyword in response for keyword in keywords)
            self.assertTrue(keyword_found, 
                          f"Response for '{query}' missing keywords: {keywords}")
        
        print("✓ Response quality test passed")
    
    def test_07_error_handling(self):
        """Test error handling"""
        # Empty query
        result = self.agent.ask("")
        self.assertIsNotNone(result)
        
        # Very long query
        long_query = "a" * 1000
        result = self.agent.ask(long_query)
        self.assertIsNotNone(result)
        
        print("✓ Error handling test passed")

def run_performance_test():
    """Run performance benchmarks"""
    print("\n" + "="*60)
    print("Running Performance Tests")
    print("="*60)
    
    agent = KenyaTravelAgent(llm_type="huggingface")
    test_queries = [
        "Tell me about Masai Mara",
        "Beaches in Kenya",
        "Safari prices",
        "Best hotels in Nairobi",
        "Kenyan food"
    ]
    
    import time
    times = []
    
    for query in test_queries:
        start = time.time()
        result = agent.ask(query)
        end = time.time()
        
        response_time = end - start
        times.append(response_time)
        
        print(f"Query: {query[:20]}...")
        print(f"  Response time: {response_time:.2f}s")
        print(f"  Response length: {len(result['answer'])} chars")
        print(f"  Sources: {len(result.get('sources', []))}")
        print()
    
    avg_time = sum(times) / len(times)
    print(f"Average response time: {avg_time:.2f}s")
    print(f"Fastest: {min(times):.2f}s")
    print(f"Slowest: {max(times):.2f}s")
    
    return avg_time

if __name__ == '__main__':
    print("\n🔍 Running Travel Agent Tests")
    print("="*60)
    
    # Run unit tests
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Run performance test
    run_performance_test()