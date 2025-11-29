import pandas_datareader.data as web
import datetime
import time
import requests 

# --- 🛰️ MUTHUR CONFIGURATION ---
TICKER = "SOUN.US"
STOP_LOSS_PRICE = 11.50   # 🚨 REAL DANGER LINE (Set to 15.00 to test)
CHECK_INTERVAL = 60       # How often to check price (seconds)
ALERT_COOLDOWN = 300      # Wait 5 mins between alerts so you don't get spammed
NTFY_TOPIC = "muthur_flight_log_839_soun" 

print(f"--- 📡 SENTINEL ONLINE: Watching {TICKER} ---")
print(f"Trigger Price: ${STOP_LOSS_PRICE:.2f}")
print(f"Uplink Channel: https://ntfy.sh/{NTFY_TOPIC}\n")

# --- 1. STARTUP PING (Confirm Connection) ---
try:
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}", 
        data=f"📡 MUTHUR ONLINE. Watching {TICKER} below ${STOP_LOSS_PRICE:.2f}", 
        headers={
            "Title": "System Active", 
            "Tags": "satellite"
        }
    )
    print("✅ Startup signal sent to phone.\n")
except Exception as e:
    print(f"⚠️ Could not send startup signal: {e}\n")

def send_alert(price):
    """Sends a priority alert to your phone"""
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
        print("✅ Alert sent to phone.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

# --- 2. MAIN WATCHDOG LOOP ---
while True:
    try:
        # Get Data (Limit to last 5 days for speed)
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=5) 
        df = web.DataReader(TICKER, 'stooq', start, end)
        
        if df.empty:
            time.sleep(10)
            continue

        current_price = df['Close'].iloc[0]
        now = datetime.datetime.now().strftime("%H:%M:%S")

        # Check Price
        if current_price < STOP_LOSS_PRICE:
            print(f"\n[{now}] 🔴 PRICE DROP: ${current_price:.2f}")
            send_alert(current_price)
            
            # Anti-Spam: Wait for cooldown before checking again
            print(f"   (Cooling down for {ALERT_COOLDOWN}s...)")
            time.sleep(ALERT_COOLDOWN) 
            
        else:
            # Safe Zone
            print(f"[{now}] ✅ Holding steady: ${current_price:.2f}", end="\r")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n👋 Sentinel deactivated.")
        break
    except Exception as e:
        print(f"\n⚠️ Glitch: {e}")
        time.sleep(CHECK_INTERVAL)