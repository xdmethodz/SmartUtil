import re
import os
import asyncio
from urllib.parse import urlparse
from pyrogram import Client, filters

# Replace this SESSION STRING with your actual SESSION_STRING
SESSION_STRING = "BQF3ZcoAsX0yc18HrzrBGcI8rNpM02CXtzn5YPHRhTs725h-OjM3KPGwv_yckjVNlFy7M6jT9u2NbAu1z2eOZzRMTg2FVPoBZ7LmPrCksegO3yK1irJjWh0f8yk3LlU1uGqRLC0ZlrJSGIzuqiF9vj7S_K8AU25Pw5IXaTuubXwPET65a6HfGtxmi6gbAQ-ayjiVcavTamd_Wc_QWS17Am4fQoLF_8fwP59sWcTY5PrXVdLfmke5xLODmxVHqBpoVkpccnxWDOskJwZXYFwoysclMcZ2V9xRiKlUpfVmgxUmSRX1GbCzHSBXCUUgBpZILJw576l7KOByjXyly1y-gVRvvrciggAAAAHWFal6AA"

# Admin IDs
ADMIN_IDS = [7303810912, 6249257243]

# Limits
DEFAULT_LIMIT = 10000  # Card Scrapping Limit For Everyone
ADMIN_LIMIT = 50000  # Card Scrapping Limit For Admin

# Initialize the user client
user = Client(
    "user_session",
    session_string=SESSION_STRING,
    workers=1000
)

async def scrape_messages(client, channel_username, limit, start_number=None):
    messages = []
    count = 0
    pattern = r'\d{16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'
    async for message in user.search_messages(channel_username):
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

def remove_duplicates(messages):
    unique_messages = list(set(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

def setup_scr_handler(app):
    @app.on_message(filters.command(["scr", "ccscr", "scrcc"]) & (filters.group | filters.private))
    async def scr_cmd(client, message):
        args = message.text.split()[1:]
        if len(args) < 2 or len(args) > 3:
            await message.reply_text("<b>⚠️ Provide channel username and amount to scrape</b>")
            return
        channel_identifier = args[0]
        limit = int(args[1])

        # Check if from_user is available
        if message.from_user is None:
            max_lim = DEFAULT_LIMIT
        else:
            max_lim = ADMIN_LIMIT if message.from_user.id in ADMIN_IDS else DEFAULT_LIMIT

        if limit > max_lim:
            await message.reply_text(f"<b>Sorry Bro! Amount over Max limit is {max_lim} ❌</b>")
            return

        start_number = args[2] if len(args) == 3 else None
        parsed_url = urlparse(channel_identifier)
        channel_username = parsed_url.path.lstrip('/') if not parsed_url.scheme else channel_identifier

        try:
            chat = await user.get_chat(channel_username)
            channel_name = chat.title
        except Exception:
            await message.reply_text("<b>Hey Bro! 🥲 Incorrect username ❌</b>")
            return

        temporary_msg = await message.reply_text("<b>Scraping in progress wait.....</b>")
        scrapped_results = await scrape_messages(user, chat.id, limit, start_number)
        unique_messages, duplicates_removed = remove_duplicates(scrapped_results)

        if unique_messages:
            file_name = f"x{len(unique_messages)}_{channel_name.replace(' ', '_')}.txt"
            with open(file_name, 'w') as f:
                f.write("\n".join(unique_messages))
            with open(file_name, 'rb') as f:
                if message.chat.type in ["group", "supergroup"]:
                    if message.from_user is None:
                        user_link = '<a href="https://t.me/ItsSmartToolBot">Smart Tool ⚙️</a>'
                    else:
                        user_first_name = message.from_user.first_name
                        user_last_name = message.from_user.last_name if message.from_user.last_name else ""
                        user_full_name = f"{user_first_name} {user_last_name}".strip()
                        user_link = f'<a href="tg://user?id={message.from_user.id}">{user_full_name}</a>'
                else:
                    if message.from_user is None:
                        user_link = '<a href="https://t.me/ItsSmartToolBot">Smart Tool ⚙️</a>'
                    else:
                        user_first_name = message.from_user.first_name
                        user_last_name = message.from_user.last_name if message.from_user.last_name else ""
                        user_full_name = f"{user_first_name} {user_last_name}".strip()
                        user_link = f'<a href="tg://user?id={message.from_user.id}">{user_full_name}</a>'

                caption = (
                    f"<b>CC Scrapped Successful ✅</b>\n"
                    f"<b>━━━━━━━━━━━━━━━━</b>\n"
                    f"<b>Source:</b> <code>{channel_name}</code>\n"
                    f"<b>Amount:</b> <code>{len(unique_messages)}</code>\n"
                    f"<b>Duplicates Removed:</b> <code>{duplicates_removed}</code>\n"
                    f"<b>━━━━━━━━━━━━━━━━</b>\n"
                    f"<b>Card-Scrapper By: {user_link}</b>\n"
                )
                await temporary_msg.delete()
                await client.send_document(message.chat.id, f, caption=caption)
            os.remove(file_name)
        else:
            await temporary_msg.delete()
            await client.send_message(message.chat.id, "<b>Sorry Bro ❌ No Credit Card Found</b>")



# Ensure the user client is started
user.start()
