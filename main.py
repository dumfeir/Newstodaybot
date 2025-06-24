import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler
from datetime import datetime

# تأكد من أن المتغيرات البيئية مضبوطة
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ضع_توكن_البوت_هنا"  # البديل للاختبار المحلي

def get_events():
    """جلب الأحداث من Wikipedia مع معالجة أخطاء محسنة"""
    today = datetime.utcnow()
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{today.month}/{today.day}"
    
    try:
        response = requests.get(url, timeout=15)  # زيادة المهلة
        if response.status_code == 200:
            return response.json().get("events", [])[:5]
        print(f"خطأ في API: {response.status_code}")
        return []
    except Exception as e:
        print(f"فشل جلب الأحداث: {str(e)}")
        return []

def start(update: Update, context):
    """دالة معالجة أمر /start"""
    chat_id = update.message.chat.id
    print(f"تم استلام /start من: {chat_id}")
    
    try:
        events = get_events()
        if not events:
            update.message.reply_text("🔍 لا توجد أحداث تاريخية اليوم!")
            return
            
        reply = "📜 الأحداث التاريخية لليوم:\n"
        for idx, event in enumerate(events, 1):
            reply += f"\n{idx}. سنة {event.get('year', '?')}:\n{event.get('text', '')}\n"
        
        update.message.reply_text(reply[:4000])  # تقطيع النص إذا كان طويلاً
        
    except Exception as e:
        print(f"خطأ غير متوقع: {str(e)}")
        update.message.reply_text("⚡ حدث خطأ، الرجاء المحاولة لاحقًا")

def main():
    print("🚀 بدء تشغيل البوت...")
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        
        # وضع التشغيل (يختار تلقائيًا بين webhook/polling)
        if "RAILWAY" in os.environ:  # إذا كان يعمل على Railway
            PORT = int(os.environ.get("PORT", 8443))
            updater.start_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN,
                webhook_url=f"https://{os.environ['RAILWAY_STATIC_URL']}/{BOT_TOKEN}"
            )
            print(f"🌐 Webhook نشط على: {os.environ['RAILWAY_STATIC_URL']}")
        else:  # للتشغيل المحلي
            updater.start_polling()
            print("🔍 Polling mode مفعل")
            
        print("✅ البوت يعمل الآن!")
        updater.idle()
        
    except Exception as e:
        print(f"🔥 فشل تشغيل البوت: {str(e)}")

if __name__ == "__main__":
    main()
