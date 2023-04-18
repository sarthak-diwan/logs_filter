import logging
from telegram import Update
from telegram.ext import filters,MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
import dotenv
import os
import random
import string

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

dotenv.load_dotenv()

# Define a handler function for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a simple Telegram bot for filtering cloud logs.")

async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    file_name = random_string + '.' + update.message.document.file_name.split('.')[-1]
    file = context.bot.get_file(update.message.document.file_id)
    file.download(file_name)
    context.bot.send_message(chat_id=update.message.chat_id, text='File downloaded successfully as ' + file_name + '!')


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.environ.get('BOT_TOKEN')).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    file_handler = MessageHandler(filters.Document.ALL, )
    application.run_polling()