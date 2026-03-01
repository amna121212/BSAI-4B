import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

 
ALPHA_VANTAGE_API_KEY = "PW4QHHWTE7RV16AD"

BASE_URL = "https://www.alphavantage.co/query"


def get_stock_quote(symbol: str):
    """
    Fetch latest stock quote using Alpha Vantage GLOBAL_QUOTE endpoint.
    Returns a dict with cleaned data or an error message.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        return None, "Please enter a stock symbol (e.g., AAPL)."

    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "PASTE_YOUR_KEY_HERE":
        return None, "Missing API key. Add your Alpha Vantage key in app.py or as ALPHA_VANTAGE_API_KEY env var."

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException:
        return None, "Network error while calling the API. Try again."

    # Alpha Vantage returns: {"Global Quote": {...}} or sometimes a "Note" (rate limit) or "Error Message"
    if "Note" in data:
        return None, "API rate limit hit. Wait 1 minute and try again."
    if "Error Message" in data:
        return None, "Invalid symbol or API error."

    quote = data.get("Global Quote", {})
    if not quote:
        return None, "No data found for that symbol."

    # Clean fields
    result = {
        "symbol": quote.get("01. symbol", symbol),
        "open": quote.get("02. open", "N/A"),
        "high": quote.get("03. high", "N/A"),
        "low": quote.get("04. low", "N/A"),
        "price": quote.get("05. price", "N/A"),
        "volume": quote.get("06. volume", "N/A"),
        "latest_trading_day": quote.get("07. latest trading day", "N/A"),
        "previous_close": quote.get("08. previous close", "N/A"),
        "change": quote.get("09. change", "N/A"),
        "change_percent": quote.get("10. change percent", "N/A"),
    }
    return result, None


@app.route("/", methods=["GET", "POST"])
def index():
    stock_data = None
    error = None
    symbol = ""

    if request.method == "POST":
        symbol = request.form.get("symbol", "")
        stock_data, error = get_stock_quote(symbol)

    return render_template("index.html", stock_data=stock_data, error=error, symbol=symbol)


if __name__ == "__main__":
    # debug=True for development only
    app.run(debug=True)