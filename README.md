# Funding Rate Signal Bot 🤖

Automatisierter Bot, der Funding Rates von Coinglass scrappt und Arbitrage-Signale live auf GitHub bereitstellt.

## 🎯 Features

- **Live Scraping**: Coinglass Funding Rates alle 5 Min
- **GitHub Integration**: Signals direkt als JSON auf GitHub
- **No Telegram**: Vollständig serverlos – nur GitHub Pages + Actions
- **Docker Ready**: Läuft lokal oder auf VPS
- **Web UI**: Live-Dashboard mit Signalen
- **Automatisch**: GitHub Actions oder Docker Container

## 📁 Struktur

```
.
├── bot.py                    # Scraper (Docker)
├── index.html                # Web-Dashboard
├── signals.json              # Output (auto-updated)
├── requirements.txt          # Python-Dependencies
├── Dockerfile                # Docker-Image
├── docker-compose.yml        # Docker-Komposition
└── .github/workflows/
    └── update-signals.yml    # GitHub Actions Schedule
```

## 🚀 Setup

### Option 1: GitHub Actions (Kein Token-Risiko)

Push zu GitHub → Actions aktivieren → **Fertig!** Läuft automatisch alle 5 Min.

```bash
git add .
git commit -m "Init Funding Rate Bot"
git push
```

### Option 2: Docker (Lokal/VPS)

```bash
# .env erstellen (GitHub Token braucht Scope: repo)
echo "GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE" > .env

# Starten
docker-compose up -d

# Logs
docker-compose logs -f funding-bot
```

**Token erstellen:** GitHub → Settings → Developer settings → Personal tokens → Generate

## 📊 Output: signals.json

```json
[
  {
    "pair": "BTC/USDT",
    "funding": "0.052%",
    "profitable": true,
    "action": "LONG SPOT, SHORT PERP",
    "timestamp": "28.01.2026 14:32 CET",
    "exchange": "Binance"
  }
]
```

## 🌐 Web UI

`index.html` lädt `signals.json` live:
- ✅ Live Funding Rates
- 🎨 Grün = Trade, Gelb = Warte
- 🔄 Auto-Refresh alle 5 Min

```bash
python -m http.server 8000
```

## ⚙️ Konfiguration

Pairs in `bot.py` anpassen:
```python
TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
```

Profitabilität (> dieser Wert = Action):
```python
is_profitable = rate_pct > 0.05  # 0.05% Mindest-Schwelle
```

## 🔧 Troubleshooting

**Bot scrappt nicht:**
- Coinglass URL in Bot überprüfen
- User-Agent erhöhen falls blockiert
- Timeout erhöhen: `timeout=30`

**GitHub Push fail:**
- Token regenerieren
- Scope muss `repo` sein
- `signals.json` initial committen

**Docker-Fehler:**
```bash
docker logs funding-rate-bot
docker-compose logs -f
```

## 📝 License

MIT – Build & Share
