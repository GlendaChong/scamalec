import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
import requests
import os
<<<<<<< HEAD
from transformers import pipeline
=======
import telebot

from dotenv import load_dotenv
load_dotenv()
>>>>>>> 450104921ea0d364258d78bdd6c340895b7a45b5

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
# NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

if not BOT_TOKEN:
    raise ValueError("The BOT_TOKEN environment variable is not set or empty.")
# if not NEWS_API_KEY:
#     raise ValueError("The NEWS_API_KEY environment variable is not set or empty.")

# Initialize the text classifier
classifier = pipeline(task="text-classification", model="phishbot/ScamLLM", top_k=None)

# Function to get news
# def get_news():
#     url = f'https://newsapi.org/v2/everything?q=anti-scam&apiKey={NEWS_API_KEY}'
#     response = requests.get(url)
#     data = response.json()
#     articles = data.get('articles', [])
#     if not articles:
#         return "No news found."
#     news_message = "Today's Anti-Scam News:\n"
#     for article in articles[:5]:  # Limiting to 5 articles
#         news_message += f"{article['title']}\n{article['url']}\n\n"
#     return news_message

# Command handler to send news
# def daily_news(update: Update, context: CallbackContext) -> None:
#     news = get_news()
#     context.bot.send_message(chat_id=update.message.chat_id, text=news)

# Function to handle /start command
def start(update: Update, context: CallbackContext) -> None:
<<<<<<< HEAD
    update.message.reply_text('Hello! Use /checkscam to check if a text is a scam or /news for the latest anti-scam news.')

SCAM_TEXT = 1

def check_scam(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Please send the text you want to check for scams:')
    return SCAM_TEXT

def scam_result(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    result = predict(user_text)
    update.message.reply_text(f"Scam check result:\n{result}")
    return ConversationHandler.END

# Function to cancel the conversation
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Scam check cancelled.')
    return ConversationHandler.END

def predict(text: str) -> str: 
    model_outputs = classifier([text])
    # Map the labels to their meanings
    return model_outputs[0]

=======
    update.message.reply_text('Hello! The bot should be working.')
>>>>>>> 450104921ea0d364258d78bdd6c340895b7a45b5

# Main function to set up the bot
def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Conversation handler for /checkscam command
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('checkscam', check_scam)],
        states={
            SCAM_TEXT: [MessageHandler(Filters.text & ~Filters.command, scam_result)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("news", daily_news))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 450104921ea0d364258d78bdd6c340895b7a45b5
