import streamlit as st
import os
from dotenv import load_dotenv

from parser import parse_document
from embedder import store_chunks
from chat import FREE_CONFIG, PROVIDERS, prepare_rag_messages, stream_response

load_dotenv()

# Read API key: .env (local) > st.secrets (cloud) > env var
if not os.getenv("OPENROUTER_API_KEY"):
    _cloud_key = st.secrets.get("OPENROUTER_API_KEY", "")
    if _cloud_key and _cloud_key != "your-openrouter-api-key-here":
        os.environ["OPENROUTER_API_KEY"] = _cloud_key

FREE_MAX_FILES = 10
FREE_MAX_FILE_MB = 15
BYOK_MAX_FILE_MB = 200

st.set_page_config(page_title="DocuMind AI", layout="centered")

st.markdown("""
    <style>
    .stAppDeployButton {display:none;}
    /* ChatGPT-style chat bubbles */
    [data-testid="stChatMessage"] {
        padding: 1.2rem 1.5rem;
        border-radius: 0;
    }
    [data-testid="stChatMessageContent"] p {
        font-size: 0.95rem;
        line-height: 1.7;
    }
    [data-testid="stChatMessageContent"] code {
        font-size: 0.85rem;
        background: rgba(0,0,0,0.06);
        padding: 2px 6px;
        border-radius: 4px;
    }
    /* Cleaner chat input */
    [data-testid="stChatInputTextArea"] {
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("DocuMind AI")
st.caption("Document analysis with AI")

# -- Sidebar --
with st.sidebar:
    st.header("Settings")

    mode = st.radio("Mode", ["Free", "Bring Your Own Key"], horizontal=True)

    if mode == "Free":
        st.session_state.active_config = FREE_CONFIG
        st.session_state.active_api_key = os.getenv("OPENROUTER_API_KEY")
        st.session_state.active_base_url = "https://openrouter.ai/api/v1"
        st.session_state.mode = "free"
        st.caption("Uses openrouter/free. May be slower.")
    else:
        st.markdown("**Provider**")
        provider = st.selectbox("Choose provider", options=list(PROVIDERS.keys()), label_visibility="collapsed")
        provider_cfg = PROVIDERS[provider]
        st.session_state.active_base_url = provider_cfg['base_url']

        byok_key = st.text_input("API Key", type="password", help=f"Enter your {provider} API key")
        if not byok_key:
            st.warning(f"Enter your {provider} API key to continue.")
            st.stop()

        st.session_state.active_api_key = byok_key
        st.markdown("**Model**")
        model_list = list(provider_cfg['models'].keys())
        selected_model = st.selectbox("Choose model", options=model_list, label_visibility="collapsed")
        st.session_state.active_config = provider_cfg['models'][selected_model]
        st.session_state.mode = "byok"

    st.success("Connected")
    st.divider()

    st.markdown("**Documents**")

    current_mode = st.session_state.get("mode", "free")
    if current_mode == "free":
        st.caption(f"Free = up to {FREE_MAX_FILES} files, {FREE_MAX_FILE_MB}MB each")
    else:
        st.caption(f"BYOK = unlimited files, {BYOK_MAX_FILE_MB}MB each")

    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        type=["pdf", "doc", "docx", "txt", "csv"],
        accept_multiple_files=True,
        label_visibility="visible",
    )

# -- Init session state --
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()
if "doc_greeted" not in st.session_state:
    st.session_state.doc_greeted = False

# -- Validate uploads --
docs_ready = False
file_names = []

if uploaded_files:
    current_mode = st.session_state.get("mode", "free")
    valid = True

    if current_mode == "free":
        if len(uploaded_files) > FREE_MAX_FILES:
            st.error(f"Free mode allows up to {FREE_MAX_FILES} files. You uploaded {len(uploaded_files)}.")
            valid = False
        for f in uploaded_files:
            size_mb = f.size / (1024 * 1024)
            if size_mb > FREE_MAX_FILE_MB:
                st.error(f"Rejected: {f.name} is {size_mb:.1f}MB. Free mode limit is {FREE_MAX_FILE_MB}MB per file.")
                valid = False
    else:
        for f in uploaded_files:
            size_mb = f.size / (1024 * 1024)
            if size_mb > BYOK_MAX_FILE_MB:
                st.error(f"Rejected: {f.name} is {size_mb:.1f}MB. Limit is {BYOK_MAX_FILE_MB}MB per file.")
                valid = False

    if valid:
        new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]

        if new_files:
            with st.status("Processing documents...", expanded=True) as status:
                for i, f in enumerate(new_files):
                    st.write(f"Parsing {f.name}...")
                    try:
                        chunks = parse_document(f.getvalue(), f.name)
                        st.write(f"Indexing {f.name} ({len(chunks)} chunks)...")
                        store_chunks(chunks)
                        st.session_state.processed_files.add(f.name)
                    except Exception as e:
                        st.error(f"Failed: {f.name}: {e}")
                    pct = int(((i + 1) / len(new_files)) * 100)
                    status.update(label=f"Processing documents... {pct}%")
                status.update(label="Done", state="complete", expanded=False)

            st.session_state.doc_greeted = False

        file_names = [f.name for f in uploaded_files]
        docs_ready = True

# -- AI greeting --
if docs_ready and not st.session_state.doc_greeted:
    file_list = ", ".join(file_names)
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"I've analyzed your document(s): **{file_list}**.\n\nHow can I help you?"
    })
    st.session_state.doc_greeted = True

# -- Chat history --
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=False)

# -- Chat input --
if not docs_ready:
    st.chat_input("Upload documents to start chatting...", disabled=True, key="disabled_chat")
else:
    if prompt := st.chat_input("Ask about your documents...", key="chat_input"):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build RAG messages
        api_messages = prepare_rag_messages(
            user_query=prompt,
            chat_history=st.session_state.messages[:-1]
        )

        # Stream assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_response = ""
                raw_stream = stream_response(
                    messages=api_messages,
                    model_config=st.session_state.active_config,
                    api_key=st.session_state.active_api_key,
                    base_url=st.session_state.active_base_url,
                )

                for token in raw_stream:
                    full_response += token

                st.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
