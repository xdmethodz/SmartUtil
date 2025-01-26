import re
import os
import asyncio
from pyrogram import Client, filters, handlers
from pyrogram.enums import ParseMode
from pyrogram.types import Message

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
        await message.reply_text("<b>⚠️ Reply to a message with a text file.</b>", parse_mode=ParseMode.HTML)
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

    if len(emails) > 10:
        file_name = "Smart_Tool_⚙️_Email_Results.txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(emails))
        user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        caption = (
            f"<b>Here are the extracted emails:</b>\n"
            f"<b>━━━━━━━━━━━━━━━━</b>\n"
            f"<b>Total Emails:</b> <code>{len(emails)}</code>\n"
            f"<b>━━━━━━━━━━━━━━━━</b>\n"
            f"<b>Filter By:</b> <a href='tg://user?id={message.from_user.id}'>{user_full_name}</a>\n"
        )
        await temp_msg.delete()
        await client.send_document(message.chat.id, file_name, caption=caption, parse_mode=ParseMode.HTML)
        os.remove(file_name)
    else:
        formatted_emails = '\n'.join(f'`{email}`' for email in emails)
        await temp_msg.delete()
        await message.reply_text(formatted_emails, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    os.remove(file_path)

# Command to handle filtering and extracting email:password pairs
async def handle_fpass_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document or not message.reply_to_message.document.file_name.endswith('.txt'):
        await message.reply_text("<b>⚠️ Reply to a message with a text file.</b>", parse_mode=ParseMode.HTML)
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

    if len(email_passes) > 10:
        file_name = "Smart_Tool_⚙️_Email_Pass_Results.txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(email_passes))
        user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        caption = (
            f"<b>Here are the extracted mail pass:</b>\n"
            f"<b>━━━━━━━━━━━━━━━━</b>\n"
            f"<b>Total Mail pass:</b> <code>{len(email_passes)}</code>\n"
            f"<b>━━━━━━━━━━━━━━━━</b>\n"
            f"<b>Filter By:</b> <a href='tg://user?id={message.from_user.id}'>{user_full_name}</a>\n"
        )
        await temp_msg.delete()
        await client.send_document(message.chat.id, file_name, caption=caption, parse_mode=ParseMode.HTML)
        os.remove(file_name)
    else:
        formatted_email_passes = '\n'.join(f'`{email_pass}`' for email_pass in email_passes)
        await temp_msg.delete()
        await message.reply_text(formatted_email_passes, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    os.remove(file_path)

# Setup handlers
def setup_mail_handlers(app: Client):
    app.add_handler(handlers.MessageHandler(handle_fmail_command, filters.command("fmail") & (filters.private | filters.group)))
    app.add_handler(handlers.MessageHandler(handle_fpass_command, filters.command("fpass") & (filters.private | filters.group)))
