import re
import os
import asyncio
import requests
from collections import Counter
from pyrogram import Client, filters, handlers
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

async def extrapolate_cc(bin_number, amount=5):
    """Generate extrapolated credit card data using a BIN."""
    extrapolated_ccs = [f"{bin_number}{str(i).zfill(10)}xxxxxxxx" for i in range(amount)]
    return extrapolated_ccs

async def fetch_bin_info(bin_number):
    """Fetch BIN information from the API."""
    url = f"https://data.handyapi.com/bin/{bin_number}"
    headers = {'Referer': 'your-domain'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

async def filter_valid_cc(content):
    """Filter valid credit card details from the file content."""
    valid_cc_pattern = re.compile(r'^\d{16}\|\d{2}\|\d{4}\|\d{3}$')
    valid_ccs = [line.strip() for line in content if valid_cc_pattern.match(line.strip())]
    return valid_ccs

async def handle_extrapolate_command(client, message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply_text("<b>⚠️ Please provide a BIN.</b>", parse_mode=ParseMode.HTML)
        return

    bin_number = args[1]
    if not re.match(r'^\d{6}$', bin_number):
        await message.reply_text("<b>⚠️ BIN number must be 6 digits.</b>", parse_mode=ParseMode.HTML)
        return

    # Send a temporary message indicating extrapolation in progress
    temp_msg = await message.reply_text("<b>Extrapolating In Progress.....</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(1)
    await temp_msg.delete()

    # Extrapolate CC data and fetch BIN info
    extrapolated_ccs = await extrapolate_cc(bin_number)
    bin_info = await fetch_bin_info(bin_number)

    if bin_info:
        bank = bin_info.get("Issuer", "Unknown Bank")
        country = bin_info.get("Country", {}).get("Name", "Unknown Country")
        card_info = f"{bin_info.get('Scheme', 'Unknown')} - {bin_info.get('Type', 'Unknown')} - {bin_info.get('CardTier', 'Unknown')}"
    else:
        bank = "Unknown Bank"
        country = "Unknown Country"
        card_info = "Unknown"

    # Create the response message
    formatted_ccs = "\n".join(extrapolated_ccs)
    response_message = (
        f"<b>𝗘𝘅𝘁𝗿𝗮𝗽 ⇾ {bin_number}</b>\n"
        f"<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 5</b>\n\n"
        f"```\n{formatted_ccs}\n```\n\n"
        f"<b>𝗕𝗮𝗻𝗸:</b> {bank}\n"
        f"<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> {country}\n"
        f"<b>𝗕𝗜𝗡 𝗜𝗻𝗳𝗼:</b> {card_info}"
    )

    # Send the response message with a regenerate button
    regenerate_button = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Regenerate", callback_data=f"regenerate_{bin_number}")]
        ]
    )
    await message.reply_text(response_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=regenerate_button)

async def handle_fcc_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document or not message.reply_to_message.document.file_name.endswith('.txt'):
        await message.reply_text("<b>⚠️ Reply to a message or provide text to filter CC.</b>", parse_mode=ParseMode.HTML)
        return

    # Send a temporary message indicating filtering in progress
    temp_msg = await message.reply_text("<b>Filtering CCS Please Wait....</b>", parse_mode=ParseMode.HTML)
    
    file_path = await message.reply_to_message.download()
    with open(file_path, 'r') as file:
        content = file.readlines()

    valid_ccs = await filter_valid_cc(content)
    
    if not valid_ccs:
        await temp_msg.delete()
        await message.reply_text("<b>No valid credit card details found in the file.</b>", parse_mode=ParseMode.HTML)
        os.remove(file_path)
        return

    # Create the response message
    user_full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    user_profile_url = f"https://t.me/{message.from_user.username}" if message.from_user.username else None
    user_link = f'<a href="{user_profile_url}">{user_full_name}</a>' if user_profile_url else user_full_name
    
    formatted_ccs = "\n".join(valid_ccs)
    response_message = (
        f"<b>Total cards found: {len(valid_ccs)}</b>\n\n"
        f"```\n{formatted_ccs}\n```\n\n"
        f"<b>Filter By:</b> {user_link}"
    )

    await temp_msg.delete()
    await message.reply_text(response_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    os.remove(file_path)

async def handle_topbin_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document or not message.reply_to_message.document.file_name.endswith('.txt'):
        await message.reply_text("<b>⚠️ Please reply to a text file contains credit cards to check top bins.</b>", parse_mode=ParseMode.HTML)
        return

    # Send a temporary message indicating finding top bins in progress
    temp_msg = await message.reply_text("<b>Finding Top Bins...</b>", parse_mode=ParseMode.HTML)
    
    file_path = await message.reply_to_message.download()
    with open(file_path, 'r') as file:
        content = file.readlines()

    bin_counter = Counter([line.strip()[:6] for line in content])
    top_bins = bin_counter.most_common(20)

    if not top_bins:
        await temp_msg.delete()
        await message.reply_text("<b>No BIN data found in the file.</b>", parse_mode=ParseMode.HTML)
        os.remove(file_path)
        return

    # Create the response message
    response_message = "<b>Here are top 20 bins:</b>\n━━━━━━━━━━━━━━━━\n"
    for i, (bin, count) in enumerate(top_bins, 1):
        response_message += f"{i:02d}. BIN: `{bin}` - Count: `{count}`\n"

    await temp_msg.delete()
    await message.reply_text(response_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    os.remove(file_path)

async def handle_callback_query(client, callback_query):
    data = callback_query.data
    if data.startswith("regenerate_"):
        bin_number = data.split("_")[1]
        extrapolated_ccs = await extrapolate_cc(bin_number)
        bin_info = await fetch_bin_info(bin_number)

        if bin_info:
            bank = bin_info.get("Issuer", "Unknown Bank")
            country = bin_info.get("Country", {}).get("Name", "Unknown Country")
            card_info = f"{bin_info.get('Scheme', 'Unknown')} - {bin_info.get('Type', 'Unknown')} - {bin_info.get('CardTier', 'Unknown')}"
        else:
            bank = "Unknown Bank"
            country = "Unknown Country"
            card_info = "Unknown"

        # Create the response message
        formatted_ccs = "\n".join(extrapolated_ccs)
        response_message = (
            f"<b>𝗘𝘅𝘁𝗿𝗮𝗽 ⇾ {bin_number}</b>\n"
            f"<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 5</b>\n\n"
            f"```\n{formatted_ccs}\n```\n\n"
            f"<b>𝗕𝗮𝗻𝗸:</b> {bank}\n"
            f"<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> {country}\n"
            f"<b>𝗕𝗜𝗡 𝗜𝗻𝗳𝗼:</b> {card_info}"
        )

        # Only edit the message if the new response is different
        if response_message != callback_query.message.text:
            await callback_query.message.edit_text(response_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=callback_query.message.reply_markup)

def setup_filter_handlers(app: Client):
    app.add_handler(handlers.MessageHandler(handle_extrapolate_command, filters.command(["extp"])))
    app.add_handler(handlers.MessageHandler(handle_fcc_command, filters.command(["fcc"])))
    app.add_handler(handlers.MessageHandler(handle_topbin_command, filters.command(["topbin"])))
    app.add_handler(handlers.CallbackQueryHandler(handle_callback_query))
