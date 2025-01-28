import re
import os
import random
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

def get_bin_info(bin):
    headers = {'Referer': 'your-domain'}
    response = requests.get(f"https://data.handyapi.com/bin/{bin}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def luhn_algorithm(card_number):
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def generate_luhn_compliant_card(bin):
    card = bin + ''.join([str(random.randint(0, 9)) for _ in range(15 - len(bin))])
    for check_digit in range(10):
        if luhn_algorithm(card + str(check_digit)):
            return card + str(check_digit)
    return None

def generate_credit_card(bin, amount, month=None, year=None):
    cards = []
    for _ in range(amount):
        card = generate_luhn_compliant_card(bin)
        if not card:
            continue
        card_month = month or f"{random.randint(1, 12):02}"
        card_year = year or random.randint(2024, 2029)
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append(f"{card}|{card_month}|{card_year}|{cvv}")
    return cards

def parse_input(user_input):
    bin = None
    month = None
    year = None
    amount = 10

    match = re.match(r"(\d{6,12})(x{4})?\|?(\d{2})?\|?(\d{2,4})?\s*(\d+)?", user_input)
    if match:
        bin, suffix, month, year, amount = match.groups()
        if suffix:
            bin += suffix
        year = f"20{year}" if year and len(year) == 2 else year
        amount = int(amount) if amount else 10

    return bin, month, year, amount

def generate_custom_cards(bin, amount, month, year):
    cards = []
    for _ in range(amount):
        card = ''.join([str(random.randint(0, 9)) if c in 'xX' else c for c in bin])
        if not luhn_algorithm(card):
            continue
        card_month = month or f"{random.randint(1, 12):02}"
        card_year = year or random.randint(2024, 2029)
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append(f"{card}|{card_month}|{card_year}|{cvv}")
    return cards

def setup_credit_handlers(app: Client):
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
            await message.reply_text("**Invalid BIN provided ❌**")
            return

        bank = bin_info.get("Issuer")
        country_name = bin_info["Country"].get("Name", "Unknown")
        card_type = bin_info.get("Type", "Unknown")
        card_scheme = bin_info.get("Scheme", "Unknown")
        bank_text = bank.upper() if bank else "Unknown"
        bin_info_text = f"**Bank:** `{bank_text}`\n**Country:** `{country_name}`\n**BIN Info:** `{card_scheme.upper()} - {card_type.upper()}`"

        # Notify user that the bot is generating cards
        progress_message = await message.reply_text("**Generating Credit Cards...☑️**")

        # Generate credit cards
        if 'x' in bin.lower():
            cards = generate_custom_cards(bin, amount, month, year)
        else:
            cards = generate_credit_card(bin, amount, month, year)

        if amount <= 10:
            card_text = "\n".join([f"`{card}`" for card in cards])
            await progress_message.delete()
            response_text = f"**BIN ⇾ {bin}**\n**Amount ⇾ {amount}**\n\n{card_text}\n\n{bin_info_text}"
            callback_data = f"regenerate|{user_input}|{amount}"

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
                caption = (
                    f"{amount} {card_scheme.upper()} {card_type.upper()} credit card numbers for BIN {bin}\n"
                    f"━━━━━━━━━━━━━━━━━━\n{bin_info_text}\n━━━━━━━━━━━━━━━━━━"
                )

                await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply_text(f"**Failed to save or send document: {str(e)}**")
            finally:
                if os.path.exists(file_name):
                    os.remove(file_name)

    return app

# To use the handler, call setup_credit_handlers(app) in your main script
