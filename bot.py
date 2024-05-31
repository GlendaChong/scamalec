import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
import requests
import os
from transformers import pipeline
from bs4 import BeautifulSoup


# from dotenv import load_dotenv
# load_dotenv()

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

# Function to handle /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello, welcome to scam alec! Here are some functions of our telebot: \n' + 
                              '/checkscam: Check how likely the text is a scam\n' + 
                              '/news: Keep updated with the latest top 30 scam-related news in SG\n' +
                              '/realstories: Read real stories of individuals being scammed\n')

SCAM_TEXT = 1

def check_scam(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Please send the text you want to check for scams:')
    return SCAM_TEXT

def scam_result(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    result = predict(user_text)
    
    label_1_score = result[1]['score'] if result[1]['label'] == 'LABEL_1' else result[0]['score']
    response = f"There is a {label_1_score * 100:.2f}% chance that this is a scam! Please make sure to double check the information before proceeding. Stay safe!"
   
    update.message.reply_text(response)
    update.message.reply_text('What would you like to do next?\n1. Check another message: /checkscam \n2. Get the latest anti-scam news: /news\n'
                              + '3. Read real stories of individuals being scammed: /realstories\n'
                              + '4. End the chat: /cancel')
    
    return ConversationHandler.END


def predict(text: str) -> str: 
    model_outputs = classifier([text])
    # Map the labels to their meanings
    return model_outputs[0]


def get_real_scam_articles():
    # URL of the website to scrape
    URL = "https://www.scamalert.sg/news"
    
    # Send a GET request to the website
    response = requests.get(URL)
    
    # Check if the request was successful
    if response.status_code != 200:
        return "Failed to retrieve the page.", []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all article divs
    article_divs = soup.find_all('div', class_='card p-4')

    if not article_divs:
        return "No articles found.", []

    articles_list = []
    for article in article_divs:
        date = article.find('div', class_='card-date text-primary').get_text(strip=True)
        title_element = article.find('h4', class_='card-title').find('a')
        title = title_element.get_text(strip=True)
        link = title_element['href']
        summary = article.find('p', class_='card-text').get_text(strip=True) if article.find('p', class_='card-text') else 'No summary available'
        articles_list.append({'date': date, 'title': title, 'link': link, 'summary': summary})
    
    # Print the number of articles retrieved
    print(f"Number of articles retrieved: {len(articles_list)}")

    return articles_list


def get_real_scam_stories():
    base_url = "https://www.scamalert.sg/stories"
    
    # Function to get stories from the page
    def get_stories_from_page(page_url):
        response = requests.get(page_url)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        story_divs = soup.find_all('div', class_='card')
        
        stories = []
        for div in story_divs:
            date = div.find('div', class_='card-date text-primary').get_text(strip=True)
            title_element = div.find('h4', class_='card-title').find('a')
            title = title_element.get_text(strip=True)
            link = base_url + title_element['href']
            summary = div.find('p', class_='card-text').get_text(strip=True) if div.find('p', class_='card-text') else 'No summary available'
            stories.append({'date': date, 'title': title, 'link': link, 'summary': summary})
        return stories
    
    # Scrape stories from the page
    stories_list = get_stories_from_page(base_url)
    
    # Print the number of stories retrieved
    print(f"Number of stories retrieved: {len(stories_list)}")

    return stories_list


def news(update: Update, context: CallbackContext) -> None:
    articles = get_real_scam_articles()

    if not articles:
        update.message.reply_text("No articles found.")
        return

    context.user_data['articles'] = articles  # Store articles in context.user_data
    context.user_data.pop('stories', None)  # Remove stories from context.user_data if present
    context.user_data['article_index'] = 0  # Initialize the article index

    article = articles[0]
    text = f"Date: {article['date']}\nTitle: {article['title']}\nLink: {article['link']}"

    keyboard = [
        [
            InlineKeyboardButton("Previous", callback_data=f"prev_article_{0}"),
            InlineKeyboardButton("Next", callback_data=f"next_article_{0}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text=text, reply_markup=reply_markup)

    
    
def display_article(update: Update, context: CallbackContext, index: int) -> None:
    article = context.user_data['articles'][index]
    text = f"Date: {article['date']}\nTitle: {article['title']}\nLink: {article['link']}\nSummary: {article['summary']}"

    keyboard = [
        [
            InlineKeyboardButton("Previous", callback_data=f"prev_article_{index}"),
            InlineKeyboardButton("Next", callback_data=f"next_article_{index}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    query.edit_message_text(text=text, reply_markup=reply_markup)


def button_articles(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    article_index = context.user_data.get('article_index', 0)

    if "next" in query.data:
        article_index = min(article_index + 1, len(context.user_data['articles']) - 1)
    elif "prev" in query.data:
        article_index = max(article_index - 1, 0)

    context.user_data['article_index'] = article_index

    display_article(update, context, article_index)



def real_stories(update: Update, context: CallbackContext) -> None:
    stories = get_real_scam_stories()

    if not stories:
        update.message.reply_text("No stories found.")
        return

    context.user_data['stories'] = stories  # Store stories in context.user_data
    context.user_data.pop('articles', None)  # Remove articles from context.user_data if present
    context.user_data['story_index'] = 0  # Initialize the story index

    story = stories[0]
    text = f"Date: {story['date']}\nTitle: {story['title']}\nLink: {story['link']}\nStory: {story['summary']}"

    keyboard = [
        [
            InlineKeyboardButton("Previous", callback_data=f"prev_story_{0}"),
            InlineKeyboardButton("Next", callback_data=f"next_story_{0}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text=text, reply_markup=reply_markup)


def display_story(update: Update, context: CallbackContext, index: int) -> None:
    story = context.user_data['stories'][index]
    text = f"Date: {story['date']}\nTitle: {story['title']}\nLink: {story['link']}\nStory: {story['summary']}"

    keyboard = [
        [
            InlineKeyboardButton("Previous", callback_data=f"prev_story_{index}"),
            InlineKeyboardButton("Next", callback_data=f"next_story_{index}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    query.edit_message_text(text=text, reply_markup=reply_markup)


def button_stories(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    story_index = context.user_data.get('story_index', 0)

    if "next" in query.data:
        story_index = min(story_index + 1, len(context.user_data['stories']) - 1)
    elif "prev" in query.data:
        story_index = max(story_index - 1, 0)
    
    context.user_data['story_index'] = story_index
    
    display_story(update, context, story_index)


# Function to cancel the conversation
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Thank you for using scam alec! Do remmeber to always stay safe and vigilant! Bye!')
    return ConversationHandler.END

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

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("realstories", real_stories))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(conv_handler)

    # Register CallbackQueryHandlers
    dispatcher.add_handler(CallbackQueryHandler(button_articles, pattern=r'^prev_article_\d+|^next_article_\d+'))
    dispatcher.add_handler(CallbackQueryHandler(button_stories, pattern=r'^prev_story_\d+|^next_story_\d+'))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
