import streamlit as st
from huggingface_hub import InferenceClient
import time

# Configure page
st.set_page_config(
    page_title="Quale Quest Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for dark theme
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --background-color: #000000;
        --secondary-background-color: #0a0a0a;
        --text-color: #ffffff;
        --font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: radial-gradient(circle at center, #030303, #000000 80%);
        color: var(--text-color);
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Chat container */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 140px);
        padding: 10px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    
    /* Header */
    .header {
        background-color: #000000;
        padding: 10px 15px;
        border-bottom: 1px solid #1a1a1a;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-title {
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        border: 1px solid white;
        border-radius: 20px;
        padding: 5px 15px;
    }
    
    /* Messages */
    .message {
        display: flex;
        margin-bottom: 10px;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .assistant-message {
        justify-content: flex-start;
    }
    
    .message-content {
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .user-message .message-content {
        background-color: rgba(5,5,5,0.9);
        border: 1px solid #1a1a1a;
        margin-right: 10px;
    }
    
    .assistant-message .message-content {
        background-color: rgba(10,10,10,0.8);
        border: 1px solid #1a1a1a;
        margin-left: 10px;
    }
    
    .avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .user-avatar {
        background-color: white;
        color: black;
    }
    
    .assistant-avatar {
        background-color: transparent;
        border: 1px solid #1a1a1a;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 15px;
        background-color: #000000;
        border-top: 1px solid #1a1a1a;
        z-index: 100;
    }
    
    /* Stickers */
    .stTextInput > div > div > input {
        background-color: rgba(5,5,5,0.9) !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 20px !important;
        color: white !important;
        padding: 10px 15px !important;
    }
    
    .stButton button {
        background-color: transparent !important;
        border: none !important;
        color: #9CA3AF !important;
    }
    
    .stButton button:hover {
        color: white !important;
    }
    
    /* Hide Streamlit branding */
    footer {display: none !important;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        margin: 0 2px;
        background-color: white;
        border-radius: 50%;
        opacity: 0.6;
    }
    
    .typing-dot-1 {
        animation: typing 1s infinite;
        animation-delay: 0s;
    }
    
    .typing-dot-2 {
        animation: typing 1s infinite;
        animation-delay: 0.2s;
    }
    
    .typing-dot-3 {
        animation: typing 1s infinite;
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0); }
    }
</style>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Create app header
st.markdown("""
<div class="header">
    <div style="width: 35px; display: flex; justify-content: center;">
        <span id="menu-button" style="cursor:pointer;">☰</span>
    </div>
    <div class="header-title">Begin Your Quest <span style="margin-left: 3px;">🔥</span></div>
    <div style="width: 35px; text-align: right;">AI <span style="margin-left: 3px;">🔥</span></div>
</div>

<script>
    // Add event listener to toggle session menu
    document.getElementById('menu-button').addEventListener('click', function() {
        const menu = document.getElementById('session-menu');
        if (menu.style.display === 'none' || menu.style.display === '') {
            menu.style.display = 'block';
        } else {
            menu.style.display = 'none';
        }
    });
</script>

<div id="session-menu" style="display:none; position: absolute; top: 50px; left: 10px; background-color: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 5px; padding: 10px; z-index: 1000; min-width: 200px;">
    <div style="border-bottom: 1px solid #1a1a1a; padding-bottom: 8px; margin-bottom: 8px;">
        <div style="font-size: 14px; font-weight: bold; color: white; margin-bottom: 5px;">Chat Sessions</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <form id="new-chat-form" action="" method="post">
                <input type="hidden" name="new_session" value="true">
                <button type="submit" style="background-color: #1a1a1a; border: none; color: white; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px;">+ New Chat</button>
            </form>
        </div>
    </div>
    <div id="session-list" style="max-height: 300px; overflow-y: auto;">
        <!-- Session list will be populated by Streamlit -->
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize client
@st.cache_resource
def get_client():
    client = InferenceClient(
        model="google/gemma-2b-it", 
        token=st.secrets["HUGGINGFACE_API_KEY"]
    )
    return client

client = get_client()

# Initialize session state
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": [
            {"role": "assistant", "content": "Welcome to Quale Quest Research Assistant. How can I help with your research today?"}
        ]
    }
    st.session_state.current_session = "default"
    st.session_state.session_names = {"default": "New Chat"}

if "typing" not in st.session_state:
    st.session_state.typing = False
    
if "session_counter" not in st.session_state:
    st.session_state.session_counter = 1
    
# Helper functions for session management
def create_new_session():
    session_id = f"session_{st.session_state.session_counter}"
    st.session_state.session_counter += 1
    st.session_state.sessions[session_id] = [
        {"role": "assistant", "content": "Welcome to Quale Quest Research Assistant. How can I help with your research today?"}
    ]
    st.session_state.session_names[session_id] = f"New Chat {st.session_state.session_counter}"
    st.session_state.current_session = session_id
    
def switch_session(session_id):
    st.session_state.current_session = session_id
    
def rename_session(session_id, new_name):
    st.session_state.session_names[session_id] = new_name
    
def delete_session(session_id):
    if session_id in st.session_state.sessions and len(st.session_state.sessions) > 1:
        del st.session_state.sessions[session_id]
        del st.session_state.session_names[session_id]
        st.session_state.current_session = list(st.session_state.sessions.keys())[0]

# Process new session or session switch requests first
if st.experimental_get_query_params().get("new_session"):
    create_new_session()
    st.experimental_set_query_params()
    st.rerun()

if session_id := st.experimental_get_query_params().get("switch_session"):
    if session_id[0] in st.session_state.sessions:
        switch_session(session_id[0])
        st.experimental_set_query_params()
        st.rerun()

# Build the session list for the menu
session_list_html = ""
for session_id, name in st.session_state.session_names.items():
    is_current = session_id == st.session_state.current_session
    session_list_html += f"""
    <div style="display: flex; justify-content: space-between; align-items: center; 
                padding: 5px; margin-bottom: 5px; 
                background-color: {'rgba(30,30,30,0.5)' if is_current else 'transparent'}; 
                border-radius: 3px;">
        <a href="?switch_session={session_id}" 
           style="color: {'white' if is_current else '#9CA3AF'}; text-decoration: none; flex-grow: 1;">
            {name}
        </a>
        {'<span style="font-size: 10px; color: #9CA3AF;">current</span>' if is_current else ''}
    </div>
    """

# Inject the session list into the menu
st.markdown(f"""
<script>
    document.addEventListener('DOMContentLoaded', (event) => {{
        document.getElementById('session-list').innerHTML = `{session_list_html}`;
    }});
</script>
""", unsafe_allow_html=True)

# Get current session messages
current_messages = st.session_state.sessions[st.session_state.current_session]

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in current_messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="message user-message">
            <div class="message-content">{msg["content"]}</div>
            <div class="avatar user-avatar">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message assistant-message">
            <div class="avatar assistant-avatar">🤖</div>
            <div class="message-content">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Show typing indicator
if st.session_state.typing:
    st.markdown(f"""
    <div class="message assistant-message">
        <div class="avatar assistant-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot typing-dot-1"></div>
                <div class="typing-dot typing-dot-2"></div>
                <div class="typing-dot typing-dot-3"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([7, 1, 1])
with col1:
    user_input = st.text_input("", placeholder="Ask your research question...", label_visibility="collapsed", key="user_input")
with col2:
    send_button = st.button("📤", key="send")
with col3:
    new_chat_button = st.button("🆕", key="new_chat", help="Start a new chat")
st.markdown('</div>', unsafe_allow_html=True)

# Handle new chat button
if new_chat_button:
    create_new_session()
    st.rerun()

# Process user input
if (user_input or send_button) and user_input:
    # Save user message to current session
    st.session_state.sessions[st.session_state.current_session].append(
        {"role": "user", "content": user_input}
    )
    
    # Set typing indicator
    st.session_state.typing = True
    st.rerun()

if st.session_state.typing:
    # Get messages from current session
    current_messages = st.session_state.sessions[st.session_state.current_session]
    
    # Generate response
    try:
        # Helper function to generate system prompt
        def generate_prompt(history, new_question):
            prompt = """You are Quale Quest's Research Assistant, a helpful AI that provides accurate, detailed information. 
            Answer questions clearly and professionally, citing sources when possible."""
            
            # Format conversation history
            formatted_history = ""
            for msg in history[-6:]:  # Include up to 6 most recent messages
                formatted_history += f"{msg['role'].title()}: {msg['content']}\n"
            
            # Add the new question
            final_prompt = f"{prompt}\n\n{formatted_history}\nUser: {new_question}\nAssistant:"
            
            return final_prompt
            
        prompt = generate_prompt(
            current_messages[:-1], 
            current_messages[-1]["content"]
        )
        
        # Call the API
        response = client.text_generation(
            prompt,
            max_new_tokens=500,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.1
        )
        
        # Save response to current session
        ai_message = response
        st.session_state.sessions[st.session_state.current_session].append(
            {"role": "assistant", "content": ai_message}
        )
        
        # Generate a session name based on the first user question
        if len(current_messages) == 2 and current_messages[0]["role"] == "assistant" and current_messages[1]["role"] == "user":
            # This is the first user message, use it to name the session
            user_first_msg = current_messages[1]["content"]
            # Truncate to first 20 chars
            session_name = user_first_msg[:20] + ("..." if len(user_first_msg) > 20 else "")
            st.session_state.session_names[st.session_state.current_session] = session_name
        
    except Exception as e:
        st.session_state.sessions[st.session_state.current_session].append({
            "role": "assistant", 
            "content": "I'm having trouble connecting to my research database. Please try again in a moment."
        })
        
    # Reset typing indicator and input
    st.session_state.typing = False
    st.session_state.user_input = ""
    
    # Rerun to update UI
    st.rerun()
