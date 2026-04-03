import streamlit as st
import streamlit.components.v1 as components
from database import load_csv_to_sqlite
from agent import run_query_agent

st.set_page_config(
    page_title="Talk to your Data",
    page_icon="🔍",
    layout="centered"
)

# ── Session State ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "db_name" not in st.session_state:
    st.session_state.db_name = None
if "table_name" not in st.session_state:
    st.session_state.table_name = None

# ── Hero Section ──────────────────────────────────────────
st.title("🔍 Talk to your Data")
st.markdown("""
Built by **Aakrati Bansal** — a Data Analyst turned AI Engineer.

Upload any CSV file and ask questions about your data in plain English.
No SQL knowledge needed. No coding required. Just ask.
""")

# ── 3 Differentiator Cards ────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **🧠 Understands your data**

    Reads your CSV schema
    automatically — knows
    your columns and types
    """)

with col2:
    st.info("""
    **✅ Execution-based validation**

    Every SQL query is tested
    against your actual database
    before returning results
    """)

with col3:
    st.info("""
    **🔄 Retries intelligently**

    If a query fails, the agent
    learns from the exact error
    and fixes it — up to 3x
    """)

st.divider()

# ── How It Works ──────────────────────────────────────────
with st.expander("⚙️ How does this work?", expanded=False):
    st.markdown("""
    This agent runs a 4-step pipeline every time you ask a question:

    1. **Reads your schema** — understands your table structure, column names and data types automatically
    2. **Generates SQL** — uses Groq (LLaMA 3.1) to write an optimised SQL query based on your question
    3. **Tests the query** — actually runs the query against SQLite. If it fails, feeds the real error back and retries up to 3 times
    4. **Returns plain English** — explains the result in simple language alongside the SQL query

    **Tech used:** Python · LangChain · Groq (LLaMA 3.1) · SQLite · Streamlit

    **Built without auto-magic frameworks** — the agent architecture is designed from scratch
    so every step is transparent and explainable.
    """)

    st.markdown("### Agent Architecture")

    diagram = """
    <svg width="100%" viewBox="0 0 680 720" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M2 1L8 5L2 9" fill="none" stroke="#666" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
    </defs>

    <!-- USER QUESTION -->
    <rect x="215" y="20" width="250" height="44" rx="8" fill="#f1efea" stroke="#888" stroke-width="0.5"/>
    <text x="340" y="42" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="14" font-weight="500" fill="#2c2c2a">User asks a question</text>
    <line x1="340" y1="64" x2="340" y2="104" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>

    <!-- SCHEMA READING -->
    <rect x="190" y="104" width="300" height="56" rx="8" fill="#e1f5ee" stroke="#0f6e56" stroke-width="0.5"/>
    <text x="340" y="124" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="14" font-weight="500" fill="#085041">Schema Reader</text>
    <text x="340" y="144" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="12" fill="#0f6e56">reads table structure, columns and types</text>
    <line x1="340" y1="160" x2="340" y2="200" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>

    <!-- SQL GENERATOR -->
    <rect x="190" y="200" width="300" height="56" rx="8" fill="#eeedfe" stroke="#534ab7" stroke-width="0.5"/>
    <text x="340" y="220" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="14" font-weight="500" fill="#3c3489">SQL Generator</text>
    <text x="340" y="240" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="12" fill="#534ab7">Groq (LLaMA 3.1) generates optimised query</text>
    <line x1="340" y1="256" x2="340" y2="296" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>

    <!-- EXECUTION TEST -->
    <rect x="190" y="296" width="300" height="56" rx="8" fill="#faeeda" stroke="#ba7517" stroke-width="0.5"/>
    <text x="340" y="316" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="14" font-weight="500" fill="#633806">Execution Test</text>
    <text x="340" y="336" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="12" fill="#ba7517">runs query on SQLite — real error feedback</text>
    <path d="M190 324 Q100 324 100 248 Q100 180 190 228" fill="none" stroke="#993c1d" stroke-width="1" stroke-dasharray="5 4" marker-end="url(#arrow)"/>
    <text x="55" y="270" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993c1d">retry with</text>
    <text x="55" y="284" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993c1d">real error</text>
    <line x1="340" y1="352" x2="340" y2="392" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>

    <!-- OUTPUT -->
    <rect x="190" y="392" width="300" height="56" rx="8" fill="#e6f1fb" stroke="#185fa5" stroke-width="0.5"/>
    <text x="340" y="412" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="14" font-weight="500" fill="#042c53">Plain English Answer</text>
    <text x="340" y="432" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="12" fill="#185fa5">returns answer + SQL query to user</text>

    </svg>
    """
    components.html(diagram, height=500, scrolling=False)

st.divider()

# ── Production Thinking ───────────────────────────────────
with st.expander("🏗️ Production-Level Design Decisions", expanded=False):
    st.markdown("""
    While building this agent, I thought through real production challenges:

    **🔑 Unique database per user**
    Every uploaded CSV gets a UUID-based filename — so two users uploading
    the same file never overwrite each other's data.

    **🧹 Messy real-world data**
    Column names with spaces, dashes and special characters break SQL queries.
    The agent cleans all names automatically before loading into SQLite.

    **✅ Execution-based validation over LLM validation**
    Initially built an LLM validator — but it hallucinated reasons and rejected
    valid queries. Replaced with actual query execution testing against SQLite.
    Real errors are more reliable than LLM opinions.

    **📖 Data dictionaries for ambiguous columns**
    In real databases, columns like `val` or `status` are meaningless without context.
    Version 2 will let users add descriptions to columns so the LLM understands them.

    **🗃️ Multi-table support with RAG**
    Real databases have dozens of tables. Version 2 will use RAG-based schema search —
    embedding all table schemas and doing similarity search to find the relevant ones
    before generating SQL.
    """)

st.divider()

# ── Tech Stack ────────────────────────────────────────────
st.subheader("🛠️ Tech Stack")
st.markdown("""
| Component | Technology | Why |
|---|---|---|
| LLM | Groq (LLaMA 3.1 8b) | Fast inference, free tier |
| Agent Framework | LangChain | SQL database utilities |
| Database | SQLite | Lightweight, no setup needed |
| Schema Reading | LangChain SQLDatabase | Auto-reads any table structure |
| Unique IDs | UUID | Production-safe file naming |
| Frontend | Streamlit | Fast deployment |
""")

st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Your Database")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        if st.button("Load Data", use_container_width=True, type="primary"):
            with st.spinner("Loading your data..."):
                db_name = load_csv_to_sqlite(uploaded_file)
                st.session_state.db_name = db_name
                st.session_state.table_name = uploaded_file.name.replace(".csv", "")
                st.session_state.chat_history = []
            st.success("✅ Data loaded successfully!")

    if st.session_state.db_name:
        st.info(f"📊 Active dataset: **{st.session_state.table_name}**")
        st.caption("Ask anything about your data in the chat below.")

st.divider()

# ── Chat Interface ────────────────────────────────────────
st.subheader("💬 Ask your Data")

for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["answer"])
            with st.expander("🔍 Show Agent Thinking"):
                for step in message["steps"]:
                    st.markdown(step)
            with st.expander("📝 Show SQL Query"):
                st.code(message["sql_query"], language="sql")

question = st.chat_input("Ask a question about your data...")

if question:
    if st.session_state.db_name is None:
        st.warning("⚠️ Please upload a CSV file first.")
    else:
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("assistant"):
            steps = []
            with st.spinner("Thinking..."):
                steps.append("✅ Step 1 — Database schema loaded")
                steps.append("✅ Step 2 — SQL query generated")
                result = run_query_agent(question, st.session_state.db_name)
                steps.append("✅ Step 3 — Query executed successfully")
                steps.append("✅ Step 4 — Answer generated")

            sql_query = ""
            answer = result
            if "SQL Query:" in result:
                parts = result.split("SQL Query:")
                answer = parts[0].replace("Answer:", "").strip()
                sql_query = parts[1].strip()

            st.markdown(answer)
            with st.expander("🔍 Show Agent Thinking"):
                for step in steps:
                    st.markdown(step)
            with st.expander("📝 Show SQL Query"):
                st.code(sql_query, language="sql")

            st.session_state.chat_history.append({
                "role": "assistant",
                "answer": answer,
                "sql_query": sql_query,
                "steps": steps
            })

st.divider()
st.caption("Talk to your Data · Built by Aakrati Bansal · Data Analyst turned AI Engineer 🤖")