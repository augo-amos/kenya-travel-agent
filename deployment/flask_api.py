from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import os
import uuid
from datetime import timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.travel_agent import KenyaTravelAgent
from agent.memory_manager import ConversationMemory

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
app.permanent_session_lifetime = timedelta(hours=1)
CORS(app)

# Store agents and memories (in production, use Redis)
agents = {}
memories = {}

@app.route('/')
def home():
    return jsonify({
        "message": "Kenya Travel Agent API",
        "version": "1.0",
        "endpoints": {
            "/init": "POST - Initialize a new agent session",
            "/chat": "POST - Send a message",
            "/history": "GET - Get conversation history",
            "/recommendations": "GET - Get personalized recommendations",
            "/destinations": "GET - List popular destinations",
            "/reset": "POST - Reset session"
        }
    })

@app.route('/init', methods=['POST'])
def initialize_agent():
    """Initialize a new travel agent session"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', str(uuid.uuid4()))
        llm_type = data.get('llm_type', 'huggingface')
        
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # Initialize agent and memory
        agent = KenyaTravelAgent(llm_type=llm_type)
        memory = ConversationMemory(user_id=user_id)
        
        # Store in dictionaries
        agents[session_id] = agent
        memories[session_id] = memory
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "message": "Agent initialized successfully"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Send a message to the agent"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return jsonify({"success": False, "error": "session_id and message required"}), 400
        
        if session_id not in agents:
            return jsonify({"success": False, "error": "Session not found. Call /init first"}), 404
        
        # Get agent and memory
        agent = agents[session_id]
        memory = memories[session_id]
        
        # Add to memory
        memory.add_message("user", message)
        
        # Get response
        result = agent.ask(message)
        
        # Add to memory
        memory.add_message("assistant", result["answer"], 
                          {"sources": [doc.metadata.get('source', 'unknown') for doc in result["sources"]]})
        
        # Format sources for response
        sources = []
        for doc in result["sources"]:
            sources.append({
                "content": doc.page_content[:200] + "...",
                "source": doc.metadata.get('source', 'unknown'),
                "destination": doc.metadata.get('destination', 'unknown')
            })
        
        return jsonify({
            "success": True,
            "response": result["answer"],
            "sources": sources,
            "context": memory.get_context()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "session_id required"}), 400
        
        if session_id not in memories:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        memory = memories[session_id]
        
        return jsonify({
            "success": True,
            "history": memory.current_session["messages"],
            "summary": memory.get_summary()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized recommendations"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "session_id required"}), 400
        
        if session_id not in memories:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        memory = memories[session_id]
        recommendations = memory.get_recommendations()
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "preferences": memory.current_session["user_preferences"]
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/destinations', methods=['GET'])
def get_destinations():
    """Get list of popular destinations"""
    destinations = {
        "masai_mara": {
            "name": "Masai Mara National Reserve",
            "type": "Safari",
            "best_time": "July-October",
            "highlights": ["Great Migration", "Big Cats", "Hot Air Balloons"],
            "activities": ["Game Drives", "Balloon Safaris", "Cultural Visits"]
        },
        "diani_beach": {
            "name": "Diani Beach",
            "type": "Beach",
            "best_time": "December-March",
            "highlights": ["White Sands", "Coral Reefs", "Water Sports"],
            "activities": ["Snorkeling", "Kitesurfing", "Boat Trips"]
        },
        "amboseli": {
            "name": "Amboseli National Park",
            "type": "Safari",
            "best_time": "June-October",
            "highlights": ["Elephant Herds", "Mt. Kilimanjaro Views", "Swamp Wildlife"],
            "activities": ["Game Drives", "Photography", "Nature Walks"]
        },
        "nairobi": {
            "name": "Nairobi",
            "type": "City",
            "best_time": "Year-round",
            "highlights": ["National Park", "Giraffe Centre", "Karen Blixen Museum"],
            "activities": ["City Tours", "Restaurants", "Shopping"]
        },
        "mombasa": {
            "name": "Mombasa",
            "type": "Coastal City",
            "best_time": "December-March",
            "highlights": ["Fort Jesus", "Old Town", "Beaches"],
            "activities": ["Historical Tours", "Dhow Safaris", "Water Sports"]
        },
        "lamu": {
            "name": "Lamu Island",
            "type": "Cultural",
            "best_time": "January-March",
            "highlights": ["Swahili Culture", "Donkey Transport", "Old Town"],
            "activities": ["Dhow Trips", "Cultural Tours", "Beach Relaxation"]
        },
        "tsavo": {
            "name": "Tsavo National Parks",
            "type": "Safari",
            "best_time": "June-September",
            "highlights": ["Red Elephants", "Mzima Springs", "Lava Fields"],
            "activities": ["Game Drives", "Bird Watching", "Camping"]
        },
        "nakuru": {
            "name": "Lake Nakuru National Park",
            "type": "Safari",
            "best_time": "Year-round",
            "highlights": ["Flamingos", "Rothschild Giraffes", "White Rhinos"],
            "activities": ["Game Drives", "Bird Watching", "Picnic"]
        }
    }
    
    return jsonify({
        "success": True,
        "destinations": destinations,
        "count": len(destinations)
    })

@app.route('/reset', methods=['POST'])
def reset_session():
    """Reset a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "session_id required"}), 400
        
        if session_id in memories:
            # End current session
            memories[session_id].end_session()
            
            # Create new session in same memory
            memories[session_id].current_session = {
                "session_id": memories[session_id]._generate_session_id(),
                "start_time": datetime.now().isoformat(),
                "messages": [],
                "user_preferences": {},
                "context": {}
            }
        
        return jsonify({
            "success": True,
            "message": "Session reset successfully"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "active_sessions": len(agents),
        "timestamp": datetime.now().isoformat()
    })

# Cleanup old sessions (in production, use a proper task scheduler)
@app.before_request
def cleanup_sessions():
    """Simple cleanup of old sessions (every 100 requests)"""
    if request.endpoint == 'health':
        return
    
    # Very simple cleanup - in production use Redis with TTL
    global agents, memories
    if len(agents) > 100:  # If too many sessions, clear old ones
        agents = {}
        memories = {}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)