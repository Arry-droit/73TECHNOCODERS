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
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #b0b0b0;
        text-align: center;
        margin-bottom: 2em;
    }
    .data-box {
        background-color: #1e1e1e;
        padding: 1.2em;
        border-radius: 10px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.2);
        margin-top: 1em;
        color: #ffffff;
    }
    .stApp {
        background-color: #121212;
    }
    .stTextInput>div>div>input {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #2e2e2e;
        color: #ffffff;
        border: 1px solid #3e3e3e;
    }
    .stButton>button:hover {
        background-color: #3e3e3e;
        border: 1px solid #4e4e4e;
    }
    a {
        color: #4a9eff;
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
