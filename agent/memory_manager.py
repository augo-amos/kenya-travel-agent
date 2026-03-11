import json
import os
from datetime import datetime
from typing import List, Dict, Any
import hashlib

class ConversationMemory:
    """
    Manage conversation memory and context for the travel agent
    """
    
    def __init__(self, user_id: str = "default", storage_dir: str = "data/conversations"):
        self.user_id = user_id
        self.storage_dir = storage_dir
        self.conversations = []
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "user_preferences": {},
            "context": {}
        }
        
        # Ensure directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load previous conversations
        self._load_conversations()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_input = f"{self.user_id}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:10]
    
    def _load_conversations(self):
        """Load previous conversations from file"""
        filename = f"{self.storage_dir}/{self.user_id}_conversations.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
                print(f"Loaded {len(self.conversations)} previous conversations")
            except:
                self.conversations = []
    
    def _save_conversations(self):
        """Save conversations to file"""
        filename = f"{self.storage_dir}/{self.user_id}_conversations.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the current session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.current_session["messages"].append(message)
        
        # Extract preferences from user messages
        if role == "user":
            self._extract_preferences(content)
    
    def _extract_preferences(self, message: str):
        """Extract user preferences from message"""
        message_lower = message.lower()
        
        # Detect destination preferences
        destinations = ["masai mara", "diani", "nairobi", "mombasa", "amboseli", 
                       "tsavo", "lamu", "malindi", "nakuru", "naivasha"]
        
        for dest in destinations:
            if dest in message_lower:
                self.current_session["user_preferences"]["last_destination"] = dest
                self.current_session["user_preferences"]["interested_in"] = dest
                break
        
        # Detect budget preferences
        if "budget" in message_lower or "cheap" in message_lower or "affordable" in message_lower:
            self.current_session["user_preferences"]["budget"] = "budget"
        elif "luxury" in message_lower or "high-end" in message_lower:
            self.current_session["user_preferences"]["budget"] = "luxury"
        
        # Detect travel style
        if "safari" in message_lower:
            self.current_session["user_preferences"]["interest"] = "safari"
        elif "beach" in message_lower:
            self.current_session["user_preferences"]["interest"] = "beach"
        elif "culture" in message_lower or "tribe" in message_lower:
            self.current_session["user_preferences"]["interest"] = "culture"
    
    def get_context(self) -> Dict:
        """Get current context for the agent"""
        return {
            "preferences": self.current_session["user_preferences"],
            "recent_topics": self._get_recent_topics(),
            "session_duration": self._get_session_duration()
        }
    
    def _get_recent_topics(self) -> List[str]:
        """Extract recent conversation topics"""
        topics = []
        keywords = ["safari", "beach", "hotel", "restaurant", "transport", "price", 
                   "visa", "weather", "culture", "wildlife"]
        
        for msg in self.current_session["messages"][-5:]:  # Last 5 messages
            if msg["role"] == "user":
                msg_lower = msg["content"].lower()
                for keyword in keywords:
                    if keyword in msg_lower and keyword not in topics:
                        topics.append(keyword)
        
        return topics[-3:]  # Last 3 topics
    
    def _get_session_duration(self) -> str:
        """Calculate session duration"""
        if not self.current_session["messages"]:
            return "0 minutes"
        
        start = datetime.fromisoformat(self.current_session["start_time"])
        now = datetime.now()
        duration = now - start
        
        minutes = int(duration.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            return f"{hours} hours {minutes % 60} minutes"
    
    def end_session(self):
        """End current session and save"""
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["message_count"] = len(self.current_session["messages"])
        
        # Add to conversations list
        self.conversations.append(self.current_session)
        
        # Save to file
        self._save_conversations()
        
        # Start new session
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "user_preferences": {},
            "context": {}
        }
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on user preferences"""
        recommendations = []
        prefs = self.current_session["user_preferences"]
        
        if "interested_in" in prefs:
            dest = prefs["interested_in"]
            if dest == "masai mara":
                recommendations = [
                    "Consider visiting between July-October for the Great Migration",
                    "Hot air balloon safaris offer amazing views ($450/person)",
                    "Stay at a conservancy for night game drives"
                ]
            elif dest == "diani":
                recommendations = [
                    "December-March has the best beach weather",
                    "Try kitesurfing at Diani Beach - world-class conditions",
                    "Visit the Colobus Conservation to see monkeys"
                ]
            elif dest == "amboseli":
                recommendations = [
                    "Early morning game drives offer the best Kilimanjaro views",
                    "Look for large elephant herds - Amboseli is famous for them",
                    "Stay at a lodge with swamp views for constant wildlife"
                ]
        
        return recommendations
    
    def get_summary(self) -> str:
        """Get conversation summary"""
        if not self.conversations and not self.current_session["messages"]:
            return "No conversations yet"
        
        total_messages = sum(len(sess["messages"]) for sess in self.conversations)
        total_messages += len(self.current_session["messages"])
        
        sessions_count = len(self.conversations) + 1
        
        summary = f"Summary: {sessions_count} sessions, {total_messages} messages"
        
        # Add preferences if any
        if self.current_session["user_preferences"]:
            prefs = self.current_session["user_preferences"]
            summary += f"\nInterests: {', '.join(prefs.values())}"
        
        return summary


# Example usage
if __name__ == "__main__":
    # Test the memory manager
    memory = ConversationMemory(user_id="test_user")
    
    # Simulate conversation
    memory.add_message("user", "I want to visit Masai Mara next July")
    memory.add_message("assistant", "Great choice! July is perfect for the wildebeest migration.")
    memory.add_message("user", "What's the budget for a 4-day safari?")
    
    # Get context
    print("Context:", memory.get_context())
    print("\nRecommendations:", memory.get_recommendations())
    print("\nSummary:", memory.get_summary())
    
    # End session
    memory.end_session()