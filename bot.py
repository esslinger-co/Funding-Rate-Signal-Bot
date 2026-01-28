#!/usr/bin/env python3
"""
Funding Rate Signal Bot
Scrapes Coinglass funding rates and updates signals.json via GitHub API
"""

import requests
import json
import time
import base64
import re
from datetime import datetime
import os

# GitHub-Konfiguration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "ghp_YOUR_TOKEN_HERE")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "esslinger-co/Funding-Rate-Signal-Bot")
SIGNALS_FILE = "signals.json"

# Coinglass-URL
COINGLASS_URL = "https://www.coinglass.com/FundingRate"

# Trading Pairs zum Monitoren
TRADING_PAIRS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "MATIC/USDT",
]

def get_github_file_sha():
    """Hole SHA der aktuellen signals.json für Update"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SIGNALS_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("sha")
        return None
    except Exception as e:
        print(f"Error getting SHA: {e}")
        return None

def push_signals_to_github(signals_data):
    """Schreibe signals.json zu GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SIGNALS_FILE}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Hole aktuelle SHA
    sha = get_github_file_sha()
    
    # Konvertiere JSON zu Base64
    content_bytes = json.dumps(signals_data, indent=2, ensure_ascii=False).encode('utf-8')
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')
    
    payload = {
        "message": f"Update: {datetime.now().strftime('%d.%m.%Y %H:%M CET')}",
        "content": content_b64,
    }
    
    if sha:
        payload["sha"] = sha
    
    try:
        r = requests.put(url, json=payload, headers=headers, timeout=10)
        if r.status_code in [200, 201]:
            print(f"✓ Signals gepusht zu GitHub - {len(signals_data)} Paare")
            return True
        else:
            print(f"✗ GitHub Push fehlgeschlagen: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"✗ Push Error: {e}")
        return False

def scrape_funding_rates():
    """Scrape Coinglass für aktuelle Funding Rates"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }
        r = requests.get(COINGLASS_URL, headers=headers, timeout=15)
        r.raise_for_status()
        
        html_lower = r.text.lower()
        signals = []
        
        for pair in TRADING_PAIRS:
            symbol, fiat = pair.split("/")
            symbol_lower = symbol.lower()
            
            # Finde Position des Symbols
            pos = html_lower.find(symbol_lower)
            if pos == -1:
                continue
            
            # Extrahiere Chunk um das Symbol (±500 Zeichen)
            start = max(0, pos - 300)
            end = min(len(r.text), pos + 500)
            chunk = r.text[start:end].lower()
            
            # Suche nach "binance" und danach nach Rate (z.B. "0.01%")
            bin_pos = chunk.find("binance")
            if bin_pos == -1:
                bin_pos = chunk.find("okx")  # Fallback
            
            if bin_pos != -1:
                # Extrahiere Text nach binance/okx
                after_exchange = chunk[bin_pos:bin_pos+200]
                
                # Regex für Prozentwerte: z.B. "0.01%", "0.001%", "-0.02%"
                rate_match = re.search(r'([-+]?\d+\.?\d*)\s*%', after_exchange)
                
                if rate_match:
                    rate_str = rate_match.group(1)
                    try:
                        rate_pct = float(rate_str)
                        rate_decimal = rate_pct / 100
                        
                        # Arbitage-Logik: Wenn Rate > 0.05%, dann LONG SPOT / SHORT PERP
                        is_profitable = rate_pct > 0.05
                        action = "LONG SPOT, SHORT PERP" if is_profitable else "Warte"
                        
                        signals.append({
                            "pair": pair,
                            "funding": f"{rate_pct:.3f}%",
                            "funding_decimal": f"{rate_decimal:.6f}",
                            "profitable": is_profitable,
                            "action": action,
                            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M CET"),
                            "exchange": "Binance"
                        })
                        print(f"  ✓ {pair}: {rate_pct:.3f}% - {action}")
                    except ValueError:
                        pass
        
        return signals
    
    except Exception as e:
        print(f"✗ Scraping Error: {e}")
        return []

def main():
    """Main Loop"""
    print(f"🤖 Funding Rate Signal Bot gestartet")
    print(f"📊 Monitore: {', '.join(TRADING_PAIRS)}")
    print(f"📁 Repo: {GITHUB_REPO}")
    print(f"🔄 Interval: 5 Minuten\n")
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scrape Coinglass...")
            signals = scrape_funding_rates()
            
            if signals:
                print(f"Pushe {len(signals)} Signale...")
                push_signals_to_github(signals)
            else:
                print("⚠️  Keine Signale gefunden")
            
            print(f"⏰ Nächster Run in 5 Min...")
            time.sleep(300)  # 5 Minuten
        
        except KeyboardInterrupt:
            print("\n✋ Bot gestoppt")
            break
        except Exception as e:
            print(f"✗ Error im Main Loop: {e}")
            time.sleep(60)  # 1 Min bei Error

if __name__ == "__main__":
    main()
