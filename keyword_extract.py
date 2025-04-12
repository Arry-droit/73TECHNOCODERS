import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords(content):
    """Use OpenAI GPT to extract relevant keywords from article content."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial news analyst. Extract key information from the given article."},
                {"role": "user", "content": f"""Analyze this financial news article and provide:
1. 3-5 most important keywords or entities (companies, events, economic terms)
2. Overall sentiment (Positive/Negative/Neutral)
                3. link to the article

Article:
{content}

Format your response as:
Keywords: [comma-separated list]
Sentiment: [sentiment]"""}
            ],
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Keyword extraction failed: {e}")
        return None

def summarize_article(content):
    """Use OpenAI GPT to summarize the article."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial news summarizer. Provide concise summaries of financial articles."},
                {"role": "user", "content": f"Summarize this financial article in 2-3 sentences:\n\n{content}"}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Summarization failed: {e}")
        return None
