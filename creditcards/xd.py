import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_URL = "https://data.handyapi.com/bin/"

# Helper function to fetch BIN details
async def get_bin_info(bin_prefix):
    url = f"{API_URL}{bin_prefix}"
    headers = {'HAS-0YJB9RtL3zc4rbQ4S015m38VYPy': 'your-api-key'}  # Replace with your actual API key
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None

# Command Handlers
async def check_bin(client: Client, message: Message):
    bins = []
    if message.reply_to_message:
        if message.reply_to_message.document:
            file_path = await message.reply_to_message.download()
            with open(file_path, 'r') as file:
                bins = file.read().split()
        elif message.reply_to_message.text:
            bins = message.reply_to_message.text.split()
    else:
        bins = message.text.split()[1:]

    bins = bins[:20]  # Limit to 20 BINs at a time
    if not bins:
        await message.reply_text("Please provide BINs to check.")
        return

    fetching_message = await message.reply_text(
        "<b>FETCHING ALL BIN DETAILS FROM DATABASE PLEASE WAIT ⚡️</b>", 
        parse_mode=ParseMode.HTML
    )

    bin_details = []
    for bin_prefix in bins:
        data = await get_bin_info(bin_prefix)  # Call the helper function for each BIN asynchronously
        if data:
            bin_info = (
                f"• BIN: {data.get('bin')}\n"
                f"• INFO: {data.get('info')}\n"
                f"• BANK: {data.get('bank')}\n"
                f"• COUNTRY: {data.get('country')} {data.get('country_code')}\n"
            )
            bin_details.append(bin_info)
        else:
            bin_details.append(f"• BIN: {bin_prefix}\n• INFO: Not Found\n")

    await fetching_message.delete()
    result_message = "🔍 BIN Details 📋\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(bin_details)
    await message.reply_text(result_message, parse_mode=ParseMode.HTML)

# Setup Function for Handlers
def setup_xd_handlers(app: Client):
    app.add_handler(MessageHandler(check_bin, filters.command("mbin")), group=1)
