import streamlit as st
import sqlite3
import os
import tempfile
from pathlib import Path

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="دستیار هوشمند RAG", page_icon="🧠", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');

:root {
  --c-bg:       oklch(97% 0.005 260);
  --c-surface:  oklch(100% 0 0);
  --c-border:   oklch(88% 0.01 260);
  --c-text:     oklch(18% 0.02 260);
  --c-muted:    oklch(52% 0.015 260);
  --c-accent:   oklch(58% 0.22 280);
  --c-accent2:  oklch(65% 0.20 160);
  --c-warn:     oklch(72% 0.18  80);
  --c-step-done:oklch(62% 0.18 160);
  --c-step-act: oklch(58% 0.22 280);
  --c-step-off: oklch(82% 0.01 260);
  --r: 12px;
}

html, body, [class*="css"] {
  font-family: 'Vazirmatn', 'B Homa', Tahoma, sans-serif !important;
  direction: rtl;
  background: var(--c-bg) !important;
  color: var(--c-text);
}

/* ── header ── */
.rag-header {
  background: linear-gradient(135deg, oklch(55% 0.24 280), oklch(62% 0.22 200));
  border-radius: var(--r);
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
  color: #fff;
}
.rag-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0 0 .4rem; }
.rag-header p  { font-size: 1rem; opacity: .88; margin: 0; }

/* ── timeline ── */
.timeline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 2.5rem;
  direction: ltr;
}
.tl-step {
  display: flex; flex-direction: column; align-items: center;
  position: relative; flex: 1; max-width: 180px;
}
.tl-circle {
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1rem; z-index: 1;
  border: 3px solid transparent;
  transition: all .25s ease;
}
.tl-circle.done  { background: var(--c-step-done); color: #fff; border-color: var(--c-step-done); }
.tl-circle.active{ background: var(--c-step-act);  color: #fff; border-color: var(--c-step-act);
                   box-shadow: 0 0 0 5px oklch(58% 0.22 280 / .18); }
.tl-circle.off   { background: var(--c-surface); color: var(--c-muted); border-color: var(--c-border); }
.tl-label { font-size: .78rem; margin-top: .45rem; color: var(--c-muted); text-align: center; direction: rtl; }
.tl-label.active { color: var(--c-accent); font-weight: 600; }
.tl-line {
  flex: 1; height: 3px; background: var(--c-border);
  margin-bottom: 1.4rem; max-width: 80px;
}
.tl-line.done { background: var(--c-step-done); }

/* ── card ── */
.card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  padding: 1.8rem 2rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 1px 4px oklch(0% 0 0 / .06);
}
.card-title {
  font-size: 1.15rem; font-weight: 700;
  color: var(--c-accent); margin-bottom: 1rem;
  display: flex; align-items: center; gap: .5rem;
}

/* ── api key box ── */
.api-box {
  background: oklch(96% 0.015 280);
  border: 1.5px dashed var(--c-accent);
  border-radius: var(--r); padding: 1.2rem 1.5rem;
  margin-bottom: 1rem;
}

/* ── source chunk ── */
.source-chunk {
  background: oklch(96% 0.01 260);
  border-right: 4px solid var(--c-accent);
  border-radius: 8px; padding: .9rem 1rem;
  margin-bottom: .7rem; font-size: .88rem;
}
.source-rank { font-weight: 700; color: var(--c-accent); margin-bottom: .3rem; }

/* ── chat bubbles ── */
.bubble-user {
  background: oklch(94% 0.04 280);
  border-radius: 16px 4px 16px 16px;
  padding: .75rem 1.1rem; margin: .5rem 0;
  max-width: 78%; margin-right: auto;
  font-size: .95rem;
}
.bubble-bot {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 4px 16px 16px 16px;
  padding: .75rem 1.1rem; margin: .5rem 0;
  max-width: 88%; margin-left: auto;
  font-size: .95rem;
}

/* ── buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--c-accent), oklch(62% 0.22 200)) !important;
  color: #fff !important; border: none !important;
  border-radius: 8px !important; font-family: inherit !important;
  font-weight: 600 !important; padding: .55rem 1.6rem !important;
  transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .88 !important; }

/* ── misc ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
  font-family: inherit !important; direction: rtl !important;
  border-radius: 8px !important;
}
.stFileUploader { direction: rtl; }
.badge {
  display: inline-block; padding: .2rem .65rem;
  border-radius: 20px; font-size: .75rem; font-weight: 600;
}
.badge-ok  { background: oklch(92% 0.08 160); color: oklch(35% 0.15 160); }
.badge-err { background: oklch(94% 0.08  30); color: oklch(40% 0.18  30); }
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
        if msg["role"] == "user":
            st.markdown(f'<div class="bubble-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bubble-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
            if "sources" in msg:
                with st.expander("📚 منابع مرتبط (۳ قطعه برتر)"):
                    for j, src in enumerate(msg["sources"]):
                        st.markdown(f'<div class="source-chunk"><div class="source-rank">#{j+1}</div>{src.page_content[:350]}...</div>',
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
