import pandas_datareader.data as web
import datetime
import requests
import os
import sys

# --- CONFIGURATION ---
# The Hunting Ground: Tech & Semi-Conductors
WATCHLIST = [
    'AAPL.US', 'MSFT.US', 'GOOGL.US', 'AMZN.US', 'NVDA.US', 
    'TSLA.US', 'META.US', 'AMD.US', 'NFLX.US', 'PLTR.US',
    'SOUN.US', 'TEVA.US'  # <--- Added your picks here
]

# Load Secrets (or use defaults)
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "muthur_flight_log_839_soun")

print(f"--- 🏹 CLOUD HUNTER STARTING ---")
print(f"Scanning {len(WATCHLIST)} targets...")

found_targets = []

def send_alert(message):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={
                "Title": "🎯 HUNTER FOUND TARGETS",
                "Priority": "default",
                "Tags": "bow_and_arrow,chart_with_upwards_trend"
            }
        )
        print("✅ Alert sent.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

# MAIN LOOP
for ticker in WATCHLIST:
    try:
        # Get Data (2 Years for moving averages)
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=365*2)
        df = web.DataReader(ticker, 'stooq', start, end).iloc[::-1]

        # Calc Indicators
        df['50_MA'] = df['Close'].rolling(window=50).mean()
        df['200_MA'] = df['Close'].rolling(window=200).mean()

        # Check Today vs Yesterday (Did it cross JUST NOW?)
        today = df.iloc[-1]
        yesterday = df.iloc[-2]

        clean_name = ticker.replace(".US", "")
        
        # GOLDEN CROSS CHECK
        # Condition: Yesterday Short < Long  AND  Today Short > Long
        if yesterday['50_MA'] < yesterday['200_MA'] and today['50_MA'] > today['200_MA']:
            print(f"🔥 MATCH: {clean_name}")
            found_targets.append(clean_name)
        else:
            print(f". {clean_name} is cold.")

    except Exception as e:
        print(f"x Error on {ticker}")

# REPORTING
if found_targets:
    msg = f"Golden Cross detected on: {', '.join(found_targets)}"
    print(f"\n{msg}")
    send_alert(msg)
else:
    print("\n✅ Scan complete. No targets found today.")