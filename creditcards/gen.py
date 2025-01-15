import os
import re
import requests
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode

def get_bin_info(bin):
    response = requests.get(f"https://data.handyapi.com/bin/{bin}")
    if response.status_code == 200:
        return response.json()
    return None

def generate_credit_card(bin, month, year, amount):
    cards = []
    for _ in range(amount):
        card = bin + ''.join([str(random.randint(0, 9)) for _ in range(12-len(bin))])
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

def setup_gen_handlers(app: Client):
    @app.on_message(filters.command(["gen", ".gen"]))
    async def generate_handler(client: Client, message: Message):
        user_input = message.text.split(maxsplit=1)
        if len(user_input) == 1:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**")
            return
        
        user_input = user_input[1]

        # Validate the input format
        match = re.match(r"(\d{6,})\|(\d{2})\|(\d{4})\s*(\d+)?", user_input)
        if not match:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**")
            return

        bin, month, year, amount = match.groups()
        amount = int(amount) if amount else 10

        if len(bin) < 6:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**")
            return

        # Fetch BIN info
        bin_info = get_bin_info(bin)
        if not bin_info:
            await message.reply_text("**Invalid bin provided❌**")
            return

        bank = bin_info.get("bank", "Unknown")
        country = bin_info.get("country", "Unknown")
        card_type = bin_info.get("type", "Unknown")
        card_brand = bin_info.get("brand", "Unknown")
        bin_info_text = f"**Bank:** {bank}\n**Country:** {country}\n**BIN Info:** {card_type.upper()} - {card_brand.upper()}"

        # Notify user that the bot is generating cards
        progress_message = await message.reply_text("**Generating Credit Cards...☑️**")

        # Generate credit cards
        cards = generate_credit_card(bin, month, year, amount)
        card_text = "\n".join([f"`{card}`" for card in cards])

        if amount <= 10:
            await progress_message.delete()
            response_text = f"**BIN ⇾ {bin}**\n**Amount ⇾ {amount}**\n\n{card_text}\n\n{bin_info_text}"
            await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
        else:
            # Save cards to a file if amount is greater than 10
            file_name = f"{bin} x {amount}.txt"
            with open(file_name, "w") as file:
                file.write("\n".join(cards))

            await progress_message.delete()
            user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
            user_link = f"[{user_full_name}](tg://user?id={message.from_user.id})"
            caption = f"{amount} {card_type.upper()} {card_brand.upper()} credit card numbers for BIN {bin}\n━━━━━━━━━━━━━━━━━━\n{bin_info_text}\n━━━━━━━━━━━━━━━━━━\nGenerate By: {user_link}"

            await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.MARKDOWN)
            os.remove(file_name)

    return app
