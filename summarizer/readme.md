# 📊 Stock Summarizer with Finviz, OpenAI & Ollama

This tool fetches stock data from [Finviz.com](https://finviz.com), summarizes financial metrics using a large language model, and outputs a styled HTML report in German.  
It supports both **OpenAI's GPT-4o** and **local models via Ollama**.

---

## ✅ Features

- Scrapes and cleans up Finviz profile pages
- Summarizes financial metrics in Warren Buffett-style
- Detects catalysts and provides 3-month outlooks
- Supports both:
  - `--local` = use your own Ollama model (e.g. DeepSeek)
  - default = use OpenAI GPT-4o Mini or GPT-4o via API
- Outputs a beautiful `overview.html` report

---

## 🛠 Installation

### 1. Clone this repo (or drop the Python file in a folder)

```bash
git clone https://github.com/cblab/finance.git
cd summarizer


### 2. Install required libraries

pip install -r requirements.txt
