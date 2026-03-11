
# Kenya Travel AI Agent

An intelligent travel assistant for Kenyan tourism, built with Python and LangChain.

## Features

- **Web Scraping**: Collect data from travel websites, Wikipedia, and social media
- **RAG System**: Retrieval-Augmented Generation for accurate responses
- **Multiple LLM Options**: Use OpenAI or free HuggingFace models
- **Conversation Memory**: Remembers user preferences and history
- **Multiple Interfaces**: Streamlit web app, Flask API, CLI
- **Docker Support**: Easy deployment

## Quick Start

### Prerequisites

- Python 3.8+
- Docker (optional)
- OpenAI API key (optional, can use free HuggingFace models)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/kenya-travel-agent.git
cd kenya-travel-agent
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Data Collection

Run the scrapers to collect Kenyan travel data:

```bash
python scrapers/run_scrapers.py
```

This will:
- Scrape travel websites
- Collect Wikipedia articles
- Process and clean the data
- Save to `data/processed/`

### Create Vector Database

```bash
python models/vector_store.py
```

### Run the Agent

**Option 1: Command Line Interface**
```bash
python agent/travel_agent.py --llm huggingface
```

**Option 2: Streamlit Web App**
```bash
streamlit run deployment/streamlit_app.py
```

**Option 3: Flask API**
```bash
python deployment/flask_api.py
```

### Docker Deployment

```bash
cd deployment
chmod +x deploy.sh
./deploy.sh
```

## Usage Examples

### Web Interface

Access the Streamlit app at `http://localhost:8501`

### API Endpoints

```python
import requests

# Initialize session
response = requests.post('http://localhost:5000/init', 
                        json={'user_id': 'tourist123'})
session_id = response.json()['session_id']

# Ask a question
response = requests.post('http://localhost:5000/chat', json={
    'session_id': session_id,
    'message': 'Best time to visit Masai Mara?'
})

print(response.json()['response'])
```

### Python Library

```python
from agent.travel_agent import KenyaTravelAgent

agent = KenyaTravelAgent(llm_type='huggingface')
result = agent.ask('Tell me about Diani Beach')
print(result['answer'])
```

## Project Structure

```
kenya-travel-agent/
├── agent/
│   ├── travel_agent.py      # Main agent logic
│   └── memory_manager.py     # Conversation memory
├── scrapers/
│   ├── basic_scraper.py      # Basic web scraping
│   ├── advanced_scraper.py   # Selenium scraping
│   ├── data_processor.py     # Data cleaning
│   └── run_scrapers.py       # Master scraper
├── models/
│   └── vector_store.py        # Embeddings and vector DB
├── deployment/
│   ├── streamlit_app.py       # Web interface
│   ├── flask_api.py           # API backend
│   ├── Dockerfile             # Docker config
│   ├── docker-compose.yml     # Multi-container setup
│   ├── deploy.sh              # Deployment script
│   └── monitor.py              # Monitoring tool
├── tests/
│   └── test_agent.py          # Unit tests
├── data/
│   ├── raw/                    # Raw scraped data
│   ├── processed/              # Cleaned data
│   └── embeddings/             # Vector store
├── requirements.txt
└── README.md
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI models |
| `HUGGINGFACEHUB_API_TOKEN` | HuggingFace token | Optional |
| `FLASK_SECRET_KEY` | Flask session key | For API |

### LLM Options

- **OpenAI**: Better quality, requires API key
- **HuggingFace**: Free, runs locally, slower

## Monitoring

Run the monitoring tool:

```bash
python deployment/monitor.py
```

This provides:
- Health checks
- Response time metrics
- Error tracking
- Performance reports

## Testing

Run the test suite:

```bash
python -m unittest tests/test_agent.py
```

Or run with coverage:

```bash
pip install coverage
coverage run -m unittest tests/test_agent.py
coverage report
```

## Production Deployment

### Using Docker Compose

```bash
cd deployment
docker-compose up -d
```

### Manual Deployment

1. Set up a production server (AWS, DigitalOcean, etc.)
2. Install Docker and Docker Compose
3. Clone the repository
4. Set up environment variables
5. Run `./deploy.sh`

### Scaling Considerations

- Use Redis for session management
- Implement rate limiting
- Add load balancing for multiple instances
- Use CDN for static files

## Contributing

Contributions welcome! Please read our contributing guidelines.

## License

MIT License - see LICENSE file

## Acknowledgments

- LTLAB Big Data Fellowship
- Kenya Tourism Board
- Open-source community

## Support

- Issues: GitHub Issues
- Email: augoamos@gmail.com
