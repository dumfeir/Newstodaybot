import os
import requests
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
from datetime import datetime

# إعدادات البوت
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

def get_historical_events():
    today = datetime.utcnow()
    month = today.month
    day = today.day
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    
    try:
        response = requests.get(url)
        print("جلب البيانات من Wikipedia:", response.status_code)  # طباعة حالة الاستجابة
        events = response.json().get("events", [])
        return events[:5]  # أول 5 أحداث فقط
    except Exception as e:
        print("حدث خطأ:", e)
        return []

def send_events(update: Update, context):
    user = update.message.from_user
    print(f"تم استلام /start من {user.first_name}")  # تأكيد استلام الأمر
    
    events = get_historical_events()
    if not events:
        update.message.reply_text("⚠️ لا توجد أحداث تاريخية اليوم!")
        return
    
    update.message.reply_text("📜 الأحداث التاريخية لليوم:")
    
    for event in events:
        try:
            text = f"📅 {event.get('year', '')} - {event.get('text', '')}"
            
            # إرسال الصورة إذا وجدت
            if 'pages' in event and event['pages']:
                for page in event['pages']:
                    if 'originalimage' in page:
                        image_url = page['originalimage']['source']
                        update.message.reply_photo(photo=image_url, caption=text[:1000])
                        break
                else:
                    update.message.reply_text(text)
            else:
                update.message.reply_text(text)
                
        except Exception as e:
            print(f"خطأ في إرسال الحدث: {e}")
            update.message.reply_text("❌ حدث خطأ في عرض هذا الحدث")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", send_events))
    
    print("🤖 البوت يعمل الآن...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
