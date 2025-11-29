import pandas_datareader.data as web
import datetime
import requests
import os
import sys

# --- CONFIGURATION ---
WATCHLIST = [
    'AAPL.US', 'MSFT.US', 'GOOGL.US', 'AMZN.US', 'NVDA.US', 
    'TSLA.US', 'META.US', 'AMD.US', 'NFLX.US', 'PLTR.US',
    'SOUN.US', 'TEVA.US'
]

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "muthur_flight_log_839_soun")

print(f"--- 🏹 CLOUD HUNTER STARTING ---")
print(f"Scanning {len(WATCHLIST)} targets...")

found_targets = []

def send_alert(message, title, priority, tags):
    """Sends a flexible alert to your phone"""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={
                "Title": title,
                "Priority": priority, # 'high' = sound/vibrate, 'default' = normal
                "Tags": tags
            }
        )
        print("✅ Alert sent.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

# MAIN LOOP
for ticker in WATCHLIST:
    try:
        # Get Data (2 Years)
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=365*2)
        df = web.DataReader(ticker, 'stooq', start, end).iloc[::-1]

        # Calc Indicators
        df['50_MA'] = df['Close'].rolling(window=50).mean()
        df['200_MA'] = df['Close'].rolling(window=200).mean()

        # Check Today vs Yesterday
        today = df.iloc[-1]
        yesterday = df.iloc[-2]

        clean_name = ticker.replace(".US", "")
        
        # GOLDEN CROSS CHECK
        if yesterday['50_MA'] < yesterday['200_MA'] and today['50_MA'] > today['200_MA']:
            print(f"🔥 MATCH: {clean_name}")
            found_targets.append(clean_name)
        else:
            print(f". {clean_name} is cold.")

    except Exception as e:
        print(f"x Error on {ticker}")

# --- REPORTING LOGIC (UPDATED) ---
if found_targets:
    # SCENARIO A: We found gold. Scream about it.
    msg = f"Golden Cross detected on: {', '.join(found_targets)}"
    print(f"\n🔥 {msg}")
    send_alert(msg, title="🎯 HUNTER FOUND TARGETS", priority="high", tags="dart,chart_with_upwards_trend")

else:
    # SCENARIO B: Boring day. Send a polite summary.
    msg = f"Scanned {len(WATCHLIST)} stocks. No new signals today."
    print(f"\n✅ {msg}")
    send_alert(msg, title="Daily Scan Complete", priority="default", tags="clipboard,coffee")