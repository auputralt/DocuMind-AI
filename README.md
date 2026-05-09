# DocuMind AI

AI-powered document analysis chatbot. Upload documents, ask questions, get answers with source citations.

## Features

- **Free Mode** — No API key needed. Uses openrouter/free.
- **Bring Your Own Key** — Use your own API key from OpenRouter, OpenAI, Anthropic, DeepSeek, or Google.
- **Document Upload** — Supports PDF, DOCX, DOC, TXT, CSV.
- **Smart Retrieval** — Documents are chunked and indexed for context-aware answers.
- **Streaming Chat** — ChatGPT-style conversation with real-time responses.
- **Source Citations** — AI cites which document and chunk the answer comes from.

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
Get your key at [openrouter.ai/keys](https://openrouter.ai/keys). Required for free mode. For BYOK, enter your key directly in the app sidebar.

### 3. Run
```bash
streamlit run app.py
```

## Tech Stack

- **UI:** Streamlit
- **LLM Gateway:** OpenRouter (free tier) or BYOK (OpenAI, Anthropic, DeepSeek, Google)
- **Parsing:** PyMuPDF, python-docx
- **Storage:** Local JSON file-based chunk storage
- **Retrieval:** Keyword-overlap scoring

## Project Structure

```
app.py          # Main Streamlit app
chat.py         # LLM client, model configs, streaming
embedder.py     # Chunk storage (JSON file)
parser.py       # Document parsing (PDF, DOCX, TXT, CSV)
retriever.py    # Context retrieval (keyword scoring)
requirements.txt
.env            # API keys (not committed)
```

## Author

**auputralt**

## License

All rights reserved.
