#!/usr/bin/env python3
"""
Monitoring script for Kenya Travel Agent
"""

import requests
import time
import json
from datetime import datetime
import os
import sys
from collections import deque

class TravelAgentMonitor:
    """Monitor the travel agent's performance"""
    
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.metrics = {
            'response_times': deque(maxlen=100),
            'errors': deque(maxlen=100),
            'queries': deque(maxlen=1000)
        }
        
    def check_health(self):
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"API Healthy - Active sessions: {data.get('active_sessions', 0)}")
                return True
            else:
                print(f"API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"API not reachable: {e}")
            return False
    
    def test_query(self, query):
        """Test a single query"""
        try:
            # First initialize session
            init_response = requests.post(f"{self.api_url}/init", 
                                         json={"user_id": "monitor"})
            
            if init_response.status_code != 200:
                print(f"Failed to initialize session: {init_response.text}")
                return None
            
            session_id = init_response.json()['session_id']
            
            # Send query
            start_time = time.time()
            
            response = requests.post(f"{self.api_url}/chat", json={
                "session_id": session_id,
                "message": query
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Record metrics
                self.metrics['response_times'].append(response_time)
                self.metrics['queries'].append({
                    'query': query,
                    'time': response_time,
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'response_time': response_time,
                    'response': data['response'][:100] + "...",
                    'sources': len(data.get('sources', []))
                }
            else:
                self.metrics['errors'].append({
                    'query': query,
                    'error': response.text,
                    'timestamp': datetime.now().isoformat()
                })
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            self.metrics['errors'].append({
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_queries(self, queries, interval=1):
        """Run multiple queries with interval"""
        print(f"\n Running {len(queries)} test queries...")
        print("="*60)
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Query: {query}")
            
            result = self.test_query(query)
            
            if result and result['success']:
                print(f"  Response time: {result['response_time']:.2f}s")
                print(f"  Preview: {result['response']}")
                print(f"  Sources: {result['sources']}")
            else:
                print(f"  Failed: {result.get('error', 'Unknown error')}")
            
            if i < len(queries):
                time.sleep(interval)
    
    def generate_report(self):
        """Generate performance report"""
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        
        if self.metrics['response_times']:
            times = list(self.metrics['response_times'])
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            print(f"\n Response Times:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Fastest: {min_time:.2f}s")
            print(f"  Slowest: {max_time:.2f}s")
            print(f"  Total queries: {len(times)}")
        
        if self.metrics['errors']:
            print(f"\n Errors: {len(self.metrics['errors'])}")
            for error in list(self.metrics['errors'])[-5:]:  # Last 5 errors
                print(f"  {error['query']}: {error['error'][:50]}")
        else:
            print(f"\nNo errors recorded")
        
        print("\n" + "="*60)
    
    def continuous_monitor(self, interval=60):
        """Continuous monitoring"""
        print(f"Starting continuous monitoring (refresh every {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}]")
                
                # Check health
                if self.check_health():
                    # Run a test query
                    test_queries = [
                        "Tell me about Masai Mara",
                        "What's the weather in Kenya?",
                        "How much is a safari?"
                    ]
                    import random
                    test_query = random.choice(test_queries)
                    
                    result = self.test_query(test_query)
                    if result and result['success']:
                        print(f"  Test query: {result['response_time']:.2f}s")
                
                # Generate quick stats
                self.generate_report()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nFinal Report:")
            self.generate_report()

def main():
    """Main monitoring function"""
    monitor = TravelAgentMonitor()
    
    # Check if API is running
    if not monitor.check_health():
        print("\nAPI is not running. Please start the API first:")
        print("  Flask: python deployment/flask_api.py")
        print("  Docker: docker-compose up -d")
        sys.exit(1)
    
    # Test queries
    test_queries = [
        "What is the best time to visit Kenya?",
        "Tell me about safaris in Masai Mara",
        "How much does accommodation cost in Diani?",
        "What should I know before traveling to Kenya?",
        "Recommend a 7-day Kenya itinerary",
        "Is Kenya safe for solo travelers?",
        "What wildlife can I see in Amboseli?",
        "Tell me about Kenyan food",
        "How do I get from Nairobi to Mombasa?",
        "What cultural experiences are there in Kenya?"
    ]
    
    print("\nKenya Travel Agent Monitor")
    print("="*60)
    
    # Ask for mode
    print("\nSelect mode:")
    print("1. Run test queries")
    print("2. Continuous monitoring")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        monitor.run_queries(test_queries)
        monitor.generate_report()
    elif choice == '2':
        interval = input("Monitoring interval in seconds (default 60): ").strip()
        interval = int(interval) if interval else 60
        monitor.continuous_monitor(interval)
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()