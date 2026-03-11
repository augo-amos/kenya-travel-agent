
# Kenya Travel Agent

An AI-powered travel assistant for Kenyan tourism destinations. This project scrapes travel data from various Kenyan tourism websites and uses LangChain with HuggingFace models to provide intelligent responses about Kenyan travel destinations.

## Features

- **Web Scrapers**: Collect data from Kenyan tourism websites
- **Vector Database**: FAISS-based storage for efficient similarity search
- **AI-Powered Q&A**: Flan-T5 model for natural language responses
- **Interactive Chat**: Command-line interface for conversations
- **Multi-Destination Support**: Covers Masai Mara, Diani Beach, Amboseli, and more

## Tech Stack

- Python 3.12
- LangChain 0.1.0
- HuggingFace Transformers
- FAISS Vector Store
- Selenium & BeautifulSoup for scraping
- Streamlit (optional, for UI)

## Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/kenya-travel-agent.git
   cd kenya-travel-agent
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Data Collection

Run the scrapers to collect travel data:

```bash
# Basic web scraping
python3 scrapers/run_scrapers.py

# Advanced scraping with Selenium
python3 scrapers/run_advanced_scraper.py
```

## Build the Knowledge Base

Create embeddings and vector store:

```bash
python3 models/vector_store.py
```

## Run the Travel Agent

### Interactive Mode
```bash
python3 agent/travel_agent.py
```

### Single Query Mode
```bash
python3 agent/travel_agent.py --query "Tell me about Masai Mara"
```

## Project Structure

```
kenya-travel-agent/
├── agent/
│   └── travel_agent.py          # Main AI agent
├── scrapers/
│   ├── run_scrapers.py          # Basic scrapers
│   └── advanced_scraper.py       # Selenium scrapers
├── models/
│   └── vector_store.py           # Vector DB management
├── data/
│   ├── raw/                      # Scraped data
│   ├── processed/                 # Cleaned data
│   └── embeddings/                # FAISS indices
├── requirements.txt
├── .gitignore
└── README.md
```

## Configuration

Create a `.env` file for environment variables:

```bash
# Optional: API keys if using OpenAI
OPENAI_API_KEY=your_key_here
```

## Testing

```bash
# Test the agent
python3 agent/travel_agent.py --query "What's the best time to visit Amboseli?"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for the amazing framework
- HuggingFace for the language models
- Kenya Wildlife Service for destination information

## Contact

Amos Augo - augoamos@gmail.com

Project Link: [https://github.com/augo-amos/kenya-travel-agent](https://github.com/augo-amos/kenya-travel-agent)


