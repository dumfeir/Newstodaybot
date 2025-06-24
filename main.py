import os
import requests
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler
from datetime import datetime

# إعدادات البوت
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ضع_توكن_البوت_هنا_مباشرة"  # البديل إذا لم توجد متغيرات بيئية
bot = Bot(token=BOT_TOKEN)

def get_historical_events():
    """جلب الأحداث من Wikipedia API"""
    today = datetime.utcnow()
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{today.month}/{today.day}"
    
    try:
        response = requests.get(url, timeout=10)  # زيادة مهلة الانتظار
        data = response.json()
        print("✅ تم جلب البيانات بنجاح")  # رسالة تأكيد
        return data.get("events", [])[:5]  # أول 5 أحداث
    except Exception as e:
        print(f"❌ خطأ في جلب البيانات: {e}")
        return []

def send_events(update: Update, context):
    """معالجة أمر /start"""
    user = update.message.from_user
    print(f"🎯 تم استلام /start من: {user.first_name} (ID: {user.id})")
    
    events = get_historical_events()
    
    if not events:
        update.message.reply_text("⚠️ عذرًا، لا توجد أحداث تاريخية اليوم!")
        return
    
    update.message.reply_text(f"📅 الأحداث التاريخية ليوم {datetime.utcnow().day}/{datetime.utcnow().month}:")
    
    for event in events:
        try:
            text = f"🎯 السنة: {event.get('year', 'غير معروف')}\n\n{event.get('text', 'لا يوجد وصف')}"
            
            # إرسال مع صورة إذا وجدت
            if 'pages' in event:
                for page in event['pages']:
                    if 'originalimage' in page:
                        update.message.reply_photo(
                            photo=page['originalimage']['source'],
                            caption=text[:1000]  # تقليل النص إذا طويل
                        )
                        break
                else:
                    update.message.reply_text(text)
            else:
                update.message.reply_text(text)
                
        except Exception as e:
            print(f"⚠️ خطأ في إرسال حدث: {e}")
            update.message.reply_text("❌ حدث خطأ في عرض هذا الحدث")

def main():
    """تشغيل البوت"""
    print("🚀 بدء تشغيل البوت...")
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # إضافة معالج الأوامر
    dispatcher.add_handler(CommandHandler("start", send_events))
    
    # بدء البوت
    updater.start_polling()
    print("🤖 البوت يعمل الآن! أرسل /start في التليجرام")
    updater.idle()

if __name__ == "__main__":
    main()
