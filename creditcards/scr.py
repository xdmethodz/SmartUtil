import re
import os
import asyncio
from urllib.parse import urlparse
from pyrogram.enums import ParseMode
from pyrogram import Client, filters

# Admin IDs
ADMIN_IDS = [7303810912, 6808763554]

# Limits
DEFAULT_LIMIT = 10000  # Card Scrapping Limit For Everyone
ADMIN_LIMIT = 50000  # Card Scrapping Limit For Admin

scrape_queue = asyncio.Queue()

def remove_duplicates(messages):
    unique_messages = list(set(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

async def scrape_messages(client, channel_id, limit, start_number=None):
    messages = []
    count = 0
    pattern = r'\d{16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'
    
    async for message in client.get_chat_history(channel_id, limit=limit):
        if count >= limit:
            break
        text = message.text if message.text else message.caption
        if text:
            matched_messages = re.findall(pattern, text)
            if matched_messages:
                formatted_messages = []
                for matched_message in matched_messages:
                    extracted_values = re.findall(r'\d+', matched_message)
                    if len(extracted_values) == 4:
                        card_number, mo, year, cvv = extracted_values
                        year = year[-2:]
                        formatted_messages.append(f"{card_number}|{mo}|{year}|{cvv}")
                messages.extend(formatted_messages)
                count += len(formatted_messages)
                
    if start_number:
        messages = [msg for msg in messages if msg.startswith(start_number)]
    messages = messages[:limit]
    return messages

def setup_scr_handler(app: Client):
    @app.on_message(filters.command(["scr"]))
    async def scr_cmd(client, message):
        args = message.text.split()[1:]
        if len(args) < 2 or len(args) > 3:
            await message.reply_text("<b>⚠️ Provide channel username and amount to scrape</b>")
            return
        channel_identifier = args[0]
        limit = int(args[1])
        max_lim = ADMIN_LIMIT if message.from_user.id in ADMIN_IDS else DEFAULT_LIMIT
        if limit > max_lim:
            await message.reply_text(f"<b>Sorry Bro! Amount over Max limit is {max_lim} ❌</b>")
            return
        start_number = args[2] if len(args) == 3 else None
        parsed_url = urlparse(channel_identifier)
        channel_username = parsed_url.path.lstrip('/') if not parsed_url.scheme else channel_identifier
        try:
            chat = await client.get_chat(channel_username)
            channel_name = chat.title
        except Exception:
            await message.reply_text("<b>Hey Bro! 🥲 Incorrect username ❌</b>")
            return
        temporary_msg = await message.reply_text("<b>Scraping in progress wait.....</b>")
        scrapped_results = await scrape_messages(client, chat.id, limit, start_number)
        unique_messages, duplicates_removed = remove_duplicates(scrapped_results)
        if unique_messages:
            file_name = f"x{len(unique_messages)}_{channel_name.replace(' ', '_')}.txt"
            with open(file_name, 'w') as f:
                f.write("\n".join(unique_messages))
            with open(file_name, 'rb') as f:
                caption = (
                    f"<b>CC Scrapped Successful ✅</b>\n"
                    f"<b>━━━━━━━━━━━━━━━━</b>\n"
                    f"<b>Source:</b> <code>{channel_name}</code>\n"
                    f"<b>Amount:</b> <code>{len(unique_messages)}</code>\n"
                    f"<b>Duplicates Removed:</b> <code>{duplicates_removed}</code>\n"
                    f"<b>━━━━━━━━━━━━━━━━</b>\n"
                    f"<b>Card-Scrapper By: <a href='https://t.me/itsSmartDev'>Smart Dev</a></b>\n"
                )
                await temporary_msg.delete()
                await client.send_document(message.chat.id, f, caption=caption)
            os.remove(file_name)
        else:
            await temporary_msg.delete()
            await client.send_message(message.chat.id, "<b>Sorry Bro ❌ No Credit Card Found</b>")
