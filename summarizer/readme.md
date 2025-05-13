# 📊 Stock Summarizer with Finviz, OpenAI & Ollama

This tool fetches stock data from [Finviz.com](https://finviz.com), summarizes financial metrics using a large language model, and outputs a styled HTML report in German.  
It supports both **OpenAI's GPT-4o**, **Openrouter models** and **local models via Ollama**.

---

## ✅ Features

- Scrapes and cleans up Finviz profile pages
- Summarizes financial metrics in Warren Buffett-style
- Detects catalysts and provides 3-month outlooks
- Supports both:
  - `--local` = use your own Ollama model (e.g. DeepSeek)
  - `--openrouter` = use Openrouter (e.g. qwen/qwen3-235b-a22b)
  - default = use OpenAI GPT-4o Mini or GPT-4o via API
- Outputs a beautiful `overview.html` report with ticker/company related financial analysis for each ticker
- Asseses the whole formerly generated report and creates another report called `risk_analysis.html`

---

## 🛠 Installation

### 1. Clone this repo (or drop the Python file in a folder)

```bash
git clone https://github.com/cblab/finance.git
cd summarizer


### 2. Install required libraries

pip install -r requirements.txt
