# 📊 Financial News Assistant

A real-time financial news analysis tool that scrapes, processes, and provides insights about stock and market movements using AI-powered analysis.

## 🚀 Features

- **Automated News Collection**: Scrapes financial news from Yahoo Finance and CNBC every 6 hours
- **AI-Powered Analysis**: Uses OpenAI's GPT-3.5 to analyze news and provide insights
- **Real-time Updates**: Keeps data fresh with scheduled updates
- **User-Friendly Interface**: Clean, modern UI with dark theme
- **Smart Summarization**: Extracts key information and relevant articles
- **Stock Movement Analysis**: Explains why stocks or funds are moving up or down

## 🛠️ Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd financial-news-assistant
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web scraping

## 🏃‍♂️ Running the Application

1. Start the scheduler (in a separate terminal):

```bash
python scheduler.py
```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

## 🔄 How It Works

1. **Data Collection**:

   - Scheduler runs every 6 hours
   - Scrapes news from Yahoo Finance and CNBC
   - Extracts keywords and generates summaries
   - Saves processed data to JSON files

2. **User Interaction**:
   - Users ask questions about stock movements
   - App uses latest scraped data
   - AI analyzes context and provides insights
   - Returns relevant article links

## 📁 Project Structure

```
financial-news-assistant/
├── app.py                 # Streamlit web application
├── crawler.py            # Web scraping functionality
├── keyword_extract.py    # Article processing
├── scheduler.py          # Automated data collection
├── finance_data/         # Stored news data
└── .env                  # Environment variables
```

## ⚙️ Configuration

- Modify `keywords` in `crawler.py` to change search terms
- Adjust `max_articles` to control data volume
- Change update frequency in `scheduler.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool provides financial information for educational purposes only. Always do your own research before making investment decisions.
