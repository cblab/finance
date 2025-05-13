import os
import json
import argparse
import requests
import pandas as pd
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import openai
from openai import OpenAI as OpenRouterClient

# Argumente parsen
parser = argparse.ArgumentParser()
parser.add_argument("--local", action="store_true")
parser.add_argument("--openrouter", action="store_true")
args = parser.parse_args()

use_local = args.local
use_openrouter = args.openrouter

# Modellnamen und Dateipfade
ollama_model = "deepseek-r1:7b"
overview_file = "overview.html"
risk_file = "risk_report.html"
weights_file = "weights.csv"

# Umgebungsvariablen laden
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not use_local and not use_openrouter:
    if not api_key or not api_key.startswith("sk-proj-"):
        raise ValueError("Invalid or missing OpenAI API key.")
    openai.api_key = api_key

if use_openrouter:
    if not openrouter_api_key:
        raise ValueError("Fehlender OpenRouter API Key.")
    openrouter_client = OpenRouterClient(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )

headers = {"User-Agent": "Mozilla/5.0"}
today = datetime.today().strftime("%Y-%m-%d")

# Ticker oder URLs
tickers = list(dict.fromkeys([
    "SHOP", "https://www.onvista.de/aktien/kennzahlen/Allianz-Aktie-DE0008404005", "https://www.onvista.de/aktien/kennzahlen/Muenchener-Rueck-Aktie-DE0008430026"
]))

# Gewichtungen laden
if not os.path.exists(weights_file):
    raise FileNotFoundError("weights.csv nicht gefunden.")

with open(weights_file, newline='', encoding='utf-8') as f:
    sample = f.read(2048)
    dialect = csv.Sniffer().sniff(sample)
    f.seek(0)
    df_weights = pd.read_csv(f, delimiter=dialect.delimiter)

df_weights.columns = [col.strip() for col in df_weights.columns]
gewichtung_col = [col for col in df_weights.columns if "gewicht" in col.lower()][0]
df_weights[gewichtung_col] = df_weights[gewichtung_col].astype(str).str.replace(",", ".", regex=False).astype(float)
weights_text = df_weights.to_markdown(index=False)

system_prompt = (
    f"Heute ist der {today}. "
    "Du agierst in der Rolle eines Weltklasse-Finanzanalysten. Analysiere eine Aktie basierend auf den Webseiteninhalten. "
    "Ignoriere Navigations- oder UI-Texte. Starte die Analyse und benutze dabei so viele wie möglich der folgende Kennzahlen: "
    "ROA, ROE, ROI, Revenue Growth, Cost of Revenue, Gross Profit, Operating Expenses, Operating Income, Pretax Income, "
    "Market Cap, P/E, Price/Sales, Price/Book, EPS Surprise, EPS this y, Debt/Equity, und Short Ratio oder Short Float. "
    "Bewerte die Aktie im Stil eines Value-Investors wie Warren Buffett. "
    "Erkenne kurzfristige Katalysatoren (innerhalb der nächsten 3 Monate) und gib eine 3-Monats-Prognose ab. "
    "Falls News oder Ankündigungen vorliegen, fasse diese separat zusammen. "
    "Antworte in deutscher Sprache im Markdown-Format."
)

class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for tag in soup.body(["script", "style", "img", "input"]):
            tag.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

def user_prompt_for(website):
    return f"You are looking at a financial website titled '{website.title}'.\n\nHere is the scraped text content:\n\n{website.text}"

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(identifier):
    if identifier.startswith("http"):
        url = identifier
    else:
        url = f"https://finviz.com/quote.ashx?t={identifier}&ty=c&ta=1&p=d"

    print(f"\n🔍 {identifier}")
    try:
        website = Website(url)
    except Exception as e:
        return f"[Fehler beim Laden: {e}]"

    if use_local:
        prompt = f"{system_prompt}\n\n{user_prompt_for(website)}"
        payload = {"model": ollama_model, "prompt": prompt, "stream": False}
        try:
            r = requests.post("http://localhost:11434/api/generate", headers={"Content-Type": "application/json"}, data=json.dumps(payload))
            r.raise_for_status()
            return r.json().get("response", "[Fehler: Kein response-Feld]")
        except Exception as e:
            return f"[Fehler vom lokalen Modell: {e}]"

    elif use_openrouter:
        try:
            response = openrouter_client.chat.completions.create(
                model="qwen/qwen3-235b-a22b",
                messages=messages_for(website),
                extra_headers={
                    "HTTP-Referer": "https://deinprojekt.de",
                    "X-Title": "FinanzanalyseTool"
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Fehler von OpenRouter API: {e}]"

    else:
        try:
            response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages_for(website))
            return response.choices[0].message.content
        except Exception as e:
            return f"[Fehler von OpenAI API: {e}]"

def generate_html(title, sections, path):
    html = [
        "<html><head><meta charset='UTF-8'>",
        f"<title>{title}</title>",
        "<link href='https://fonts.googleapis.com/css2?family=Roboto&display=swap' rel='stylesheet'>",
        "<style>",
        "body { font-family: 'Roboto', sans-serif; background-color: #f9f9f9; color: #333; line-height: 1.6; padding: 40px; margin: 0; }",
        "h1 { font-size: 2.2em; margin-bottom: 0.5em; }",
        "h2 { margin-top: 2em; color: #2c3e50; }",
        "div { background-color: #fff; padding: 20px; margin-bottom: 40px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); max-width: 1000px; }",
        "</style></head><body>",
        f"<h1>{title}</h1>"
    ]
    html.extend(sections)
    html.append("<div style='margin-bottom: 150px;'></div></body></html>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"✅ {path}")

overview_sections = []
for identifier in tickers:
    result = summarize(identifier)
    html_result = result.replace("\n", "<br>")
    overview_sections.append(f"<h2>{identifier}</h2>")
    overview_sections.append(f"<div>{html_result}</div>")

generate_html("Stock Overview Report", overview_sections, overview_file)

def generate_risk_report(input_html="overview.html", output_html="risk_report.html"):
    with open(input_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        raw_text = soup.get_text(separator="\n", strip=True)

    prompt = (
        f"Du agierst in der Rolle von Warren Buffett. Heute ist der {today}. "
        "Du bewertest das Gesamtportfolio basierend auf den folgenden Einzelanalysen.\n"
        "Berücksichtige dabei auch die Gewichtungen der Positionen.\n\n"
        "Erstelle einen Risikobericht in Markdown mit folgenden Punkten:\n"
        "- Überbewertungen\n- Schwache Fundamentaldaten\n- Klumpenrisiken\n"
        "- Zyklische Schwächen\n- Makroökonomische Risiken\n\n"
        f"### Gewichtungen im Portfolio:\n{weights_text}\n\n"
        f"### Detailanalysen:\n{raw_text}"
    )

    if use_local:
        payload = {"model": ollama_model, "prompt": prompt, "stream": False}
        try:
            r = requests.post("http://localhost:11434/api/generate", headers={"Content-Type": "application/json"}, data=json.dumps(payload))
            r.raise_for_status()
            result = r.json().get("response", "[Fehler: Kein response-Feld]")
        except Exception as e:
            result = f"[Fehler vom lokalen Modell: {e}]"

    elif use_openrouter:
        try:
            response = openrouter_client.chat.completions.create(
                model="qwen/qwen3-235b-a22b",
                messages=[
                    {"role": "system", "content": "Du agierst in der Rolle von Warren Buffett, ein vorsichtiger Value-Investor."},
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "https://deinprojekt.de",
                    "X-Title": "FinanzanalyseTool"
                }
            )
            result = response.choices[0].message.content
        except Exception as e:
            result = f"[Fehler von OpenRouter API: {e}]"

    else:
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Du agierst in der Rolle von Warren Buffett, ein vorsichtiger Value-Investor."},
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content
        except Exception as e:
            result = f"[Fehler von OpenAI API: {e}]"

    html_result = result.replace("\n", "<br>")
    generate_html("Risikobericht – Portfolioanalyse", [f"<div>{html_result}</div>"], output_html)

generate_risk_report()
