from models.schemas import AgentContext, Profile
from tools.llm import call_groq
from tools.finance import get_affected_tickers, get_stock_snapshot
import json

WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "AAPL", "TSLA"]

async def run(context: AgentContext) -> AgentContext:
    """Prediction Agent: Forecasts future signals and executes portfolio checks."""
    
    # 1. Prediction forecaster (Shared)
    system = "You are a strategic forecaster."
    prompt = (
        "Forecast 2-3 specific things to watch next as a direct result of this news event. "
        "Output ONLY a valid JSON array of strings.\n\n"
        f"TEXT:\n{context.article_text}"
    )
    res = await call_groq(prompt, system)
    try:
        context.predictions = json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        context.predictions = []
        
    # 2. Portfolio signal (Profile specific: Investor)
    if context.profile == Profile.investor:
        affected = await get_affected_tickers(context.article_text)
        signal_data = {}
        # Intersect affected tickers with our hardcoded watchlist
        for ticker in affected:
            # We fetch snap for any ticker mentioned, or just watchlist ones
            # Diagram: "check if any affected tickers match a hardcoded watchlist"
            if ticker in WATCHLIST or any(ticker in w for w in WATCHLIST):
                signal_data[ticker] = get_stock_snapshot(ticker)
        
        context.portfolio_signals = signal_data
        
    return context
