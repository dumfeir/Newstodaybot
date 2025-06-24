import os
import requests
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
from datetime import datetime

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

# ========== إرسال الأحداث إلى القناة عند استلام /start ==========
def send_events_to_channel(update: Update, context):
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

    # إرسال رسالة تأكيد للمستخدم
    update.message.reply_text("✅ تم إرسال الأحداث إلى القناة!")

# ========== تشغيل البوت ومعالجة الأوامر ==========
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # إضافة معالج لأمر /start
    dispatcher.add_handler(CommandHandler("start", send_events_to_channel))

    # بدء البوت
    updater.start_polling()
    print("✅ البوت يعمل! أرسل /start لبدء الإرسال.")
    updater.idle()

if __name__ == "__main__":
    main()
