from langchain.agents import initialize_agent
from langchain_google_genai import GoogleGenerativeAI

from services.web_tools import search_tech_data, search_healthcare_data , get_stock_fundamentals
from services.finance_tools import get_stock_price,get_stock_returns
from services.analysis_tools import analyze_finance
import os
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
load_dotenv()

llm = GoogleGenerativeAI(model="models/gemini-2.0-flash",api_key=os.getenv("GOOGLE_API_KEY"))

tools = [
    search_tech_data,
    search_healthcare_data,
    get_stock_fundamentals,
    get_stock_returns,
    get_stock_price,
    analyze_finance
]

prefix = """You are a financial deep research assistant. 
Always provide **detailed, step-by-step reasoning** in plain English, 
not just the final number. 
Explain your thought process, show the data used, 
and then provide a clear conclusion.
Always provide a full, detailed with clear explanation. 
Never end the chain until you’ve compared options and recommended next steps.
"""

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
    memory=memory,
    agent_kwargs={"prefix": prefix},
    max_iterations=200,
    max_execution_time=600
)

def run_agent(query: str) -> str:
    """Runs the unified agent with the given query."""
    return agent.invoke(query)