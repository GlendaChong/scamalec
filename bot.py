import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import os
import telebot


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Function to get news
def get_news():
    url = f'https://newsapi.org/v2/everything?q=anti-scam&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])
    if not articles:
        return "No news found."
    news_message = "Today's Anti-Scam News:\n"
    for article in articles[:5]:  # Limiting to 5 articles
        news_message += f"{article['title']}\n{article['url']}\n\n"
    return news_message

# Command handler to send news
def daily_news(update: Update, context: CallbackContext) -> None:
    news = get_news()
    context.bot.send_message(chat_id=update.message.chat_id, text=news)

# Function to handle /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I will send you daily anti-scam news.')

# Main function to set up the bot
def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("news", daily_news))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if name == '__main__':
    main()