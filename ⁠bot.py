import os
import time
import requests
import pandas as pd
import pandas_ta as ta

# --- إعدادات البوت والاتصال ---
TELEGRAM_BOT_TOKEN = "8927793889: AAEuS3XEvsLgsNkeLr5o130_LSTLqlKsVIU"  
TELEGRAM_CHAT_ID = "130116545"      

SYMBOL = "BTCUSDT"                     # العملة المراد مراقبتها
INTERVAL = "1h"                        # الفاصل الزمني (ساعة واحدة)
RSI_LOWER = 30                         # منطقة تشبع بيعي (فرصة شراء)
RSI_UPPER = 70                         # منطقة تشبع شرائي (فرصة بيع)

def send_telegram_message(message):
    """دالة لإرسال التنبيه إلى تلغرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"خطأ في إرسال الرسالة: {e}")

def check_market():
    """فحص السوق عبر بينانس وإرسال التنبيه عند توفر فرصة"""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
        response = requests.get(url)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        
        # حساب المؤشرات
        df['RSI'] = ta.rsi(df['close'], length=14)
        df['SMA_50'] = ta.sma(df['close'], length=50)
        
        last_row = df.iloc[-2]
        current_price = df.iloc[-1]['close']
        rsi = last_row['RSI']
        sma_50 = last_row['SMA_50']
        
        # شروط الصفقات
        if rsi < RSI_LOWER and current_price > sma_50:
            msg = f"🚨 *فرصة شراء مقترحة (BUY)* 🚨\n🔹 العملة: {SYMBOL}\n💵 السعر: `{current_price}`\n📊 RSI: `{round(rsi, 2)}`"
            send_telegram_message(msg)
        elif rsi > RSI_UPPER and current_price < sma_50:
            msg = f"⚠️ *تنبيه بيع / هبوط (SELL)* ⚠️\n🔹 العملة: {SYMBOL}\n💵 السعر: `{current_price}`\n📊 RSI: `{round(rsi, 2)}`"
            send_telegram_message(msg)
        else:
            print(f"السعر الحالي: {current_price} | RSI: {round(rsi, 2)} - لا توجد إشارة جديدة.")
    except Exception as e:
        print(f"خطأ أثناء فحص السوق: {e}")

if __name__ == "__main__":
    send_telegram_message("🤖 تم تشغيل بوت التداول بنجاح وهو يراقب السوق الآن 24/7...")
    # حلقة لا نهائية لفحص السوق كل ساعة (3600 ثانية)
    while True:
        check_market()
        time.sleep(3600)
