from langchain.tools import tool

@tool("analyze_finance", return_direct=False)
def analyze_finance(data: str) -> str:
    """Analyzes combined outputs from other tools and synthesizes a recommendation."""
    return f"Final analysis based on collected data:\n{data}"
