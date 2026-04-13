import json
import yfinance as yf
from tools.llm import call_groq

async def finbert_sentiment(text: str) -> dict:
    """Virtual replacement for ProsusAI/finbert via Groq"""
    system = "You are a financial sentiment analysis model."
    prompt = (
        "Analyze the impact of this text on financial markets or specific stocks. "
        "Output ONLY valid JSON containing 'label' (positive, negative, neutral) and 'score' (0.0 to 1.0).\n\n"
        f"TEXT:\n{text}"
    )
    res = await call_groq(prompt, system)
    try:
        return json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        return {"label": "neutral", "score": 0.5}

async def get_affected_tickers(text: str) -> list[str]:
    """Uses Groq to reliably map entities to their actual stock tickers (e.g. NSE/BSE or US)."""
    system = "You are a financial entity extraction API."
    prompt = (
        "Extract any publicly traded companies mentioned in the text. "
        "Return ONLY a JSON array of strings containing their most common stock ticker symbols "
        "(e.g., ['RELIANCE.NS', 'TCS.NS', 'AAPL']).\n\n"
        f"TEXT:\n{text}"
    )
    res = await call_groq(prompt, system)
    try:
        return json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        return []

def get_stock_snapshot(ticker: str) -> dict:
    """Uses yfinance to pull live market data."""
    try:
        tkr = yf.Ticker(ticker)
        fast_info = tkr.fast_info
        
        # Calculate % change based on previous close and last price
        prev_close = fast_info.previous_close
        last_price = fast_info.last_price
        change_pct = ((last_price - prev_close) / prev_close * 100) if prev_close else 0.0

        return {
            "price": round(last_price, 2),
            "change_pct": round(change_pct, 2),
            "volume": getattr(fast_info, 'last_volume', 0)
        }
    except Exception as e:
        print(f"Failed to fetch {ticker}: {e}")
        return {"price": 0.0, "change_pct": 0.0, "volume": 0}
