#!/bin/bash

# Kenya Travel Agent Deployment Script
echo "========================================="
echo "Kenya Travel Agent - Deployment Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
else
    print_status "Docker is installed"
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install docker-compose first."
    exit 1
else
    print_status "docker-compose is installed"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    
    cat > .env << EOF
# OpenAI API Key (optional if using HuggingFace)
OPENAI_API_KEY=your_openai_api_key_here

# Flask settings
FLASK_SECRET_KEY=$(openssl rand -hex 32)

# HuggingFace token (optional)
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
EOF
    
    print_warning "Please edit the .env file with your API keys"
    exit 1
else
    print_status ".env file found"
fi

# Create necessary directories
print_status "Creating data directories..."
mkdir -p ../data/raw ../data/processed ../data/embeddings ../data/conversations

# Check if we have data
if [ -z "$(ls -A ../data/processed 2>/dev/null)" ]; then
    print_warning "No processed data found. Running scrapers to collect data..."
    
    # Run the scraping pipeline
    cd ..
    python scrapers/run_scrapers.py
    
    if [ $? -ne 0 ]; then
        print_error "Scraping failed. Please check the logs."
        exit 1
    fi
    
    print_status "Data collection complete!"
    
    # Create embeddings
    print_status "Creating embeddings..."
    python models/vector_store.py
    
    cd deployment
else
    print_status "Found existing data in data/processed"
fi

# Build and deploy with docker-compose
print_status "Building and starting containers..."

# Stop any existing containers
docker-compose down 2>/dev/null

# Build and start
docker-compose up --build -d

if [ $? -eq 0 ]; then
    print_status "Containers started successfully!"
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 5
    
    # Check if API is responding
    if curl -s http://localhost:5000/health > /dev/null; then
        print_status "API is running at http://localhost:5000"
    else
        print_warning "API is not responding yet. Check logs with: docker-compose logs api"
    fi
    
    # Check if Streamlit is responding
    if curl -s http://localhost:8501 > /dev/null; then
        print_status "Streamlit app is running at http://localhost:8501"
    else
        print_warning "Streamlit app is not responding yet. Check logs with: docker-compose logs streamlit"
    fi
    
    echo ""
    echo "========================================="
    echo "Deployment Complete!"
    echo "========================================="
    echo ""
    echo "Access your Kenya Travel Agent at:"
    echo "  • Web App: http://localhost:8501"
    echo "  • API: http://localhost:5000"
    echo "  • API Docs: http://localhost:5000/"
    echo ""
    echo "Useful commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop: docker-compose down"
    echo "  • Restart: docker-compose restart"
    echo "  • Rebuild: docker-compose up --build -d"
    echo ""
    
else
    print_error "Failed to start containers. Check docker-compose logs for details."
    exit 1
fi