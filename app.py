
import streamlit as st
import sqlite3
import os
import tempfile
from pathlib import Path
import html as _html
import re

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="دستیار هوشمند RAG", page_icon="🧠", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700;800&display=swap');

:root {
  --c-bg: oklch(98% 0.01 260);
  --c-bg-2: oklch(96% 0.012 260);
  --c-surface: oklch(100% 0 0);
  --c-surface-2: oklch(97% 0.008 260);
  --c-border: oklch(88% 0.01 260);
  --c-border-2: oklch(80% 0.012 260);
  --c-text: oklch(19% 0.02 260);
  --c-muted: oklch(48% 0.015 260);
  --c-accent: oklch(58% 0.22 280);
  --c-accent-2: oklch(62% 0.18 255);
  --c-accent-soft: oklch(92% 0.05 280);
  --c-success: oklch(65% 0.15 160);
  --c-warn: oklch(75% 0.17 80);
  --c-error: oklch(65% 0.18 25);
  --c-shadow: 0 10px 30px oklch(20% 0.03 260 / 0.08);
  --c-shadow-soft: 0 4px 14px oklch(20% 0.03 260 / 0.06);
  --r: 16px;
  --r-sm: 12px;
  --s-1: 4px;
  --s-2: 8px;
  --s-3: 12px;
  --s-4: 16px;
  --s-5: 24px;
  --s-6: 32px;
  --t: 200ms ease;
}

html, body, .stApp, .stApp * {
  font-family: 'Vazirmatn', 'IRANSans', 'Tahoma', sans-serif !important;
  direction: rtl !important;
  text-align: right;
  box-sizing: border-box;
}

html, body {
  background:
    radial-gradient(circle at top right, oklch(95% 0.04 280 / .9), transparent 28%),
    radial-gradient(circle at bottom left, oklch(96% 0.03 240 / .7), transparent 24%),
    linear-gradient(180deg, var(--c-bg), var(--c-bg-2)) !important;
  color: var(--c-text);
}

.stApp {
  background: transparent !important;
}

/* keep layout RTL while preserving element order visually */
section.main > div, .block-container {
  padding-top: 1.25rem;
  padding-bottom: 2rem;
}

.block-container {
  max-width: 1320px;
}

/* Global Streamlit internals */
.stApp [data-testid],
.stApp [data-baseweb],
.stApp .stMarkdown,
.stApp .stTextInput,
.stApp .stTextArea,
.stApp .stSelectbox,
.stApp .stButton,
.stApp .stFileUploader,
.stApp .stExpander,
.stApp .stAlert,
.stApp .stInfo,
.stApp .stSuccess,
.stApp .stWarning,
.stApp .stError,
.stApp .stSpinner,
.stApp .stForm,
.stApp .stCheckbox,
.stApp .stProgress,
.stApp .stRadio,
.stApp .stMultiSelect,
.stApp .stNumberInput,
.stApp .stSlider,
.stApp .stDataFrame,
.stApp .stTable {
  direction: rtl !important;
  text-align: right !important;
  font-family: inherit !important;
}

.stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
[data-testid="stMarkdownContainer"] * {
  font-family: inherit !important;
  direction: rtl !important;
  text-align: right !important;
}

/* inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox [role="combobox"],
.stMultiSelect [role="combobox"],
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  font-family: inherit !important;
  direction: rtl !important;
  text-align: right !important;
  border-radius: 14px !important;
  transition: all var(--t) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
  color: oklch(58% 0.012 260) !important;
}

/* buttons */
.stButton > button,
.stForm button,
[data-testid="stFormSubmitButton"] button,
button[kind="primary"],
button[kind="secondary"] {
  border-radius: 14px !important;
  border: 1px solid transparent !important;
  font-family: inherit !important;
  font-weight: 700 !important;
  transition: transform var(--t), box-shadow var(--t), opacity var(--t), background var(--t) !important;
  padding: 0.6rem 1rem !important;
  min-height: 44px !important;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
  background: linear-gradient(135deg, var(--c-accent), var(--c-accent-2)) !important;
  color: white !important;
  box-shadow: var(--c-shadow-soft) !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover,
button[kind="primary"]:hover,
button[kind="secondary"]:hover {
  transform: translateY(-1px);
  opacity: .96;
}

/* containers / cards */
.card,
[data-testid="stExpander"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stForm"],
[data-testid="column"],
.stAlert {
  border-radius: var(--r) !important;
}

.card {
  background: linear-gradient(180deg, var(--c-surface), var(--c-surface-2));
  border: 1px solid var(--c-border);
  box-shadow: var(--c-shadow);
  padding: 1.25rem 1.35rem;
  margin-bottom: 1rem;
  transition: transform var(--t), box-shadow var(--t), border-color var(--t);
}
.card:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 34px oklch(20% 0.03 260 / 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: .5rem;
  font-weight: 800;
  color: var(--c-accent);
  margin-bottom: 1rem;
  font-size: 1.08rem;
}

.api-box {
  background: linear-gradient(135deg, oklch(96% 0.04 280), oklch(98% 0.02 255));
  border: 1px solid oklch(86% 0.08 280);
  border-right: 5px solid var(--c-accent);
  border-radius: var(--r);
  padding: 1rem 1.1rem;
  margin-bottom: 1rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  padding: .18rem .7rem;
  border-radius: 999px;
  font-size: .76rem;
  font-weight: 700;
  line-height: 1.6;
}
.badge-ok  { background: oklch(92% 0.08 160); color: oklch(32% 0.14 160); }
.badge-err { background: oklch(93% 0.09 28); color: oklch(35% 0.18 28); }

/* header */
.rag-header {
  background: linear-gradient(135deg, oklch(55% 0.22 280), oklch(62% 0.21 245));
  color: white;
  border-radius: calc(var(--r) + 6px);
  padding: 2rem 2rem;
  margin-bottom: 1rem;
  box-shadow: 0 16px 40px oklch(40% 0.12 270 / .25);
  position: relative;
  overflow: hidden;
}
.rag-header::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 0%, oklch(100% 0 0 / .06) 35%, transparent 70%);
  pointer-events: none;
}
.rag-header h1 {
  margin: 0 0 .35rem;
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 800;
}
.rag-header p {
  margin: 0;
  opacity: .92;
  font-size: 1rem;
}

/* timeline */
.timeline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin: 1.25rem 0 1.5rem;
  direction: ltr;
}
.tl-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  max-width: 220px;
}
.tl-circle {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1rem;
  border: 3px solid transparent;
  transition: all var(--t);
  background: var(--c-surface);
}
.tl-circle.done {
  background: var(--c-success);
  color: white;
  border-color: var(--c-success);
  box-shadow: 0 0 0 6px oklch(65% 0.15 160 / .12);
}
.tl-circle.active {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
  box-shadow: 0 0 0 6px oklch(58% 0.22 280 / .14);
}
.tl-circle.off {
  border-color: var(--c-border);
  color: var(--c-muted);
}
.tl-label {
  font-size: .82rem;
  margin-top: .5rem;
  color: var(--c-muted);
  text-align: center;
  direction: rtl;
}
.tl-label.active {
  color: var(--c-accent);
  font-weight: 700;
}
.tl-line {
  flex: 1;
  height: 3px;
  background: var(--c-border);
  margin-bottom: 1.5rem;
  max-width: 120px;
  border-radius: 999px;
}
.tl-line.done { background: linear-gradient(90deg, var(--c-success), var(--c-accent)); }

/* source chunk */
.source-chunk {
  background: oklch(97% 0.01 260);
  border: 1px solid var(--c-border);
  border-right: 4px solid var(--c-accent);
  border-radius: 14px;
  padding: .85rem .95rem;
  margin-bottom: .7rem;
  font-size: .9rem;
  line-height: 1.9;
}
.source-rank {
  font-weight: 800;
  color: var(--c-accent);
  margin-bottom: .25rem;
}

/* chat bubbles */
.chat-wrap {
  display: flex;
  flex-direction: column;
  gap: .6rem;
  margin: .7rem 0 .95rem;
}
.chat-bubble {
  display: flex;
  gap: .7rem;
  align-items: flex-start;
  max-width: 92%;
  border-radius: 18px;
  padding: .9rem 1rem;
  box-shadow: var(--c-shadow-soft);
  transition: transform var(--t), box-shadow var(--t), border-color var(--t);
}
.chat-bubble:hover { transform: translateY(-1px); }
.chat-bubble.user {
  margin-right: auto;
  flex-direction: row-reverse;
  background: linear-gradient(135deg, oklch(58% 0.22 280), oklch(62% 0.19 255));
  color: white;
  border: 1px solid oklch(60% 0.18 280 / .35);
  border-bottom-right-radius: 6px;
}
.chat-bubble.bot {
  margin-left: auto;
  background: linear-gradient(180deg, var(--c-surface), var(--c-surface-2));
  border: 1px solid var(--c-border);
  color: var(--c-text);
  border-bottom-left-radius: 6px;
}
.chat-avatar {
  flex: 0 0 auto;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: oklch(97% 0.02 260 / .95);
  color: var(--c-accent);
  font-size: 1.05rem;
  box-shadow: inset 0 0 0 1px oklch(88% 0.01 260);
}
.chat-bubble.user .chat-avatar {
  background: oklch(100% 0 0 / .18);
  color: white;
  box-shadow: inset 0 0 0 1px oklch(100% 0 0 / .18);
}
.chat-content {
  flex: 1 1 auto;
  min-width: 0;
  line-height: 1.9;
  font-size: .96rem;
  overflow-wrap: anywhere;
}
.chat-content p { margin: 0 0 .65rem; }
.chat-content p:last-child { margin-bottom: 0; }
.chat-content ul, .chat-content ol {
  margin: .45rem 0 .6rem;
  padding-inline-start: 1.15rem;
}
.chat-content li { margin: .18rem 0; }
.chat-content h1, .chat-content h2, .chat-content h3 {
  margin: .35rem 0 .55rem;
  line-height: 1.4;
}
.chat-content h1 { font-size: 1.22rem; }
.chat-content h2 { font-size: 1.12rem; }
.chat-content h3 { font-size: 1.02rem; }
.chat-content strong { font-weight: 800; }
.chat-content em { font-style: italic; }
.chat-content code {
  font-family: 'Vazirmatn', monospace !important;
  padding: .08rem .35rem;
  border-radius: 8px;
  background: oklch(94% 0.02 260);
  border: 1px solid oklch(88% 0.01 260);
}
.chat-bubble.user .chat-content code {
  background: oklch(100% 0 0 / .15);
  border-color: oklch(100% 0 0 / .18);
  color: white;
}
.chat-content a { color: var(--c-accent); text-decoration: none; }
.chat-content a:hover { text-decoration: underline; }

/* Alerts, expanders, progress, spinner, uploader */
.stAlert, [data-testid="stAlert"] {
  border-radius: var(--r) !important;
  border: 1px solid var(--c-border) !important;
  box-shadow: var(--c-shadow-soft) !important;
}
[data-testid="stAlertContentInfo"] { background: oklch(95% 0.03 250) !important; }
[data-testid="stAlertContentSuccess"] { background: oklch(94% 0.05 160) !important; }
[data-testid="stAlertContentWarning"] { background: oklch(96% 0.06 80) !important; }
[data-testid="stAlertContentError"] { background: oklch(95% 0.06 25) !important; }

[data-testid="stExpander"] {
  background: linear-gradient(180deg, var(--c-surface), var(--c-surface-2)) !important;
  border: 1px solid var(--c-border) !important;
  box-shadow: var(--c-shadow-soft) !important;
  overflow: hidden;
}
[data-testid="stExpander"] summary {
  font-weight: 700 !important;
}

[data-testid="stFileUploader"] {
  border-radius: var(--r) !important;
}
[data-testid="stFileUploaderDropzone"] {
  border: 1.5px dashed var(--c-border-2) !important;
  background: linear-gradient(180deg, oklch(99% 0.01 260), oklch(97% 0.01 260)) !important;
  border-radius: var(--r) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
  color: var(--c-muted) !important;
}

[data-testid="stProgressBar"] > div {
  background: linear-gradient(90deg, var(--c-accent), var(--c-success)) !important;
}

/* extra broad targeting for internal widgets */
[data-testid="stSidebar"], [data-testid="stSidebar"] * {
  direction: rtl !important;
  text-align: right !important;
  font-family: inherit !important;
}

[data-testid="stVerticalBlock"] {
  gap: 0.55rem;
}

hr {
  border: none;
  border-top: 1px solid var(--c-border);
  margin: 1rem 0;
}

.small-muted {
  color: var(--c-muted);
  font-size: .86rem;
}
</style>
""", unsafe_allow_html=True)

# ── constants ─────────────────────────────────────────────────────────────────
DEFAULT_API_KEY = "AQ.Ab8RN6JWt-iOf3BF8_d4bvp16E4R6y1W-PPCow1yIbIRbRz_RA"
MODELS = ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.1-pro-preview"]
DB_PATH = "rag_meta.db"

# آدرس ثابت endpoint گوگل — برخی API key ها فقط به v1 دسترسی دارند نه v1beta پیش‌فرض
GOOGLE_API_ENDPOINT = "https://generativelanguage.googleapis.com"

RAG_INFO = {
    "ساده (Simple)": "بازیابی مستقیم بر اساس شباهت برداری — سریع و مناسب برای اسناد همگن.",
    "ترکیبی (Hybrid)": "ترکیب جستجوی برداری و کلیدواژه‌ای — دقت بالاتر برای اسناد متنوع.",
    "معنایی (Semantic)": "درک عمیق معنایی با بازنویسی پرسش — بهترین کیفیت، کمی کندتر.",
}

# ── session state ─────────────────────────────────────────────────────────────
for k, v in {
    "step": 1,
    "api_key": DEFAULT_API_KEY,
    "use_custom_key": False,
    "model": MODELS[0],
    "rag_type": list(RAG_INFO.keys())[0],
    "embed_model": "models/gemini-embedding-2",
    "chat_history": [],
    "docs_parsed": [],
    "chroma_ready": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── markdown helper ───────────────────────────────────────────────────────────
def md_to_html(text):
    """Convert markdown-ish text to safe HTML. Uses python-markdown if available; otherwise a small fallback."""
    text = "" if text is None else str(text)
    try:
        import markdown as _md  # type: ignore
        return _md.markdown(text, extensions=["extra", "sane_lists"], output_format="html5")
    except Exception:
        pass

    # fallback: safe escape first, then apply very small markdown subset
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _html.escape(text)

    # code spans first
    code_spans = {}
    def _code_repl(m):
        key = f"__CODE_{len(code_spans)}__"
        code_spans[key] = m.group(1)
        return key
    text = re.sub(r"`([^`]+)`", _code_repl, text)

    # headings line by line and lists
    lines = text.split("\n")
    out = []
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            close_lists()
            out.append("")
            continue

        heading = None
        if stripped.startswith("### "):
            heading = f"<h3>{stripped[4:]}</h3>"
        elif stripped.startswith("## "):
            heading = f"<h2>{stripped[3:]}</h2>"
        elif stripped.startswith("# "):
            heading = f"<h1>{stripped[2:]}</h1>"
        if heading:
            close_lists()
            out.append(heading)
            continue

        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        numbered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if bullet:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{bullet.group(1)}</li>")
            continue
        if numbered:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{numbered.group(1)}</li>")
            continue

        close_lists()
        # inline formatting
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", line)
        line = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", line)
        out.append(f"<p>{line}</p>")

    close_lists()
    html = "\n".join(out)
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("\n", "<br>")
    for k2, v2 in code_spans.items():
        html = html.replace(k2, f"<code>{v2}</code>")
    html = html.replace("<p></p>", "")
    return html

# ── DB ────────────────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT, filetype TEXT, status TEXT, chunks INTEGER, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    con.commit(); con.close()

def db_insert(filename, filetype, status, chunks):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO documents (filename,filetype,status,chunks) VALUES (?,?,?,?)",
                (filename, filetype, status, chunks))
    con.commit(); con.close()

def db_all():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT filename,filetype,status,chunks,added_at FROM documents ORDER BY id DESC").fetchall()
    con.close(); return rows

init_db()

# ── helpers ───────────────────────────────────────────────────────────────────
def get_api_key():
    return st.session_state.api_key if st.session_state.use_custom_key else DEFAULT_API_KEY

def list_available_embed_models():
    """در صورت خطای 404 مدل امبدینگ، لیست واقعی مدل‌های در دسترس این API key را برمی‌گرداند."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=get_api_key())
        names = []
        for m in genai.list_models():
            if "embedContent" in getattr(m, "supported_generation_methods", []):
                names.append(m.name)
        return names
    except Exception as e:
        return [f"⚠️ خطا در واکشی لیست مدل‌ها: {e}"]

def parse_document(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read()); tmp_path = tmp.name
    try:
        if suffix == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader
            docs = PyPDFLoader(tmp_path).load()
        elif suffix in (".docx", ".doc"):
            from langchain_community.document_loaders import Docx2txtLoader
            docs = Docx2txtLoader(tmp_path).load()
        elif suffix in (".xlsx", ".xls"):
            from langchain_community.document_loaders import UnstructuredExcelLoader
            docs = UnstructuredExcelLoader(tmp_path).load()
        else:
            return None, "فرمت پشتیبانی نمی‌شود"
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
        return chunks, None
    except Exception as e:
        return None, str(e)
    finally:
        os.unlink(tmp_path)

def build_vectorstore(all_chunks):
    import chromadb
    from langchain_community.vectorstores import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=st.session_state.embed_model,
            google_api_key=get_api_key(),
            task_type="retrieval_document",
            client_options={"api_endpoint": GOOGLE_API_ENDPOINT},
        )
        vs = Chroma.from_documents(all_chunks, embeddings, collection_name="rag_docs")
        return vs
    except Exception as e:
        err_text = str(e)
        if "404" in err_text or "NOT_FOUND" in err_text:
            available = list_available_embed_models()
            raise RuntimeError(
                f"مدل '{st.session_state.embed_model}' برای این API key در دسترس نیست.\n\n"
                f"مدل‌های امبدینگ در دسترس این کلید:\n" + "\n".join(f"• {m}" for m in available)
            )
        raise

def ask_rag(question, vectorstore):
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=st.session_state.model,
        google_api_key=get_api_key(),
        temperature=0.3,
        client_options={"api_endpoint": GOOGLE_API_ENDPOINT},
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    context = "\n\n".join(d.page_content for d in docs)
    prompt = f"""بر اساس متن زیر به سوال پاسخ بده. اگر پاسخ در متن نیست، صادقانه بگو نمی‌دانم.

متن:
{context}

سوال: {question}
پاسخ:"""
    response = llm.invoke(prompt)
    return response.content, docs


def render_chat_message(msg):
    role = msg.get("role", "bot")
    content = msg.get("content", "")
    icon = "🧑‍💻" if role == "user" else "🤖"
    kind = "user" if role == "user" else "bot"
    bubble_html = md_to_html(content)
    st.markdown(
        f'<div class="chat-wrap"><div class="chat-bubble {kind}"><div class="chat-avatar">{icon}</div><div class="chat-content">{bubble_html}</div></div></div>',
        unsafe_allow_html=True,
    )

# ── header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
  <h1>🧠 دستیار هوشمند RAG</h1>
  <p>پلتفرم پرسش و پاسخ هوشمند از اسناد شما</p>
</div>
""", unsafe_allow_html=True)

# ── timeline ──────────────────────────────────────────────────────────────────
step = st.session_state.step
steps = ["⚙️ تنظیمات", "📂 بارگذاری اسناد", "💬 گفتگو"]

def circle_cls(i):
    if i + 1 < step: return "done"
    if i + 1 == step: return "active"
    return "off"

def line_cls(i):
    return "done" if i + 1 < step else ""

tl_html = '<div class="timeline">'
for i, label in enumerate(steps):
    tl_html += f'<div class="tl-step"><div class="tl-circle {circle_cls(i)}">{i+1}</div>'
    tl_html += f'<div class="tl-label {"active" if i+1==step else ""}">{label}</div></div>'
    if i < len(steps) - 1:
        tl_html += f'<div class="tl-line {line_cls(i)}"></div>'
tl_html += '</div>'
st.markdown(tl_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — تنظیمات
# ══════════════════════════════════════════════════════════════════════════════
if step == 1:
    st.markdown('<div class="card"><div class="card-title">🔑 تنظیمات API</div>', unsafe_allow_html=True)

    st.markdown('<div class="api-box">🔒 کلید API پیش‌فرض به صورت امن تنظیم شده است.</div>', unsafe_allow_html=True)
    use_custom = st.checkbox("استفاده از کلید API شخصی", value=st.session_state.use_custom_key)
    st.session_state.use_custom_key = use_custom
    if use_custom:
        key_input = st.text_input("کلید API شخصی خود را وارد کنید:", type="password",
                                  value="" if st.session_state.api_key == DEFAULT_API_KEY else st.session_state.api_key)
        if key_input:
            st.session_state.api_key = key_input

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">🤖 انتخاب مدل و معماری RAG</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.model = st.selectbox("مدل زبانی:", MODELS,
                                               index=MODELS.index(st.session_state.model))
    with col2:
        st.session_state.rag_type = st.selectbox("معماری RAG:", list(RAG_INFO.keys()),
                                                  index=list(RAG_INFO.keys()).index(st.session_state.rag_type))

    st.info(f"ℹ️ {RAG_INFO[st.session_state.rag_type]}")

    embed_opts = ["models/gemini-embedding-2", "models/gemini-embedding-001", "models/gemini-embedding-2-preview"]
    st.session_state.embed_model = st.selectbox("مدل Embedding:", embed_opts,
                                                 index=embed_opts.index(st.session_state.embed_model)
                                                 if st.session_state.embed_model in embed_opts else 0)

    if st.button("🔍 بررسی مدل‌های امبدینگ در دسترس این کلید"):
        with st.spinner("در حال واکشی لیست مدل‌ها ..."):
            models = list_available_embed_models()
        if models:
            st.success("مدل‌های در دسترس:")
            for m in models:
                st.write(f"• {m}")
        else:
            st.warning("هیچ مدل امبدینگی برای این کلید یافت نشد.")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("بعدی ← مرحله ۲"):
        st.session_state.step = 2
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — بارگذاری اسناد
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    st.markdown('<div class="card"><div class="card-title">📂 بارگذاری و پردازش اسناد</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("فایل‌های PDF، Word یا Excel را انتخاب کنید:",
                                 type=["pdf", "docx", "doc", "xlsx", "xls"],
                                 accept_multiple_files=True)

    if uploaded and st.button("🔄 پردازش فایل‌ها"):
        all_chunks = []
        progress = st.progress(0)
        for i, f in enumerate(uploaded):
            with st.spinner(f"در حال پردازش {f.name} ..."):
                chunks, err = parse_document(f)
                if err:
                    db_insert(f.name, Path(f.name).suffix, "خطا", 0)
                    st.error(f"❌ {f.name}: {err}")
                else:
                    all_chunks.extend(chunks)
                    db_insert(f.name, Path(f.name).suffix, "موفق", len(chunks))
                    st.session_state.docs_parsed.append({"name": f.name, "chunks": len(chunks)})
            progress.progress((i + 1) / len(uploaded))

        if all_chunks:
            with st.spinner("در حال ساخت پایگاه برداری ..."):
                try:
                    st.session_state.vectorstore = build_vectorstore(all_chunks)
                    st.session_state.chroma_ready = True
                    st.success(f"✅ {len(all_chunks)} قطعه متنی با موفقیت ایندکس شد.")
                except Exception as e:
                    st.error(f"خطا در ساخت vectorstore: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # overview
    rows = db_all()
    if rows:
        st.markdown('<div class="card"><div class="card-title">📊 وضعیت اسناد</div>', unsafe_allow_html=True)
        for r in rows:
            badge = f'<span class="badge badge-ok">✓ {r[2]}</span>' if r[2] == "موفق" else f'<span class="badge badge-err">✗ {r[2]}</span>'
            st.markdown(f"**{r[0]}** &nbsp;|&nbsp; {r[1]} &nbsp;|&nbsp; {badge} &nbsp;|&nbsp; {r[3]} قطعه &nbsp;|&nbsp; <small>{r[4]}</small>",
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← بازگشت به مرحله ۱"):
            st.session_state.step = 1; st.rerun()
    with col2:
        if st.button("بعدی ← مرحله ۳ (گفتگو)"):
            if not st.session_state.chroma_ready:
                st.warning("⚠️ ابتدا حداقل یک سند را پردازش کنید.")
            else:
                st.session_state.step = 3; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — گفتگو
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    st.markdown('<div class="card"><div class="card-title">💬 گفتگو با اسناد</div>', unsafe_allow_html=True)

    # chat history display
    for msg in st.session_state.chat_history:
        render_chat_message(msg)
        if msg["role"] != "user" and "sources" in msg:
            with st.expander("📚 منابع مرتبط (۳ قطعه برتر)"):
                for j, src in enumerate(msg["sources"]):
                    st.markdown(f'<div class="source-chunk"><div class="source-rank">#{j+1}</div>{_html.escape(src.page_content[:350])}...</div>',
                                unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # input
    with st.form("chat_form", clear_on_submit=True):
        question = st.text_input("سوال خود را بنویسید:", placeholder="مثلاً: خلاصه این سند چیست؟")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            submitted = st.form_submit_button("ارسال 📨")
        with col2:
            clear = st.form_submit_button("پاک کردن تاریخچه 🗑️")
        with col3:
            back = st.form_submit_button("← بازگشت")

    if back:
        st.session_state.step = 2; st.rerun()

    if clear:
        st.session_state.chat_history = []; st.rerun()

    if submitted and question.strip():
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("در حال جستجو و تولید پاسخ ..."):
            try:
                answer, sources = ask_rag(question, st.session_state.vectorstore)
                st.session_state.chat_history.append({"role": "bot", "content": answer, "sources": sources})
            except Exception as e:
                st.session_state.chat_history.append({"role": "bot", "content": f"❌ خطا: {e}"})
        st.rerun()

