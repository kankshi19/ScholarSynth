# ScholarSynth

An AI-powered research paper generation and analysis tool that autonomously searches academic papers, synthesizes research findings, and generates new research papers with LaTeX formatting.

## Overview

ScholarSynth is an intelligent research assistant built with LangChain and LangGraph that leverages state-of-the-art LLMs to:
- Search arXiv for recent papers on any academic topic
- Extract and analyze PDF content from research papers
- Synthesize research findings and identify new research directions
- Generate original research papers with mathematical equations
- Render papers as professional LaTeX PDFs

This tool is designed for researchers, academics, and anyone interested in exploring cutting-edge research in physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, systems science, and economics.

## Features

- **🔍 Intelligent Paper Search**: Search arXiv.org for recent papers with configurable result limits
- **📄 PDF Analysis**: Automatically extract and process text from research paper PDFs
- **🤖 AI-Powered Research Agent**: Uses ReAct (Reasoning + Acting) agent pattern with multi-step reasoning
- **📝 LaTeX Paper Generation**: Generate mathematically rigorous papers with equations and proper formatting
- **📊 PDF Rendering**: Compile LaTeX to professional PDF documents using Tectonic
- **💬 Interactive UI**: Streamlit-based web interface for seamless interaction
- **🔄 Multi-LLM Support**: Works with OpenRouter (preferred) or Google Gemini
- **💾 Conversation History**: Maintains context across interactions with message memory

## Tech Stack

- **LLM Framework**: LangChain & LangGraph
- **Frontend**: Streamlit
- **PDF Processing**: PyPDF2
- **PDF Rendering**: Tectonic (LaTeX compiler)
- **API Integration**: arXiv API, Google Gemini API, OpenRouter API
- **Python**: 3.12+

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.12 or higher**
2. **Tectonic** (for LaTeX PDF rendering)
   - Windows: `choco install tectonic` or download from [tectonic-typesetting.github.io](https://tectonic-typesetting.github.io/)
   - macOS: `brew install tectonic`
   - Linux: See [installation guide](https://tectonic-typesetting.github.io/en-US/install/)

3. **API Keys** (at least one):
   - **Google Gemini** (free tier available): [Get API key](https://makersuite.google.com/app/apikey)
   - **OpenRouter** (recommended): [Get API key](https://openrouter.ai/keys)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ScholarSynth
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

This installs all dependencies specified in `pyproject.toml`:
- langchain
- langchain-core
- langchain-google-genai
- langchain-openai
- langgraph
- pypdf2
- python-dotenv
- requests
- streamlit

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# LLM Configuration (choose one or both)
# Option 1: OpenRouter (Preferred - free models available)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/free  # or specify a model

# Option 2: Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-pro

# Optional: Performance Tuning
MAX_MODEL_CONTEXT_MESSAGES=10
MAX_TOOL_MESSAGE_CHARS=4000
MAX_TEXT_MESSAGE_CHARS=6000
```

**Priority**: If both OpenRouter and Gemini keys are set, OpenRouter will be used.

## Usage

### Running the Web UI (Recommended)

```bash
# Make sure your virtual environment is activated
streamlit run frontend.py
```

The application will open at `http://localhost:8501`

**Interactive Workflow**:
1. Describe your research topic to the AI
2. Review recent papers from arXiv
3. Select papers of interest
4. The AI reads and analyzes selected papers
5. Discuss research findings and future directions
6. Request paper generation
7. Download the rendered PDF

### Running the CLI Agent (Alternative)

For programmatic use or testing:

```python
python ai_researcher_2.py
```

## Project Structure

```
ScholarSynth/
├── ai_researcher.py          # Basic ReAct agent implementation
├── ai_researcher_2.py        # Advanced agent with optimizations & web support
├── arxiv_tool.py             # arXiv paper search functionality
├── read_pdf.py               # PDF extraction tool
├── write_pdf.py              # LaTeX to PDF rendering tool
├── frontend.py               # Streamlit web interface
├── pyproject.toml            # Project dependencies
├── README.md                 # This file
├── output/                   # Generated papers directory
│   └── paper_YYYYMMDD_HHMMSS.pdf
│   └── paper_YYYYMMDD_HHMMSS.tex
└── .env                      # Environment variables (not in repo)
```

## Core Components

### `arxiv_tool.py`
Searches arXiv API for academic papers by topic. Returns paper metadata including titles, authors, abstracts, publication dates, and download links.

### `read_pdf.py`
Extracts text content from PDF files using PyPDF2. Used to analyze paper content for research synthesis.

### `write_pdf.py`
Converts LaTeX content to PDF using the Tectonic compiler. Handles file management and output organization.

### `ai_researcher_2.py`
Main agent implementation using LangGraph with:
- State management for conversation history
- Tool integration (search, read, write)
- Message compaction for token optimization
- Multi-LLM support

### `frontend.py`
Streamlit web interface providing:
- Chat-like interaction with the research agent
- Real-time message streaming
- Paper management and downloads
- Custom styling and theme

## Example Workflow

1. **Start the app**: `streamlit run frontend.py`
2. **Ask a research question**: 
   > "I'm interested in recent advances in quantum machine learning"
3. **Review papers**: The AI searches arXiv and presents recent papers
4. **Select papers**: Choose which papers to analyze in depth
5. **Analyze**: AI reads and synthesizes the papers
6. **Generate**: Ask the AI to write a new research paper
7. **Download**: Get the PDF from the output folder

## Performance Tuning

For better performance and lower costs, adjust these environment variables:

- `MAX_MODEL_CONTEXT_MESSAGES`: Number of recent messages to keep (default: 10)
- `MAX_TOOL_MESSAGE_CHARS`: Max characters per tool response (default: 4000)
- `MAX_TEXT_MESSAGE_CHARS`: Max characters per text message (default: 6000)

Lower values = faster/cheaper but less context.

## Troubleshooting

### "Tectonic not found"
Ensure Tectonic is installed and in PATH:
```bash
tectonic --version
```

### API Key Errors
- Verify `.env` file exists and is in the project root
- Check API key validity and billing status
- Ensure no extra spaces around API key values

### PDF Generation Fails
- Check LaTeX content for syntax errors
- Ensure Tectonic has write permissions to `output/` directory
- Check available disk space

## Future Enhancements

- [ ] Support for additional academic databases (IEEE, PubMed, etc.)
- [ ] Paper recommendation engine
- [ ] Multi-language support
- [ ] Collaborative research sessions
- [ ] Citation management and bibliography generation
- [ ] Paper visualization and timeline generation
- [ ] Local LLM support (Ollama, LLaMA, etc.)

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For issues and questions, please open an issue on the repository.
