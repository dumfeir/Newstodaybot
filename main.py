import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler
from datetime import datetime

# Config
BOT_TOKEN = os.environ["BOT_TOKEN"]  # سيتم أخذ التوكن من متغيرات Railway
PORT = int(os.environ.get("PORT", 8443))

def fetch_events():
    """جلب الأحداث بدون صور"""
    today = datetime.utcnow()
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{today.month}/{today.day}"
    
    try:
        response = requests.get(url, timeout=10)
        return response.json().get("events", [])[:5]  # أول 5 أحداث
    except Exception as e:
        print(f"خطأ في جلب البيانات: {e}")
        return []

def start(update: Update, context):
    """معالجة أمر /start"""
    try:
        events = fetch_events()
        
        if not events:
            update.message.reply_text("⚠️ لا توجد أحداث اليوم!")
            return
            
        message = "📅 *أحداث اليوم في التاريخ*:\n\n"
        for event in events:
            message += f"• سنة {event.get('year', '?')}: {event.get('text', '')}\n\n"
        
        update.message.reply_text(message[:4096])  # الحد الأقصى لطول الرسالة
        
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")
        update.message.reply_text("❌ حدث خطأ، حاول لاحقًا")

def main():
    """تشغيل البوت"""
    updater = Updater(BOT_TOKEN)
    
    # للتشغيل على Railway (يستخدم Webhook)
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://{os.environ['RAILWAY_STATIC_URL']}/{BOT_TOKEN}"
    )
    
    # للتشغيل المحلي (يستخدم Polling)
    # updater.start_polling()
    
    updater.dispatcher.add_handler(CommandHandler("start", start))
    print("🤖 البوت يعمل الآن!")
    updater.idle()

if __name__ == "__main__":
    main()
