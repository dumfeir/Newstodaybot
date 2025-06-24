import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler
from datetime import datetime

# Config from Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))

def fetch_events():
    """Fetch today's historical events from Wikipedia (text only)"""
    today = datetime.utcnow()
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{today.month}/{today.day}"
    
    try:
        response = requests.get(url, timeout=10)
        return response.json().get("events", [])[:5]  # First 5 events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def start_handler(update: Update, context):
    """Handle /start command"""
    try:
        events = fetch_events()
        
        if not events:
            update.message.reply_text("📭 No historical events found today!")
            return
            
        message = "📜 *Today in History*:\n\n"
        for event in events:
            message += f"• _{event.get('year', 'Unknown')}_: {event.get('text', '')}\n\n"
        
        update.message.reply_text(message[:4096], parse_mode="Markdown")  # Telegram's max length
        
    except Exception as e:
        print(f"Error in handler: {e}")
        update.message.reply_text("❌ Failed to fetch events. Please try later.")

def main():
    """Start the bot"""
    updater = Updater(BOT_TOKEN)
    
    # Register handlers
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    
    # Start polling (for local testing)
    updater.start_polling()
    
    # For Railway deployment
    # updater.start_webhook(
    #     listen="0.0.0.0",
    #     port=PORT,
    #     url_path=BOT_TOKEN,
    #     webhook_url=f"https://your-app-name.railway.app/{BOT_TOKEN}"
    # )
    
    print("🤖 Bot is now running!")
    updater.idle()

if __name__ == "__main__":
    main()
