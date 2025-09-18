# Finance Bot

Finance Bot is an AI-powered assistant for financial research, stock discovery, and market analysis. It leverages Google Gemini LLM, LangChain, and custom sector/intent detection to help users explore top stocks, analyze trends, and ingest financial news.

---
## Screentshot
<img width="1135" height="887" alt="image" src="https://github.com/user-attachments/assets/01846480-dda3-44e0-994e-4cf5f61c5530" />

## Features

- **Sector & Intent Detection:** Classifies user queries into sectors (tech, healthcare, finance) and intents (top stocks, research) using LLM and keyword fallback.
- **Top Stocks & Price Lookup:** Instantly fetches top stocks and real-time prices for any sector.
- **Research Assistant:** Provides detailed, step-by-step financial research and analysis.
- **Web Ingestion:** Extracts and ingests financial news/articles for sector-specific research.
- **Streamlit Frontend:** Simple chat interface for interactive conversations and history.

---

## Project Structure
   ├── agents/  # LLM agents and unified agent logic
   ├── api/ # FastAPI routes for backend endpoints 
   ├── ingest/ # Web ingestion and text extraction 
   ├── services/ # Core business logic (intent, finance, analysis, etc.) 
   ├── utils/ # Utility scripts (e.g., web scraper) 
   ├── frontend.py # Streamlit UI ├── main.py # FastAPI app entrypoint 
   ├── requirements.txt # Python dependencies 
   ├── .env # Environment variables (API keys, config) 



---

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/mohit1233k/finance-bot.git
   cd finance-bot

   python -m venv myenv
    myenv\Scripts\activate   # On Windows
    # Or: source myenv/bin/activate   # On Linux/Mac

    pip install -r requirements.txt
    ```
2. **configure our env**
GEMINI_MODEL=models/gemini-2.0-flash
GOOGLE_API_KEY=your-google-api-key
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=finance_mvp
SECTOR_DETECT_CONF=0.6

3. **for backend run**
   ```sh
   uvicorn main:app --reload
   ```
4. ** for frontend run**
   ```sh
   streamlit run frontend.py
   ```

Created by mohit kamra


    

