from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from pyrogram.enums import ParseMode
import os
from converter.callback_handlers import handle_callback_query  # Import the function from the subscript
# Import the handlers
from decoders.decoders import setup_decoders_handler
from others.privacy import setup_privacy_handler
from others.yth import setup_yth_handler
from others.info import setup_info_handler
from others.times import setup_time_handler
from others.privacy import setup_privacy_handler
from crypto.binance import setup_binance_handler
from tempmail.tempmail import setup_temp_mail_handler
from crypto.crypto import setup_crypto_handler
from others.fake import setup_fake_handler
from educationutils.education import setup_education_handler
from aitools.gpt import setup_gpt_handlers 
from others.ip import setup_ip_handlers
from others.admin import setup_admin_handlers
from others.downloaders import setup_downloader_handler
from others.downloaders import initialize_admin_handler
from others.pin import setup_pinterest_handler
from others.dl import setup_dl_handlers
from others.spotify import setup_spotify_handler
from educationutils.grammar import setup_eng_handler
from creditcards.gen import setup_credit_handlers
from creditcards.db import setup_db_handlers
from creditcards.extras import setup_bin_handlers
from creditcards.filter import setup_filter_handlers
from educationutils.mail import setup_mail_handlers
from aitools.gemi import setup_gem_handler
from converter.converter import setup_aud_handler
from converter.down import setup_ws_handler
from converter.ss import setup_ss_handler
from converter.quote import setup_q_handler
from converter.git import setup_git_handler
from stringsession.string import setup_string_handler

# Replace these with your actual API details
API_ID = "24602058"  # Replace with your API ID
API_HASH = "b976a44ccb8962b20113113f84aeebf6"  # Replace with your API Hash
BOT_TOKEN = "7941865929:AAFh8u_6r7FCEAG564vZ3bvvdphZ-QRFBPg"  # Replace with your Bot Token

# Initialize the bot client
app = Client(
    "app_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Setup handlers
setup_decoders_handler(app)
setup_privacy_handler(app)
setup_yth_handler(app)
setup_info_handler(app)
setup_time_handler(app)
setup_binance_handler(app)
setup_temp_mail_handler(app)
setup_crypto_handler(app)
setup_fake_handler(app)
setup_education_handler(app)
setup_gpt_handlers(app)
setup_ip_handlers(app)
setup_admin_handlers(app)
setup_downloader_handler(app)
setup_pinterest_handler(app)
setup_dl_handlers(app)
setup_spotify_handler(app)
setup_eng_handler(app)
setup_credit_handlers(app)
setup_db_handlers(app)
setup_bin_handlers(app)
setup_filter_handlers(app)
setup_mail_handlers(app)
setup_gem_handler(app)
setup_aud_handler(app)
setup_ws_handler(app)
setup_ss_handler(app)
setup_q_handler(app)
setup_git_handler(app)
setup_string_handler(app)
initialize_admin_handler(app)
@app.on_message(filters.command("start") & filters.private)
async def send_start_message(client, message):
    chat_id = message.chat.id
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name

    # Animation messages
    animation_message = await message.reply_text("<b>Starting Smart Tool ⚙️...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)  # Use asyncio.sleep instead of sleep
    await animation_message.edit_text("<b>Generating Session Keys Please Wait...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)  # Use asyncio.sleep instead of sleep
    await animation_message.delete()

    # Main welcome message
    start_message = (
        f"<b>Hi {full_name}! Welcome to this bot</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='https://t.me/abirxdhackz'>Smart Tool ⚙️</a></b>: The ultimate toolkit on Telegram, offering education, AI, downloaders, temp mail, credit card tool, and more. Simplify your tasks with ease!\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't forget to <a href='https://t.me/ModVipRM'>join</a> for updates!</b>"
    )

    await message.reply_text(
        start_message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Main Menu", callback_data="main_menu")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/ModVipRM"),
             InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")]
        ]),
        disable_web_page_preview=True,
    )

@app.on_callback_query()
async def handle_callback(client, callback_query):
    await handle_callback_query(client, callback_query)

print("Bot is running...")
app.run()
