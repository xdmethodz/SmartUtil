import re
import os
from pyrogram import Client, filters, handlers
from pyrogram.enums import ParseMode
from pyrogram.types import Message

def filter_bin(content, bin_number):
    """Filter lines containing the specified BIN."""
    filtered_lines = [line for line in content if line.startswith(bin_number)]
    return filtered_lines

def remove_bin(content, bin_number):
    """Remove lines containing the specified BIN."""
    filtered_lines = [line for line in content if not line.startswith(bin_number)]
    return filtered_lines

async def process_file(file_path, bin_number, command):
    """Process the file to either filter or remove lines based on the command."""
    with open(file_path, 'r') as file:
        content = file.readlines()

    if command == '/adbin':
        matched_cards = filter_bin(content, bin_number)
        unmatched_cards = remove_bin(content, bin_number)
    elif command == '/rmbin':
        matched_cards = remove_bin(content, bin_number)
        unmatched_cards = filter_bin(content, bin_number)

    return matched_cards, unmatched_cards

async def handle_bin_commands(client, message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply_text("<b>⚠️ Please provide a valid BIN number.</b>")
        return

    command = args[0]
    bin_number = args[1]
    if not re.match(r'^\d{6}$', bin_number):
        await message.reply_text("<b>⚠️ BIN number must be 6 digits.</b>")
        return

    if not message.reply_to_message.document or not message.reply_to_message.document.file_name.endswith('.txt'):
        await message.reply_text("<b>⚠️ Please reply to a valid .txt file.</b>")
        return

    file_path = await message.reply_to_message.download()
    matched_cards, unmatched_cards = await process_file(file_path, bin_number, command)
    
    if not matched_cards:
        await message.reply_text(f"<b>No credit card details found with BIN {bin_number}.</b>")
        os.remove(file_path)
        return

    # Create the response message
    user_full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    user_profile_url = f"https://t.me/{message.from_user.username}" if message.from_user.username else None
    user_link = f'<a href="{user_profile_url}">{user_full_name}</a>' if user_profile_url else user_full_name
    
    filtered_cards = "\n".join(f"`{line.strip()}`" for line in matched_cards)
    remaining_cards = "\n".join(f"`{line.strip()}`" for line in unmatched_cards)
    response_message = (
        f"<b>Here are the filtered cards:</b>\n\n"
        f"{filtered_cards}\n\n"
        f"<b>Here are the remaining cards:</b>\n\n"
        f"{remaining_cards}\n\n"
        f"<b>Total Cards:</b> <code>{len(matched_cards) + len(unmatched_cards)}</code>\n"
        f"<b>Filter By:</b> {user_link}"
    )

    await message.reply_text(response_message, parse_mode=ParseMode.HTML)

    os.remove(file_path)

def setup_bin_handlers(app: Client):
    app.add_handler(handlers.MessageHandler(handle_bin_commands, filters.command(["adbin", "rmbin"])))
