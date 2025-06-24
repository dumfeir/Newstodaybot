import os
import requests
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

# ========== إعدادات البوت ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # مثل: "@history_today"
bot = Bot(token=BOT_TOKEN)

# ========== جلب الأحداث من Wikipedia ==========
def get_historical_events():
    today = datetime.utcnow()
    month = today.month
    day = today.day
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    
    try:
        response = requests.get(url)
        events = response.json().get("events", [])
    except Exception as e:
        print("خطأ أثناء جلب الأحداث:", e)
        return []

    selected_events = []
    for event in events[:5]:  # أول 5 أحداث فقط
        text = event.get("text", "")
        year = event.get("year", "")
        title = f"{year} – {text[:60]}..."
        description = text
        image_url = None

        if event.get("pages"):
            for page in event["pages"]:
                if page.get("originalimage"):
                    image_url = page["originalimage"]["source"]
                    break

        selected_events.append({
            "title": title,
            "description": description,
            "image_url": image_url
        })

    return selected_events

# ========== نشر الأحداث في القناة ==========
def send_daily_events():
    print("جاري إرسال أحداث اليوم...")
    events = get_historical_events()

    for event in events:
        caption = f"🎯 {event['title']}\n\n{event['description']}"
        try:
            if event["image_url"]:
                bot.send_photo(chat_id=CHANNEL_ID, photo=event["image_url"], caption=caption[:1024])
            else:
                bot.send_message(chat_id=CHANNEL_ID, text=caption)
        except Exception as e:
            print(f"خطأ أثناء الإرسال: {e}")

# ========== جدولة الإرسال اليومي ==========
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_events, 'cron', hour=8, minute=0)  # 8 صباحًا UTC
scheduler.start()

print("✅ البوت يعمل وسيُرسل أحداث كل يوم الساعة 8 صباحًا (UTC)")

# إبقاء البرنامج حيًا دائمًا على Railway
try:
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
