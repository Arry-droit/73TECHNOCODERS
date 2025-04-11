import streamlit as st
from check import fetch_stock_data
import re
from datetime import datetime

# --- Styling ---
st.set_page_config(page_title="📈 Stock Data Assistant", layout="centered")
st.markdown("""
    <style>
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2em;
    }
    .data-box {
        background-color: #f8f9fa;
        padding: 1.2em;
        border-radius: 10px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
        margin-top: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title & Instructions ---
st.markdown('<div class="title">📊 Stock Data Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask something like "What is SBI stock for 12-12-2024?"</div>', unsafe_allow_html=True)

# --- Prompt Input ---
prompt = st.text_input("🗣️ Enter your question:")

# --- NLP Parsing ---
def parse_prompt(prompt):
    print(f"Debug: Prompt - {prompt}")
    stock_symbol_match = re.search(r'\b([A-Z]{2,5}(?:\.[A-Z]{2,3})?)\b', prompt)
    stock_symbol = stock_symbol_match.group(1).upper() if stock_symbol_match else None
    print(f"Debug: Symbol - {stock_symbol}")

    date_match = re.search(r'(\d{1,2}[-/ ]\d{1,2}[-/ ]\d{2,4})', prompt)
    if date_match:
        raw_date = date_match.group(1)
        print(f"Debug: Raw Date - {raw_date}")
        for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d %m %Y", "%Y-%m-%d", "%d-%m-%y"]:
            try:
                date = datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        else:
            date = None
    else:
        date = None

    print(f"Debug: Parsed Date - {date}")
    return stock_symbol, date

# --- Action Button ---
if st.button("🚀 Submit"):
    if prompt:
        stock_symbol, date = parse_prompt(prompt)

        if stock_symbol and date:
            stock_data = fetch_stock_data(stock_symbol, date)

            if isinstance(stock_data, str):
                st.error(f"❌ {stock_data}")
            else:
                st.success(f"✅ Stock data for `{stock_symbol}` on `{date}`:")
                st.markdown(f"""
                    <div class="data-box">
                        <b>📈 Open:</b> {stock_data['open']}<br>
                        <b>📊 High:</b> {stock_data['high']}<br>
                        <b>📉 Low:</b> {stock_data['low']}<br>
                        <b>🔚 Close:</b> {stock_data['close']}<br>
                        <b>🔁 Volume:</b> {stock_data['volume']}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Could not extract a valid stock symbol or date. Please rephrase your question.")
    else:
        st.warning("✍️ Please enter a prompt to get started.")
