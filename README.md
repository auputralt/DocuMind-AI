# DocuMind AI

AI-powered document analysis chatbot with RAG (Retrieval-Augmented Generation). Upload documents, ask questions, get answers with source citations.

## Features

- **Free Mode** — Uses `openrouter/free`, no API key required
- **Bring Your Own Key** — Connect your own API key from OpenRouter, OpenAI, Anthropic, DeepSeek, or Google
- **Document Upload** — PDF, DOCX, DOC, TXT, CSV support
- **RAG Pipeline** — Documents are chunked, embedded locally (ChromaDB), and retrieved for context-aware answers
- **Chat Interface** — ChatGPT-style conversation with streaming responses
- **Source Citations** — AI cites which document and chunk the answer comes from

## Modes

| | Free | BYOK |
|---|---|---|
| API Key | Not needed | Required |
| Model | openrouter/free | Your choice |
| Files | Up to 10, 15MB each | Unlimited, 200MB each |
| Speed | Slower (free tier) | Depends on provider |

## Setup

### 1. Clone and install
```bash
git clone https://github.com/auputralt/DocuMind-AI.git
cd DocuMind-AI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
Create a `.env` file:
```
OPENROUTER_API_KEY=your-key-here
```
Get your key at [openrouter.ai/keys](https://openrouter.ai/keys). Required for free mode. For BYOK, enter your key directly in the app.

### 3. Run
```bash
streamlit run app.py
```

## Tech Stack

- **UI:** Streamlit
- **RAG:** ChromaDB (local embeddings, no external embedding API needed)
- **LLM:** OpenRouter (free tier) or BYOK (OpenAI, Anthropic, DeepSeek, Google)
- **Parsing:** PyMuPDF, python-docx

## Project Structure

```
app.py          # Main Streamlit app
chat.py         # LLM client, model configs, streaming
embedder.py     # ChromaDB storage with local embeddings
parser.py       # Document parsing (PDF, DOCX, TXT, CSV)
retriever.py    # Context retrieval from ChromaDB
requirements.txt
.env            # API keys (not committed)
```

## Author

**auputralt**

## License

All rights reserved.
