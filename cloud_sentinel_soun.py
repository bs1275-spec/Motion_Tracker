import pandas_datareader.data as web
import datetime
import requests
import os
import sys

# --- CONFIGURATION ---
TICKER = "SOUN.US"
# We read these from the Cloud's "Secret Vault" (Environment Variables)
# If running locally for testing, we default to your values
STOP_LOSS_PRICE = float(os.getenv("STOP_LOSS_PRICE", 11.50))
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "muthur_flight_log_839_soun")

print(f"--- ☁️ CLOUD SENTINEL STARTING ---")
print(f"Target: {TICKER} | Trigger: ${STOP_LOSS_PRICE}")

def send_alert(price):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=f"📉 CRITICAL ALERT: {TICKER} dropped to ${price:.2f}. Sell now!",
            headers={
                "Title": f"SELL {TICKER} NOW",
                "Priority": "high",
                "Tags": "rotating_light,money_with_wings"
            }
        )
        print("✅ Alert sent.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

try:
    # 1. Get Data (Stooq)
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=5)
    df = web.DataReader(TICKER, 'stooq', start, end)

    if df.empty:
        print("⚠️ No data received.")
        sys.exit(0) # Exit cleanly

    current_price = df['Close'].iloc[0]
    print(f"Current Price: ${current_price:.2f}")

    # 2. Check Price
    if current_price < STOP_LOSS_PRICE:
        print(f"🔴 PRICE DROP DETECTED")
        send_alert(current_price)
    else:
        print(f"✅ Safe. (Above ${STOP_LOSS_PRICE})")

except Exception as e:
    print(f"❌ Script failed: {e}")
    sys.exit(1)