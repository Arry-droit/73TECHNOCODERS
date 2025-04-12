import streamlit as st
import json
import os
from dotenv import load_dotenv
import re
from datetime import datetime
from openai import OpenAI
import glob

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Styling ---
st.set_page_config(page_title="📈 Financial News Assistant", layout="centered")
st.markdown("""
    <style>
    /* Base theme colors */
    :root {
        --bg-primary: #121212;
        --bg-secondary: #1e1e1e;
        --bg-tertiary: #2e2e2e;
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
        --accent: #4a9eff;
        --accent-hover: #3a8eff;
        --border: #3e3e3e;
        --border-hover: #4e4e4e;
        --shadow: rgba(0,0,0,0.2);
    }
    
    /* Main container */
    .stApp {
        background-color: var(--bg-primary);
    }
    
    /* Typography */
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 0.5em;
        text-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2);
        background: none !important;
        -webkit-background-clip: unset !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2em;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Data display */
    .data-box {
        background-color: var(--bg-secondary);
        padding: 1.5em;
        border-radius: 12px;
        box-shadow: 0px 4px 15px var(--shadow);
        margin-top: 1.5em;
        color: var(--text-primary);
        border-left: 4px solid var(--accent);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .data-box:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Form elements */
    .stTextInput>div>div>input {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        border-radius: 8px;
        border: 1px solid var(--border);
        padding: 0.7em 1em;
        transition: all 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent);
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5em 1.2em;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: var(--accent);
        border-color: var(--accent-hover);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(74, 158, 255, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Links */
    a {
        color: var(--accent);
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: var(--accent-hover);
        text-decoration: underline;
    }
    
    /* Status messages */
    .element-container .stAlert {
        border-radius: 8px;
        padding: 0.5em;
    }
    
    .element-container .stAlert > div {
        border-radius: 8px;
        padding: 1em;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border);
    }
    
    /* Article styling */
    .article-link {
        display: block;
        margin-top: 0.8em;
        padding: 0.8em;
        background-color: rgba(74, 158, 255, 0.1);
        border-radius: 8px;
        border-left: 3px solid var(--accent);
        transition: all 0.2s ease;
    }
    
    .article-link:hover {
        background-color: rgba(74, 158, 255, 0.15);
        transform: translateX(3px);
    }
    
    /* Emoji styling */
    .emoji {
        font-size: 1.2em;
        margin-right: 0.3em;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

def get_latest_scraped_data():
    """Get the most recent scraped data file from the finance_data directory."""
    data_dir = "finance_data"
    if not os.path.exists(data_dir):
        return None
    
    # Get all JSON files in the finance_data directory
    files = glob.glob(os.path.join(data_dir, "finance_articles_*.json"))
    if not files:
        return None
    
    # Get the most recent file based on timestamp in filename
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def load_latest_articles():
    """Load the most recent scraped articles."""
    latest_file = get_latest_scraped_data()
    if not latest_file:
        return None
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading articles: {e}")
        return None

# --- Title & Instructions ---
st.markdown('<div class="title">📊 Financial News Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask questions about financial news and get AI-powered answers with related articles</div>', unsafe_allow_html=True)

# --- Prompt Input ---
prompt = st.text_input("🗣️ Enter your question:")

# --- Action Button ---
if st.button("🚀 Submit"):
    if prompt:
        try:
            # Load existing articles
            articles = load_latest_articles()
            if not articles:
                st.error("❌ No articles found. Please wait for the next scheduled crawl.")
                st.stop()

            # Create context from existing articles
            context = "\n\n".join([
                f"Title: {article.get('title', '')}\n"
                f"Content: {article.get('content', '')}\n"
                f"URL: {article.get('url', '')}\n"
                for article in articles
            ])

            # Generate response using existing data
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are a financial news expert. 
                        Answer questions based on the provided article summaries and context.
                        Always include 2 relevant article links that best answer the user's question.
                        Format your response with:
                        1. A direct answer to the question in 3-4 lines
                        2. Two relevant summarized article links with a line explanations of why they're relevant"""},
                        {"role": "user", "content": f"""Context from recent financial articles:
                        {context}
                        
                        Question: {prompt}
                        
                        Please provide a detailed answer with relevant article links."""}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                # Display the response
                st.success("🤖 AI Analysis")
                st.markdown(f"""
                    <div class="data-box">
                        {response.choices[0].message.content}
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"⚠️ Error generating AI response: {str(e)}")
                
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
    else:
        st.warning("✍️ Please enter a prompt to get started.")