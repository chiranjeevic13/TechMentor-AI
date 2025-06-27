# TechMentor AI: A Dynamic RAG-based Tech Career Advisor

TechMentor AI is an advanced Retrieval-Augmented Generation (RAG) chatbot that provides personalized guidance for tech careers, learning resources, and project ideas. It combines a local knowledge base with dynamic web search capabilities to deliver comprehensive, up-to-date information.

## 🚀 Features

- **Career Roadmaps**: Personalized career paths for various tech domains
- **Learning Resources**: Curated learning materials for skills development
- **Project Ideas**: Creative project suggestions for portfolio building
- **Tech Comparisons**: Objective comparisons between technologies and career paths
- **Interview Preparation**: Guidance for technical interviews and resume building
- **Dynamic Web Search**: Real-time web content retrieval when local knowledge is insufficient

## 📋 Architecture

![RAG Architecture](https://img.shields.io/badge/Architecture-RAG-purple?style=flat-square)

TechMentor AI uses a hybrid architecture:
1. **Local Knowledge Base**: Curated tech career information indexed in a vector database
2. **Embedding Model**: Transforms text into semantic vectors for similarity search
3. **RAG Pipeline**: Retrieves relevant context and augments the LLM prompt
4. **Local LLM**: Processes the augmented prompt and generates responses
5. **Dynamic Search**: Performs real-time web searches when needed

## 🔧 Tech Stack

- **LLM**: 
  - [TinyLlama-1.1B-Chat-v1.0](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF) (current)
  - [CapybaraHermes-2.5-Mistral-7B](https://huggingface.co/TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF) (alternative)
- **Embeddings**: [Sentence Transformers](https://www.sbert.net/) (all-MiniLM-L6-v2)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Data Processing**: Custom chunking and cleaning pipeline
- **Web Scraping**: BeautifulSoup4 and Requests
- **Frontend**: Streamlit

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- 4GB+ RAM (8GB+ recommended)
- 5GB free disk space

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/tech-mentor-ai.git
   cd tech-mentor-ai
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download an LLM model**:
   - Option 1: TinyLlama (Faster, smaller)
     ```bash
     huggingface-cli download TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf --local-dir models/llm --local-dir-use-symlinks False
     ```
   - Option 2: CapybaraHermes (Higher quality, larger)
     ```bash
     huggingface-cli download TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF capybarahermes-2.5-mistral-7b.Q4_K_M.gguf --local-dir models/llm --local-dir-use-symlinks False
     ```

5. **Update config**:
   - Edit `config/config.yaml` to point to your downloaded model
   - For TinyLlama:
     ```yaml
     llm:
       model_type: "llama2"
       model_path: "models/llm/tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf"
     ```
   - For CapybaraHermes:
     ```yaml
     llm:
       model_type: "mistral"
       model_path: "models/llm/capybarahermes-2.5-mistral-7b.Q4_K_M.gguf"
     ```

## 🚀 Usage

### Data Pipeline Setup

Run the full pipeline to set up your knowledge base:

```bash
python run.py --all
```

Or run individual steps:

```bash
# Collect data from configured sources
python run.py --collect

# Process and chunk the data
python run.py --process

# Generate embeddings
python run.py --embed

# Build the vector database
python run.py --build-db

# Verify model installation
python run.py --check-model
```

### Running the App

Start the Streamlit interface:

```bash
python run.py --app
```

The application will be available at http://localhost:8501

## 📁 Project Structure

```
tech-mentor-ai/
├── data/                       # Data storage
│   ├── raw/                    # Raw collected documents
│   │   ├── web/                # Web-scraped content
│   │   ├── pdf_extracted/      # Extracted PDF text
│   │   └── youtube/            # YouTube transcripts
│   ├── processed/              # Processed documents
│   ├── embeddings/             # Saved embeddings
│   └── chroma_db/              # Vector database files
├── src/                        # Source code
│   ├── data_collection/        # Data collection modules
│   │   ├── web_scraper.py      # Web scraping utilities
│   │   ├── pdf_extractor.py    # PDF text extraction
│   │   ├── youtube_transcripts.py # YouTube transcript fetcher
│   │   └── dynamic_search.py   # Real-time web search
│   ├── preprocessing/          # Text processing modules
│   │   ├── text_cleaner.py     # Text cleaning utilities
│   │   └── chunker.py          # Document chunking
│   ├── embeddings/             # Embedding generation
│   │   └── model.py            # Embedding model wrapper
│   ├── vector_db/              # Vector database operations
│   │   └── chroma_db.py        # ChromaDB implementation
│   ├── llm/                    # LLM integration
│   │   └── model.py            # Local LLM interface
│   ├── rag/                    # RAG pipeline
│   │   ├── retriever.py        # Document retrieval
│   │   └── generator.py        # Response generation
│   └── utils/                  # Utility functions
│       └── helpers.py          # Helper utilities
├── app/                        # Streamlit application
│   ├── pages/                  # Additional pages
│   ├── components/             # UI components
│   └── app.py                  # Main Streamlit app
├── config/                     # Configuration
│   └── config.yaml             # System configuration
├── models/                     # Model files
│   ├── embeddings/             # Local embedding models
│   └── llm/                    # Local LLM models
│       ├── tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf    # TinyLlama model
│       └── capybarahermes-2.5-mistral-7b.Q4_K_M.gguf  # CapybaraHermes model
├── requirements.txt            # Project dependencies
├── run.py                      # Main execution script
└── README.md                   # Project documentation
```

## 🔍 Features Explained

### Local Knowledge Base

TechMentor AI builds a curated knowledge base from:
- Tech roadmaps and career guides
- Programming tutorials and documentation
- Learning resource directories
- Project idea compilations
- Tech comparison articles
- Interview preparation materials

### Dynamic Web Search

When the local knowledge base doesn't contain sufficient information:
1. Performs a real-time web search for relevant content
2. Extracts and processes content from top results
3. Augments the prompt with the retrieved web information
4. Clearly indicates when responses include dynamically retrieved data

### Customization Options

TechMentor AI can be customized via `config/config.yaml`:
- Switch between different LLM models
- Adjust RAG parameters (chunk size, retrieval count)
- Configure dynamic search behavior
- Customize prompt templates

## 🛠️ Extending the System

### Adding Knowledge Sources

1. Add new data sources in `config/config.yaml`:
   ```yaml
   data_collection:
     sources:
       - type: web
         urls:
           - "https://example.com/tech-guide"
       - type: youtube
         channels:
           - "TechChannel"
       - type: pdf
         paths:
           - "data/raw/my-tech-guide.pdf"
   ```

2. Run the data collection:
   ```bash
   python run.py --collect
   ```

### Using Different LLMs

1. Download a different GGUF model
2. Update the configuration in `config/config.yaml`
3. Verify with `python run.py --check-model`

### Adding New Features

The modular architecture makes it easy to extend:
- Add new data collectors in `src/data_collection/`
- Implement new processing techniques in `src/preprocessing/`
- Create new Streamlit pages in `app/pages/`

## 📊 Performance Considerations

### LLM Model Comparison

| Model | Size | Speed | Quality | RAM Usage |
|-------|------|-------|---------|-----------|
| TinyLlama-1.1B | ~600MB | Fast | Good | ~2GB |
| CapybaraHermes-2.5-Mistral-7B | ~4.5GB | Slower | Excellent | ~8GB |

### Hardware Recommendations

- **Minimum**: 4GB RAM, dual-core CPU
- **Recommended**: 8GB+ RAM, quad-core CPU
- **Optimal**: 16GB+ RAM, 8-core CPU, CUDA-compatible GPU

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- The open-source AI community for providing free models and tools
- [LangChain](https://github.com/langchain-ai/langchain) for inspiring the RAG architecture
- [Streamlit](https://streamlit.io/) for the UI framework
- [Sentence Transformers](https://www.sbert.net/) for the embedding models
- [ChromaDB](https://www.trychroma.com/) for the vector database
- [HuggingFace](https://huggingface.co/) and [TheBloke](https://huggingface.co/TheBloke) for quantized models

---

<p align="center">
  Made with ❤️ by Chiranjeevi C
</p>