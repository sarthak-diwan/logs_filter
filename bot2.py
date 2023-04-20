from telethon import TelegramClient, events
import dotenv
import os
import logging
import random
import string
from log_parser import LogParser
import shutil
import asyncio
from core_utils import extract_archive, insert_hash, insert_victims, check_hash
from progress import Progress
from collections import defaultdict

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

dotenv.load_dotenv()

tasks = defaultdict(list)

bot = TelegramClient('bot', int(os.environ.get("API_ID",'123')), os.environ.get("API_TOKEN",'')).start(bot_token=os.environ.get('BOT_TOKEN', ''))
# Define a dictionary to store progress data for each user
progress_data = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hello! I\'m a simple Telegram bot for filtering cloud logs.')
    raise events.StopPropagation

# Define a handler function for /progress command
@bot.on(events.NewMessage(pattern='/progress'))
async def show_progress(event):
    user_id = event.chat_id
    if len(tasks[user_id]):
        progress_message = ''
        for prog in tasks[user_id]:
            progress_message += f'{prog.file} => {prog.progress}\n'
        await event.respond(progress_message)
    else:
        await event.respond('No active downloads.')
    raise events.StopPropagation

@bot.on(events.NewMessage(func=lambda e: e.document))
async def download_file(event):
    user_id = event.chat_id
    progress_data[user_id] = {'progress':'starting ...'}

    original_file_name = event.document.attributes[0].file_name

    if check_hash(str(event.document.id)):
        await event.respond(f'File {original_file_name} already in database!')
        raise events.StopPropagation
    
    prog = Progress(original_file_name)
    tasks[user_id].append(prog)

    # Generate a random file name 
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    file_name = random_string + '.' + event.document.mime_type.split('/')[-1]

    # Define a progress callback function
    async def progress_callback(current, total) -> None:
        progress_percent = current/total*100
        prog.update_progress(f'Current progress: {progress_percent:.2f}%')

    def progress_callback_sync(progress_str) -> None:
        prog.update_progress(progress_str)
    
    # Download the file contents
    await bot.download_media(event.document, file_name, progress_callback=progress_callback)

    await event.respond('File downloaded successfully as ' + file_name + '! .. Now extracting file ...')
    loop = asyncio.get_event_loop()
    extracted_folder = await loop.run_in_executor(None, extract_archive, file_name, progress_callback_sync)
    if extracted_folder == '':
        await event.respond('Error in file extraction.')
        raise events.StopPropagation
    await event.respond('File extracted successfully.')

    lp=LogParser(extracted_folder)
    victims=lp.parse_all()
    # inserted = db.insert_victims(victims, progress_callback_sync)
    inserted = await loop.run_in_executor(None, insert_victims, victims,progress_callback_sync)
    await event.respond(f'Inserted {inserted} victims!')

    insert_hash(str(event.document.id), original_file_name)
    tasks[user_id].remove(prog)
    shutil.rmtree(extracted_folder)
    os.remove(file_name)


def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()