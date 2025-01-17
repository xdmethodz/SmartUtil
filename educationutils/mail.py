import re
import os
import asyncio
from urllib.parse import urlparse
from pyrogram import Client, filters, handlers
from pyrogram.enums import ParseMode
from pyrogram.types import Message

mail_scr_queue = asyncio.Queue()

def filter_messages(message):
    if message is None:
        return []

    pattern = r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b:\S+)'
    matches = re.findall(pattern, message)

    return matches

async def collect_channel_data(user_client_mail, channel_identifier, amount):
    messages = []

    async for message in user_client_mail.search_messages(channel_identifier):
        matches = filter_messages(message.text)
        if matches:
            messages.extend(matches)

        if len(messages) >= amount:
            break

    if not messages:
        return [], "<b>No Email and Password Combinations were found</b>"

    filtered_messages = messages[:amount]

    return filtered_messages, None

async def process_mail_scr_queue(user_client_mail, bot):
    while True:
        task = await mail_scr_queue.get()
        message, channel_identifier, amount, progress_message = task
        
        filtered_messages, error_msg = await collect_channel_data(user_client_mail, channel_identifier, amount)

        if error_msg:
            await progress_message.delete()
            await bot.send_message(message.chat.id, error_msg, parse_mode=ParseMode.HTML)
            return

        if not filtered_messages:
            await progress_message.delete()
            await bot.send_message(message.chat.id, "<b>🥲 No email and password combinations were found.</b>", parse_mode=ParseMode.HTML)
            return
        
        await progress_message.delete()

        with open(f'{channel_identifier}_combos.txt', 'w', encoding='utf-8') as file:
            for combo in filtered_messages:
                try:
                    file.write(f"{combo}\n")
                except UnicodeEncodeError:
                    continue

        with open(f'{channel_identifier}_combos.txt', 'rb') as file:
            user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
            user_link = f"<a href='tg://user?id={message.from_user.id}'>{user_full_name}</a>"
            output_message = f"""<b>Mail Scrapped Successful ✅
━━━━━━━━━━━━━━━━━━
Source: <code>{channel_identifier}</code>
Mail Amount: {len(filtered_messages)}
━━━━━━━━━━━━━━━━━━
Mail Scrapped By: {user_link}</b>"""
            await bot.send_document(message.chat.id, file, caption=output_message, parse_mode=ParseMode.HTML)

        os.remove(f'{channel_identifier}_combos.txt')
        
        mail_scr_queue.task_done()

# Function to filter and fetch emails from file content
async def filter_emails(content):
    """Filter and fetch email addresses from the file content."""
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    emails = [line.strip() for line in content if email_pattern.search(line)]
    return emails

# Function to filter and fetch email:password pairs from file content
async def filter_email_pass(content):
    """Filter and fetch email:password pairs from the file content."""
    email_pass_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s]+')
    email_passes = [line.strip() for line in content if email_pass_pattern.search(line)]
    return email_passes

# Command to handle fetching and filtering emails
async def handle_fmail_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document or not message.reply_to_message.document.file_name.endswith('.txt'):
        await message.reply_text("<b>⚠️ Reply to a message or a text file.</b>", parse_mode=ParseMode.HTML)
        return

    # Temporary message
    temp_msg = await message.reply_text("<b>Fetching And Filtering Mails From File... This Message Will Be Deleted After filtering</b>", parse_mode=ParseMode.HTML)
    
    file_path = await message.reply_to_message.download()
    with open(file_path, 'r') as file:
        content = file.readlines()

    emails = await filter_emails(content)
    if not emails:
        await temp_msg.delete()
        await message.reply_text("<b>No valid emails found in the file.</b>", parse_mode=ParseMode.HTML)
        os.remove(file_path)
        return

    formatted_emails = '\n'.join(f'`{email}`' for email in emails)
    response_message = f"{formatted_emails}"

    await temp_msg.delete()
    await message.reply_text(response_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    os.remove(file_path)

# Command to handle filtering and extracting email:password pairs
async def handle_fpass_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document or not message.reply_to_message.document.file_name.endswith('.txt'):
        await message.reply_text("<b>⚠️ Reply to a message or a text file.</b>", parse_mode=ParseMode.HTML)
        return

    # Temporary message
    temp_msg = await message.reply_text("<b>Filtering And Extracting Mail Pass... This Message Will Be Deleted After fetching</b>", parse_mode=ParseMode.HTML)
    
    file_path = await message.reply_to_message.download()
    with open(file_path, 'r') as file:
        content = file.readlines()

    email_passes = await filter_email_pass(content)
    if not email_passes:
        await temp_msg.delete()
        await message.reply_text("<b>No valid email:password pairs found in the file.</b>", parse_mode=ParseMode.HTML)
        os.remove(file_path)
        return

    formatted_email_passes = '\n'.join(f'`{email_pass}`' for email_pass in email_passes)
    response_message = f"{formatted_email_passes}"

    await temp_msg.delete()
    await message.reply_text(response_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    os.remove(file_path)

# Command to handle scraping email:password pairs from a channel
async def handle_mailscr_command(client, message: Message):
    greni = message.text.split()
    if len(greni) < 3:
        await message.reply_text("<b>❌ Please provide a channel with amount</b>", parse_mode=ParseMode.HTML)
        return

    channel_identifier = greni[1]
    amount = int(greni[2])

    parsed_url = urlparse(channel_identifier)
    if parsed_url.scheme and parsed_url.netloc:
        if parsed_url.path.startswith('/+'):
            try:
                chat = await client.join_chat(channel_identifier)
                channel_identifier = chat.id
            except Exception as e:
                if "USER_ALREADY_PARTICIPANT" in str(e):
                    try:
                        chat = await client.get_chat(channel_identifier)
                        channel_identifier = chat.id
                    except Exception as e:
                        await message.reply(f"<b>❌ Error joining this chat {channel_identifier}</b>", parse_mode=ParseMode.HTML)
                        return
                else:
                    await message.reply(f"<b>❌ Error in channel string {channel_identifier}</b>", parse_mode=ParseMode.HTML)
                    return
        else:
            channel_identifier = parsed_url.path.lstrip('/')
    else:
        channel_identifier = channel_identifier

    try:
        await client.get_chat(channel_identifier)
    except Exception as e:
        await message.reply(f"<b>❌Please make sure the provided username is valid: {channel_identifier}</b>", parse_mode=ParseMode.HTML)
        return

    progress_message = await message.reply("<b>Request Processing Wait....</b>", parse_mode=ParseMode.HTML)
    
    await mail_scr_queue.put((message, channel_identifier, amount, progress_message))

async def on_startup(client):
    await client.start()
    asyncio.create_task(process_mail_scr_queue(client, client))

# Setup handlers
def setup_mail_handlers(app: Client):
    app.add_handler(handlers.MessageHandler(handle_fmail_command, filters.command("fmail")))
    app.add_handler(handlers.MessageHandler(handle_fpass_command, filters.command("fpass")))
    app.add_handler(handlers.MessageHandler(handle_mailscr_command, filters.command("mailscr")))
