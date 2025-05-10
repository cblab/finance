import os
import json
import argparse
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import openai

# CLI arguments
parser = argparse.ArgumentParser(description="Stock summarizer with OpenAI or local Ollama model")
parser.add_argument("--local", action="store_true", help="Use local Ollama model instead of OpenAI API")
args = parser.parse_args()

use_local = args.local
ollama_model = "deepseek-r1:7b"
output_file = "overview.html"

tickers = list(dict.fromkeys([
    "SHOP", "ALV", "BWLPG", "GOOG", "MO", "ARCC", "CTAS", "CUBE", "IRM", "JNJ", "MAIN", "MELI", "NEE",
    "NVDA", "OHI", "PBR.A", "PG", "O", "SFM", "HIMS", "AMZN", "BRK-B", "TRMD", "LTC",
    "STAG", "PBA", "ARES", "CRWD", "OBDC", "EQNR", "ASML", "AAPL", "UL", "MSFT", "PLD",
    "SBRA", "VZ", "ADBE"
]))

# API key for OpenAI
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
if not use_local:
    if not api_key or not api_key.startswith("sk-proj-"):
        raise ValueError("Invalid or missing OpenAI API key.")
    openai.api_key = api_key

# Headers
headers = {
    "User-Agent": "Mozilla/5.0"
}

today = datetime.today().strftime("%Y-%m-%d")

# System prompt
system_prompt = (
    f"Todays date is {today}. Keep that in mind, when answering "
    "You are acting in the role of a world-class financial analyst like Warren Buffett. Analyze a stock based on financial data scraped from its Finviz profile. "
    "Ignore any navigation, ads, or UI-related text. Only begin analysis if the following key metrics are present: "
    "ROA, ROE, ROI, Revenue Growth, Cost of Revenue, Gross Profit, Operating Expenses, Operating Income, Pretax Income, "
    "Market Cap, P/E, Price/Sales, Price/Book, EPS Surprise, EPS this y, Debt/Equity, and Short Ratio or Short Float. "
    "Evaluate the stock as a value investor in the style of Warren Buffett. Identify short-term catalysts (within 3 months) "
    "and provide a 3-month forecast based on fundamentals. If news or announcements are present, summarize them separately. "
    "Respond in Markdown format in German in the style of Warren Buffett."
)

# Website scraper
class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for tag in soup.body(["script", "style", "img", "input"]):
            tag.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

# Prompt constructor
def user_prompt_for(website):
    return (
        f"You are looking at a financial website titled '{website.title}'.\n\n"
        f"Here is the scraped text content:\n\n{website.text}"
    )

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

# Summarization logic
def summarize(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}&ty=c&ta=1&p=d"
    print(f"\n🔍 Fetching data for: {ticker}")
    try:
        website = Website(url)
    except Exception as e:
        return f"[Error fetching website: {e}]"

    if use_local:
        prompt = f"{system_prompt}\n\n{user_prompt_for(website)}"
        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "[Error: No 'response' key in Ollama output]")
        except Exception as e:
            return f"[Error from local model: {e}]"
    else:
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for(website)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Error from OpenAI API: {e}]"

# HTML structure
html_parts = [
    "<html><head><meta charset='UTF-8'>",
    "<title>Stock Overview</title>",
    "<link href='https://fonts.googleapis.com/css2?family=Roboto&display=swap' rel='stylesheet'>",
    "<style>",
    "body { font-family: 'Roboto', sans-serif; background-color: #f9f9f9; color: #333; line-height: 1.6; padding: 40px; margin: 0; }",
    "h1 { font-size: 2.2em; margin-bottom: 0.5em; }",
    "h2 { margin-top: 2em; color: #2c3e50; }",
    "div { background-color: #fff; padding: 20px; margin-bottom: 40px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); max-width: 1000px; }",
    "</style></head><body><h1>Stock Overview Report</h1>"
]

# Main execution loop
for ticker in tickers:
    summary = summarize(ticker)
    html_summary = summary.replace("\n", "<br>")
    html_parts.append(f"<h2>{ticker}</h2>")
    html_parts.append(f"<div>{html_summary}</div>")

html_parts.append("<div style='margin-bottom: 150px;'></div></body></html>")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(html_parts))

print(f"\n✅ Report written to {output_file}")
