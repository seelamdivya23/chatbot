from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st

# ---------------------------
# Streamlit page setup
# ---------------------------
st.set_page_config(page_title="Custom Chatbot", page_icon="🤖", layout="wide")

# ---------------------------
# Background Image
# ---------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        color: black;  /* ✅ Only title black */
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar with Icons
# ---------------------------
st.sidebar.markdown("<div class='sidebar-title'>📂 Menu</div>", unsafe_allow_html=True)

menu_choice = st.sidebar.radio(
    "Navigation",
    options=["New Chat", "Search Chats", "Library"],
    format_func=lambda x: {
        "New Chat": "➕ New Chat",
        "Search Chats": "🔍 Search Chats",
        "Library": "📚 Library"
    }[x]
)

# Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if dark_mode:
    st.markdown(
        """
        <style>
        body {color: #FFFFFF;}
        .stTextInput>div>div>input {background-color: #1E1E1E; color: #FFFFFF;}
        .stButton>button {background-color: #3B3B3B; color: #FFFFFF;}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# Chat session state
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []

# ---------------------------
# Prompt template & LLM
# ---------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user queries."),
        ("user", "Question:{question}")
    ]
)
llm = Ollama(model="llama2")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# ---------------------------
# Main Area
# ---------------------------
st.markdown("<h1 style='text-align: center; color:white;'>🤖 My Chatbot</h1>", unsafe_allow_html=True)

if menu_choice == "New Chat":
    # Reset chat when clicking New Chat
    if st.sidebar.button("🗑️ Clear Chat"):
        if st.session_state.messages:
            st.session_state.saved_chats.append(list(st.session_state.messages))  # ✅ auto-save old chat
        st.session_state.messages = []

    st.markdown(
        "<div style='display:flex; justify-content:center; margin-top:20px;'>"
        "<div style='width:50%; background:rgba(255,255,255,0.85); padding:15px; border-radius:10px;'>", 
        unsafe_allow_html=True
    )
    user_input = st.text_input("", placeholder="Type your question here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = chain.invoke({"question": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Display chat
    st.markdown("<div style='display:flex; justify-content:center; margin-top:20px;'>", unsafe_allow_html=True)
    st.markdown("<div style='width:50%;'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='text-align:right; background-color:#DCF8C6; padding:12px; border-radius:15px; margin:5px 0; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            bg_color = "rgba(255,255,255,0.8)" if not dark_mode else "rgba(0,0,0,0.6)"
            text_color = "#000000" if not dark_mode else "#FFFFFF"
            st.markdown(
                f"<div style='text-align:left; background-color:{bg_color}; color:{text_color}; padding:12px; border-radius:15px; margin:5px 0; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{msg['content']}</div>",
                unsafe_allow_html=True
            )
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ✅ Auto-save into Library (keeps last version always updated)
    if st.session_state.messages:
        if not st.session_state.saved_chats or st.session_state.saved_chats[-1] != st.session_state.messages:
            st.session_state.saved_chats.append(list(st.session_state.messages))

elif menu_choice == "Search Chats":
    st.subheader("🔍 Search Past Chats")
    query = st.text_input("Enter a keyword to search saved chats")
    if query:
        results = []
        for chat in st.session_state.saved_chats:
            for m in chat:
                if query.lower() in m["content"].lower():
                    results.append(m)
        if results:
            for r in results:
                st.write(f"**{r['role']}**: {r['content']}")
        else:
            st.info("No results found in saved chats.")

elif menu_choice == "Library":
    st.subheader("📚 Library - Saved Chats")
    if st.session_state.saved_chats:
        for i, chat in enumerate(st.session_state.saved_chats):
            with st.expander(f"💬 Chat {i+1}"):
                for m in chat:
                    st.write(f"**{m['role']}**: {m['content']}")
    else:
        st.info("No saved chats yet. Start chatting in 'New Chat' section.")
