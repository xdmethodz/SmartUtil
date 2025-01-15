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

def generate_credit_card(bin, month, year, amount):
    cards = []
    for _ in range(amount):
        card = bin + ''.join([str(random.randint(0, 9)) for _ in range(16-len(bin))])
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

def parse_input(user_input):
    bin = None
    month = f"{random.randint(1, 12):02}"
    year = random.randint(2024, 2029)
    amount = 10

    match = re.match(r"(\d{6,})(\d{0,10}[xX]{0,4})\|?(\d{2})?\|?(\d{2,4})?\s*(\d+)?", user_input)
    if match:
        bin, suffix, month, year, amount = match.groups()
        bin = bin + ''.join([str(random.randint(0, 9)) if x in 'xX' else x for x in suffix])
        year = f"20{year}" if year and len(year) == 2 else (year if year else random.randint(2024, 2029))
        amount = int(amount) if amount else 10
        
    return bin, month, year, amount

def setup_handlers(app: Client):
    @app.on_message(filters.command(["gen", ".gen"]))
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

    @app.on_callback_query(filters.regex(r"regenerate\|(\d{6,16})\|(\d{2})\|(\d{4})\|(\d+)"))
    async def regenerate_callback(client: Client, callback_query):
        _, bin, month, year, amount = callback_query.data.split('|')
        amount = int(amount)

        # Fetch BIN info again
        bin_info = get_bin_info(bin[:6])
        if not bin_info or bin_info.get("Status") != "SUCCESS":
            await callback_query.answer("BIN info retrieval failed!", show_alert=True)
            return

        bank = bin_info.get("Issuer", "Unknown")
        country_name = bin_info["Country"].get("Name", "Unknown")
        card_type = bin_info.get("Type", "Unknown")
        card_scheme = bin_info.get("Scheme", "Unknown")

        # Generate new credit cards
        cards = generate_credit_card(bin, month, year, amount)
        card_text = "\n".join([f"`{card}`" for card in cards])

        bin_info_text = f"**Bank:** `{bank}`\n**Country:** `{country_name}`\n**BIN Info:** `{card_scheme.upper()} - {card_type.upper()}`"
        response_text = f"**BIN ⇾ {bin}**\n**Amount ⇾ {amount}**\n\n{card_text}\n\n{bin_info_text}"

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Regenerate", callback_data=f"regenerate|{bin}|{month}|{year}|{amount}")]]
        )

        await callback_query.message.edit_text(response_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        await callback_query.answer("Generated new cards successfully!")

    return app

