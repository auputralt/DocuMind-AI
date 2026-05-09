# DocuMind AI Showcase

A lightning-fast, free, and lightweight AI chat interface built with **Python**, **Streamlit**, and **OpenRouter**. 
This project serves as an elegant portfolio showcase of real-time LLM streaming without requiring paid API keys out of the box.

## Architecture

- **UI Framework:** [Streamlit](https://streamlit.io/) (Provides native streaming generators and zero-config chat UI)
- **LLM Gateway:** [OpenRouter](https://openrouter.ai/) (Routes to the best free LLM available, or allows premium models if an API key is provided)
- **Primary Model:** Auto-selected free models (e.g., Llama 3, Gemini Flash) via `openrouter/free`

## Features

- ⚡ **Real-time Streaming:** Tokens appear instantly as they are generated.
- 💸 **100% Free Default:** Uses OpenRouter's free tier automatically.
- 🔑 **Bring Your Own Key (BYOK):** Users can securely paste their own OpenRouter key in the sidebar to unlock premium models like `gpt-4o` or `claude-sonnet`.
- 🎨 **Premium UI:** Clean, distraction-free chat interface.

## Local Setup

### 1. Clone & Environment
Ensure you have Python 3.9+ installed. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install openai streamlit python-dotenv
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```bash
OPENROUTER_API_KEY=""
```
*Note: You can leave this blank to force the UI to ask for a key, or put your own key here to use it globally.*

### 4. Run the App
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

## Deployment

This app is optimized for **Streamlit Community Cloud**:
1. Push this repository to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Click "New app", select your repository, and set the main file path to `app.py`.
4. (Optional) Add your `OPENROUTER_API_KEY` to the app's Secrets settings if you want to provide a global key.
5. Click **Deploy!** Your app will be live for free forever.
