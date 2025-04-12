import streamlit as st
import json
import os
from crawler import YahooFinanceScraper
from keyword_extract import extract_keywords, summarize_article
from dotenv import load_dotenv
import re
from datetime import datetime
from openai import OpenAI

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

# --- Title & Instructions ---
st.markdown('<div class="title">📊 Financial News Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask questions about financial news and get AI-powered answers with related articles</div>', unsafe_allow_html=True)

# --- Prompt Input ---
prompt = st.text_input("🗣️ Enter your question:")

# --- Action Button ---
if st.button("🚀 Submit"):
    if prompt:
        try:
            # Initialize scraper
            scraper = YahooFinanceScraper(keywords=["stock", "market"])
            scraper.scrape_yahoo_finance(max_articles=5)
            scraper.scrape_cnbc(max_articles=5)
            
            # Save and load results
            saved_file = scraper.save_results()
            if not saved_file:
                st.error("❌ Failed to fetch news data")
            else:
                try:
                    with open(saved_file, 'r', encoding='utf-8') as f:
                        articles = json.load(f)
                    
                    if not articles:
                        st.warning("⚠️ No articles found")
                    else:
                        # Process articles and create context
                        article_contexts = []
                        for article in articles:
                            content = article.get("content", "")
                            title = article.get("title", "Unknown Title")
                            url = article.get("url", "No URL provided")
                            
                            # Get summary and keywords
                            summary = summarize_article(content)
                            keywords = extract_keywords(content)
                            
                            if summary and keywords:
                                article_contexts.append({
                                    "title": title,
                                    "url": url,
                                    "summary": summary,
                                    "keywords": keywords
                                })
                        
                        # Create context for RAG
                        context = "\n\n".join([
                            f"Article: {art['title']}\nSummary: {art['summary']}\nKeywords: {art['keywords']}"
                            for art in article_contexts
                        ])
                        
                        # Generate RAG response
                        try:
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": """You are a financial news expert. 
                                    Answer questions based on the provided article summaries and context.
                                    Always include 2 relevant article links that best answer the user's question.
                                    Format your response with:
                                    1. A direct answer to the question in 3-4 lines
                                    2. Two relevant article links with a line explanations of why they're relevant"""},
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
                    st.error(f"❌ Error loading articles: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
    else:
        st.warning("✍️ Please enter a prompt to get started.")
