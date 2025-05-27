import ccxt
import pandas as pd
import requests
import time

# تنظیمات اولیه
telegram_token = 'توکن ربات'
chat_id = 'آی‌دی چت'
symbols = ['BTC/USDT', 'ETH/USDT']
timeframes = ['15m', '1h', '4h']
limit = 200
threshold = 0.1  # حساسیت تماس با نواحی

def send_text_telegram(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    return requests.post(url, data=data)

def detect_zones(df):
    highs = df['high'].rolling(5, center=True).max()
    lows = df['low'].rolling(5, center=True).min()
    zones = []
    for i in range(2, len(df) - 2):
        if df['high'][i] == highs[i]:
            zones.append(round(df['high'][i], 2))
        if df['low'][i] == lows[i]:
            zones.append(round(df['low'][i], 2))
    return list(set(zones))

def determine_bias(df):
    try:
        if df['close'].iloc[-1] > df['close'].iloc[-5]:
            return "📈 صعودی"
        elif df['close'].iloc[-1] < df['close'].iloc[-5]:
            return "📉 نزولی"
        else:
            return "⚪ خنثی"
    except:
        return "❓ نامشخص"

# ربات فعال شد
send_text_telegram("🤖 ربات تحلیل بازار فعال شد! ✅")

exchange = ccxt.binance()

while True:
    for symbol in symbols:
        for tf in timeframes:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                zones = detect_zones(df)
                if not zones:
                    continue

                current_high = max(zones)
                current_low = min(zones)
                bias = determine_bias(df)

                message = f"""
📊 *تحلیل {symbol.replace('/USDT', '')} ({tf})*
━━━━━━━━━━━━━━━
🔹 *ناحیه‌ها:* {len(zones)}
🔺 *سقف:* `{current_high}`
🔻 *کف:* `{current_low}`
📡 *وضعیت بازار:* {bias}
━━━━━━━━━━━━━━━
🤖 @SAYACRYPTOBOT
"""
                send_text_telegram(message)

                # قیمت فعلی و بررسی برخورد
                price = exchange.fetch_ticker(symbol)['last']
                for z in zones:
                    if abs(price - z) <= threshold:
                        kind = "🔺 سقف" if z >= current_high else "🔻 کف"
                        alert = f"""
💥 *{symbol.replace('/USDT', '')} تایم‌فریم {tf}*
{kind} در قیمت `{z}` با موفقیت زده شد ✅
📈 قیمت فعلی: `{price}`
━━━━━━━━━━━━━━━
🤖 @SAYACRYPTOBOT
"""
                        send_text_telegram(alert)
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ خطا: {e}")
                continue
    time.sleep(60)  # هر دقیقه بررسی دوباره
