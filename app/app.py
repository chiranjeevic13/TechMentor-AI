import streamlit as st
import yaml
import sys
import os
from pathlib import Path
import time
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from src.rag.generator import Generator

# Load configuration
with open(os.path.join(project_root, "config", "config.yaml"), "r") as f:
    config = yaml.safe_load(f)
    app_config = config["app"]

# Custom CSS
def load_custom_css():
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #4A56E2;
            --secondary-color: #54C5C1;
            --background-color: #f8f9fa;
            --text-color: #333333;
            --sidebar-color: #ffffff;
        }
        
        /* General styling */
        .main {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        /* Custom sidebar styling */
        .css-1d391kg {
            background-color: var(--sidebar-color);
        }
        
        /* Headings */
        h1, h2, h3 {
            color: var(--primary-color);
            font-weight: 700;
        }
        
        /* Chat message styling */
        .chat-message {
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background-color: #E9F3FF;
            border-left: 5px solid var(--primary-color);
        }
        
        .assistant-message {
            background-color: #F0F7F4;
            border-left: 5px solid var(--secondary-color);
        }
        
        /* Card styling */
        .stcard {
            padding: 20px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stcard:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        /* Topic buttons */
        .topic-button {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px 15px;
            margin: 5px;
            transition: all 0.2s ease;
            text-align: center;
            cursor: pointer;
        }
        
        .topic-button:hover {
            background-color: #f1f7ff;
            border-color: var(--primary-color);
            transform: scale(1.02);
        }
        
        /* Logo styling */
        .logo-text {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* Loading animation */
        .typing-animation {
            display: inline-flex;
            align-items: center;
        }
        
        .typing-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--primary-color);
            margin: 0 3px;
            opacity: 0.6;
            animation: pulse 1.5s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.6; }
            50% { transform: scale(1.3); opacity: 1; }
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            font-size: 0.9rem;
            color: #888;
        }
        
        /* Source citation styling */
        .source-citation {
            background-color: #f8f9fa;
            border-left: 3px solid #ddd;
            padding: 10px 15px;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        /* Animated gradient background for the app title */
        .title-container {
            background: linear-gradient(-45deg, #4A56E2, #54C5C1, #6E7FF3, #83E8E5);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize RAG pipeline
@st.cache_resource
def load_generator():
    return Generator(os.path.join(project_root, "config", "config.yaml"))

def render_chat_message(message, is_user):
    """Render a chat message with custom styling."""
    class_name = "user-message" if is_user else "assistant-message"
    role_icon = "👤" if is_user else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {class_name}">
        <div><strong>{role_icon} {"You" if is_user else "TechMentor AI"}</strong></div>
        <div>{message}</div>
    </div>
    """, unsafe_allow_html=True)

def render_sources(sources):
    """Render sources with custom styling."""
    if not sources or all(s == "Unknown" for s in sources):
        return
    
    unique_sources = list(set([s for s in sources if s and s != "Unknown"]))
    
    if unique_sources:
        sources_html = "<div class='source-citation'><strong>Sources:</strong><ul>"
        for source in unique_sources:
            sources_html += f"<li>{source}</li>"
        sources_html += "</ul></div>"
        st.markdown(sources_html, unsafe_allow_html=True)

def render_typing_animation():
    """Render a typing animation."""
    st.markdown("""
    <div class="typing-animation">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    </div>
    """, unsafe_allow_html=True)

def render_topic_cards():
    """Render topic cards in a grid layout."""
    topics = {
        "Career Roadmaps": {
            "icon": "🛣️",
            "description": "Personalized tech career paths and skill progressions",
            "example": "How do I become a full stack developer?"
        },
        "Learning Resources": {
            "icon": "📚",
            "description": "Find the best materials to learn new tech skills",
            "example": "What are the best free resources to learn Python?"
        },
        "Project Ideas": {
            "icon": "💡",
            "description": "Creative projects to build your portfolio",
            "example": "Suggest beginner web development project ideas"
        },
        "Tech Comparisons": {
            "icon": "⚖️",
            "description": "Compare different technologies and career paths",
            "example": "Compare React vs Angular for frontend development"
        },
        "Interview Preparation": {
            "icon": "🎯",
            "description": "Prepare for technical interviews and job applications",
            "example": "What are common interview questions for frontend developers?"
        }
    }
    
    cols = st.columns(3)
    
    for i, (topic, data) in enumerate(topics.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="stcard" id="topic-{i}">
                <h3>{data['icon']} {topic}</h3>
                <p>{data['description']}</p>
                <div class="topic-button" onclick="
                    document.getElementById('chat-input').value = '{data['example']}';
                    document.querySelector('.stButton button').click();">
                    Ask: "{data['example']}"
                </div>
            </div>
            """, unsafe_allow_html=True)

# Main UI function
def main():
    # Apply custom CSS
    load_custom_css()
    generator = load_generator()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="logo-text">TechMentor AI</div>', unsafe_allow_html=True)
        
        st.markdown("### About")
        st.markdown("""
        TechMentor AI is your personalized guide to tech careers, learning paths, 
        and skill development. Ask questions about:
        
        • Career paths in tech
        • Learning resources
        • Project ideas
        • Technology comparisons
        • Interview preparation
        """)
        
        # Model info
        st.markdown("### Model Information")
        model_info = generator.llm.get_model_info()
        model_name = model_info.get('model_path', '').split('/')[-1].split('.')[0]
        
        st.markdown(f"""
        **Current Model:** {model_name}
        
        **Context Length:** {model_info.get('context_length', 'Unknown')}
        
        **Temperature:** {model_info.get('temperature', 'Unknown')}
        """)
        
        # Tech stack
        st.markdown("### Tech Stack")
        st.markdown("""
        - 🤖 **LLM:** Local GGUF Model
        - 🧠 **RAG:** Retrieval-Augmented Generation
        - 🔍 **Embeddings:** Sentence Transformers
        - 💾 **Vector DB:** ChromaDB
        - 🌐 **Dynamic Search:** Real-time web search
        """)
        
        # Footer
        st.markdown("""
        <div class="footer">
            Built with Streamlit<br>
            TechMentor AI © 2023
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    # Animated title container
    st.markdown("""
    <div class="title-container">
        <h1>Welcome to TechMentor AI</h1>
        <p>Your AI-powered guide to tech careers and learning paths</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Topic cards
    if "chat_history" not in st.session_state or not st.session_state.chat_history:
        st.markdown("### Explore Topics")
        render_topic_cards()
    
    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        render_chat_message(message["content"], message["role"] == "user")
        if message["role"] == "assistant" and "sources" in message:
            render_sources(message["sources"])
    
    # Chat input
    user_input = st.chat_input("Ask me about tech careers, learning paths, or anything tech-related!", key="chat-input")
    
    # Process user input
    if user_input:
        # Add user question to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user question
        render_chat_message(user_input, True)
        
        # Show thinking animation
        with st.container():
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown('<div class="assistant-message"><div><strong>🤖 TechMentor AI</strong></div>', unsafe_allow_html=True)
            render_typing_animation()
            
            try:
                # Generate response
                response_data = generator.generate_response(user_input)
                
                # Simulate typing for a more natural feel
                time.sleep(1)
                
                # Extract response and sources
                response_text = response_data["answer"]
                sources = response_data.get("sources", [])
                
                # Update placeholder with actual response
                thinking_placeholder.empty()
                render_chat_message(response_text, False)
                render_sources(sources)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response_text,
                    "sources": sources
                })
            except Exception as e:
                error_message = f"Error generating response: {str(e)}"
                thinking_placeholder.empty()
                render_chat_message(error_message, False)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})

if __name__ == "__main__":
    main()