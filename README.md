# 🔋 Battery Telegram Bot

Ein intelligenter Telegram Bot für Batterie-Management mit AI-Integration.

## Features

- 🤖 **Intelligenter AI-Chat** mit Anthropic Claude
- 📊 **Automatische Charts** und Visualisierungen
- ⚡ **Tägliche Reports** mit witzigen Updates
- 🌤️ **Wetter-Integration** für Solar-Prognosen
- 💰 **Wirtschaftlichkeits-Analysen**

## Setup

### 1. Dependencies installieren
```bash
pip install python-telegram-bot anthropic pandas matplotlib requests
```

### 2. Environment Variables setzen
```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

### 3. Bot starten
```bash
python3 telegram_bot.py
```

## Kommandos

- `/start` - Bot starten
- `/daily` - Täglichen Report anfordern
- `/status` - Aktuellen Batterie-Status abfragen
- `/chart` - Batterie-Chart generieren
- `/help` - Hilfe anzeigen

## AI-Chat

Der Bot versteht natürliche Sprache und kann Fragen zu deiner Batterie beantworten:

- "Wie läuft meine Batterie heute?"
- "Wann war der Strom am teuersten?"
- "Wie viel Solar habe ich produziert?"

## Daten

Der Bot verwendet Batterie-Daten aus `data/day1.json` für Tests.

## Sicherheit

API Keys werden über Umgebungsvariablen gesetzt und nicht im Code gespeichert.