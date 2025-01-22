import os
import re
import requests
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
def get_bin_info(bin):
    headers = {'Referer': 'your-domain'}
    response = requests.get(f"https://data.handyapi.com/bin/{bin}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def generate_credit_card(bin, amount):
    cards = []
    for _ in range(amount):
        card = bin + ''.join([str(random.randint(0, 9)) for _ in range(16-len(bin))])
        month = f"{random.randint(1, 12):02}"
        year = random.randint(2024, 2029)
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

def setup_mgen_handlers(app: Client):
    @app.on_message(filters.command(["bin"]))
    async def bin_handler(client: Client, message: Message):
        user_input = message.text.split(maxsplit=1)
        if len(user_input) == 1:
            await message.reply_text("**Provide a valid BIN (6 digits) ❌**")
            return
        
        bin = user_input[1][:6]
        if len(bin) < 6:
            await message.reply_text("**Provide a valid BIN (6 digits) ❌**")
            return

        # Notify user that the bot is fetching BIN details
        progress_message = await message.reply_text("**Fetching Bin Details...**")

        # Fetch BIN info
        bin_info = get_bin_info(bin)
        if not bin_info or bin_info.get("Status") != "SUCCESS":
            await progress_message.delete()
            await message.reply_text("**Invalid bin provided❌**")
            return

        bank = bin_info.get("Issuer", "Unknown")
        country_name = bin_info["Country"].get("Name", "Unknown")
        card_type = bin_info.get("Type", "Unknown")
        card_scheme = bin_info.get("Scheme", "Unknown")
        bin_details = (
            f"🔍 **BIN Details 📋**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"• BIN: `{bin}`\n"
            f"• INFO: **{card_type.upper()} - {card_scheme.upper()}**\n"
            f"• BANK: **{bank.upper()}**\n"
            f"• COUNTRY: **{country_name.upper()}** 🇺🇸\n"
        )

        await progress_message.delete()
        await message.reply_text(bin_details, parse_mode=ParseMode.MARKDOWN)

    @app.on_message(filters.command(["mgen"]))
    async def mgen_handler(client: Client, message: Message):
        user_input = message.text.split()[1:]
        if len(user_input) < 2:
            await message.reply_text("**Wrong args ❌**\nUse /mgen [bin1] [bin2] .. [amount]")
            return
        
        bins = user_input[:-1]
        amount = int(user_input[-1])
        total_cards_per_bin = amount
        total_cards = total_cards_per_bin * len(bins)
        
        cards = []
        for bin in bins:
            cards += generate_credit_card(bin[:6], total_cards_per_bin)

        file_name = "Smart Tool ⚙️ Multigen.txt"
        try:
            with open(file_name, "w") as file:
                file.write("\n".join(cards))

            user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
            user_link = f"[{user_full_name}](tg://user?id={message.from_user.id})"
            caption = (
                f"🔥 Generated {total_cards} credit card numbers from all BIN 🔥\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏦 BINS: " + " • ".join([f"`{bin[:6]}`" for bin in bins]) + "\n"
            )

            await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await message.reply_text(f"**Failed to save or send document: {str(e)}**")
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    return app
