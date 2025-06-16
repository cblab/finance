# 📘 Company Brochure Generator

Dieses Projekt erstellt automatisch eine **Markdown-Broschüre** zu einem Unternehmen, basierend auf der Analyse seiner Website-Inhalte.

Es verwendet:
- `requests` und `beautifulsoup4` zum Parsen von Webseiten
- `openai` GPT-Modelle für Link-Analyse und Textgenerierung
- Streaming-Ausgabe (wahlweise in IPython oder Konsole)

---

## 🔧 Voraussetzungen

### 1. Python-Version
Python 3.9 oder höher wird empfohlen.

### 2. Installation

```bash
git clone https://github.com/dein-benutzername/brochure-generator.git
cd brochure-generator
python -m venv llms
source llms/bin/activate  # oder .\llms\Scripts\activate auf Windows
pip install -r requirements.txt