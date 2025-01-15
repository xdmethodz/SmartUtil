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

def setup_handlers(app: Client):
    @app.on_message(filters.command(["gen", ".gen"]) & (filters.private | filters.group))
    async def generate_handler(client: Client, message: Message):
        user_input = message.text.split(maxsplit=1)
        if len(user_input) == 1:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**")
            return
        
        user_input = user_input[1]
        bin, month, year, amount = parse_input(user_input)

        if not bin or len(bin) < 6:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**")
            return

        # Fetch BIN info
        bin_info = get_bin_info(bin[:6])
        if not bin_info or bin_info.get("Status") != "SUCCESS":
            await message.reply_text("**Invalid BIN provided❌**")
            return

        bank = bin_info.get("Issuer", "Unknown")
        country_name = bin_info["Country"].get("Name", "Unknown")
        card_type = bin_info.get("Type", "Unknown")
        card_scheme = bin_info.get("Scheme", "Unknown")
        bin_info_text = f"**Bank:** `{bank}`\n**Country:** `{country_name}`\n**BIN Info:** `{card_scheme.upper()} - {card_type.upper()}`"

        # Notify user that the bot is generating cards
        progress_message = await message.reply_text("**Generating Credit Cards...☑️**")

        # Generate credit cards
        cards = generate_credit_card(bin, month, year, amount)
        card_text = "\n".join([f"`{card}`" for card in cards])

        if amount <= 10:
            await progress_message.delete()
            response_text = f"**BIN ⇾ {bin}**\n**Amount ⇾ {amount}**\n\n{card_text}\n\n{bin_info_text}"
            callback_data = f"regenerate|{bin}|{month}|{year}|{amount}"

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Regenerate", callback_data=callback_data)]]
            )
            await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        else:
            # Save cards to a file if amount is greater than 10
            file_name = f"{bin} x {amount}.txt"
            try:
                with open(file_name, "w") as file:
                    file.write("\n".join(cards))

                await progress_message.delete()
                user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
                user_link = f"[{user_full_name}](tg://user?id={message.from_user.id})"
                caption = f"{amount} {card_scheme.upper()} {card_type.upper()} credit card numbers for BIN {bin}\n━━━━━━━━━━━━━━━━━━\n{bin_info_text}\n━━━━━━━━━━━━━━━━━━\nGenerate By: {user_link}"

                await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply_text(f"**Failed to save or send document: {str(e)}**")
            finally:
                if os.path.exists(file_name):
                    os.remove(file_name)

    @app.on_message(filters.command(["bin", ".bin"]) & (filters.private | filters.group))
    async def bin_handler(client: Client, message: Message):
        user_input = message.text.split(maxsplit=1)
        if len(user_input) == 1:
            await message.reply_text("**Provide a valid BIN (6 digits)**")
            return

        user_input = user_input[1]
        bin = re.match(r"(\d{6,})", user_input)
        if not bin:
            await message.reply_text("**Provide a valid BIN (6 digits)**")
            return

        bin = bin.group(1)[:6]  # Extract the first 6 digits

        # Notify user about fetching BIN details
        progress_message = await message.reply_text("**Fetching BIN Details...**")

        # Fetch BIN info
        bin_info = get_bin_info(bin)
        if not bin_info or bin_info.get("Status") != "SUCCESS":
            await progress_message.delete()
            await message.reply_text("**Failed to retrieve BIN information. Please try again.**")
            return

        # Extract BIN details
        bank = bin_info.get("Issuer", "Unknown")
        country_name = bin_info["Country"].get("Name", "Unknown")
        country_emoji = bin_info["Country"].get("Emoji", "")
        card_type = bin_info.get("Type", "Unknown")
        card_scheme = bin_info.get("Scheme", "Unknown")

        # Prepare BIN details message
        response_text = (
            f"🔍 **BIN Details** 📋\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"• **BIN:** `{bin}`\n"
            f"• **INFO:** {card_scheme.upper()} - {card_type.upper()}\n"
            f"• **BANK:** {bank}\n"
            f"• **COUNTRY:** {country_name} {country_emoji}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        await progress_message.delete()
        await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)

    return app

