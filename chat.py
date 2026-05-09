import os
import streamlit as st
from typing import Dict, NamedTuple, Generator, List
from openai import OpenAI
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from openai import APITimeoutError, APIConnectionError, RateLimitError, InternalServerError
from dotenv import load_dotenv
from retriever import retrieve_context

load_dotenv()

class ModelConfig(NamedTuple):
    model_id: str
    context_window: int
    temperature: float
    max_tokens: int

FREE_CONFIG = ModelConfig('openrouter/free', 16384, 0.7, 300)

PROVIDERS = {
    'OpenRouter': {
        'base_url': 'https://openrouter.ai/api/v1',
        'models': {
            'Auto (best available)': ModelConfig('openrouter/auto', 16384, 0.7, 500),
            'DeepSeek V3 ($0.14/$0.28)': ModelConfig('deepseek/deepseek-chat-v3-0324', 16384, 0.7, 500),
            'GPT-4o Mini ($0.15/$0.60)': ModelConfig('openai/gpt-4o-mini', 16384, 0.7, 500),
            'Claude Haiku ($0.80/$4)': ModelConfig('anthropic/claude-3-5-haiku-20241022', 8192, 0.7, 500),
            'Gemini Flash ($0.30/$2.50)': ModelConfig('google/gemini-2.0-flash-001', 16384, 0.7, 500),
            'GPT-4o ($2.50/$10)': ModelConfig('openai/gpt-4o', 16384, 0.7, 500),
            'Claude Sonnet ($3/$15)': ModelConfig('anthropic/claude-sonnet-4', 8192, 0.7, 500),
        }
    },
    'OpenAI': {
        'base_url': 'https://api.openai.com/v1',
        'models': {
            'GPT-4.1 Nano ($0.10/$0.40)': ModelConfig('gpt-4.1-nano', 16384, 0.7, 500),
            'GPT-4o Mini ($0.15/$0.60)': ModelConfig('gpt-4o-mini', 16384, 0.7, 500),
            'GPT-4.1 Mini ($0.40/$1.60)': ModelConfig('gpt-4.1-mini', 16384, 0.7, 500),
            'GPT-4.1 ($2/$8)': ModelConfig('gpt-4.1', 16384, 0.7, 500),
            'GPT-4o ($2.50/$10)': ModelConfig('gpt-4o', 16384, 0.7, 500),
        }
    },
    'Anthropic': {
        'base_url': 'https://api.anthropic.com/v1',
        'models': {
            'Claude Haiku 3.5 ($0.80/$4)': ModelConfig('claude-3-5-haiku-20241022', 8192, 0.7, 500),
            'Claude Sonnet 4 ($3/$15)': ModelConfig('claude-sonnet-4-20250514', 8192, 0.7, 500),
        }
    },
    'DeepSeek': {
        'base_url': 'https://api.deepseek.com/v1',
        'models': {
            'DeepSeek Chat ($0.14/$0.28)': ModelConfig('deepseek-chat', 16384, 0.7, 500),
            'DeepSeek Reasoner ($0.55/$2.19)': ModelConfig('deepseek-reasoner', 16384, 0.7, 500),
        }
    },
    'Google': {
        'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai',
        'models': {
            'Gemini Flash-Lite ($0.03/$1.50)': ModelConfig('gemini-2.0-flash-lite', 16384, 0.7, 500),
            'Gemini Flash ($0.15/$0.60)': ModelConfig('gemini-2.0-flash', 16384, 0.7, 500),
            'Gemini Pro ($1.25/$10)': ModelConfig('gemini-2.5-pro-preview-05-06', 16384, 0.7, 500),
        }
    },
}

RETRYABLE = (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)

@st.cache_resource
def get_client(api_key: str, base_url: str):
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=httpx.Timeout(120.0, read=300.0, connect=30.0),
    )

def prepare_rag_messages(user_query: str, chat_history: List[Dict]) -> List[Dict]:
    retrieved_chunks = retrieve_context(user_query, top_k=5)

    if retrieved_chunks:
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            source = chunk['metadata'].get('source', 'Unknown')
            chunk_idx = chunk['metadata'].get('chunk_index', i)
            context_parts.append(f"--- Source: {source} (Chunk {chunk_idx}) ---\n{chunk['text']}")
        context_text = "\n\n".join(context_parts)
    else:
        context_text = "No relevant context found in uploaded documents."

    system_prompt = f"""You are DocuMind AI, an expert document analysis assistant.
Answer the user's question ONLY based on the provided document context below.
If the answer is not in the document, say "I cannot find the answer to that in the provided documents."
Always cite the source document and chunk index when providing information.

DOCUMENT CONTEXT:
{context_text}
"""

    history_to_keep = chat_history[-10:] if len(chat_history) > 10 else chat_history
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history_to_keep)
    messages.append({"role": "user", "content": user_query})
    return messages

def stream_response(messages: list[dict], model_config: ModelConfig,
                    api_key: str, base_url: str) -> Generator[str, None, None]:
    if not api_key:
        yield "Error: No API key configured."
        return

    client = get_client(api_key, base_url)

    @retry(
        retry=retry_if_exception_type(RETRYABLE),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        stop=stop_after_attempt(5),
    )
    def fetch_stream():
        return client.chat.completions.create(
            model=model_config.model_id,
            messages=messages,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            stream=True
        )

    try:
        response = fetch_stream()
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            yield "\n\nRate limited. Free models have usage caps. Try again in a minute or use BYOK mode."
        elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            yield "\n\nRequest timed out. Please try again."
        else:
            yield f"\n\nError: {error_msg}"
