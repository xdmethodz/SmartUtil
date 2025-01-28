import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random

API_URL = "https://data.handyapi.com/bin/"


# Luhn algorithm to check if a card number is valid
def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def is_valid_card(card_number):
    return luhn_checksum(card_number) == 0


# Generate valid credit card numbers using the Luhn algorithm
def generate_credit_card(bin, count=5):
    cards = []
    while len(cards) < count:
        card = bin + "".join([str(random.randint(0, 9)) for _ in range(10)])  # 10 random digits for a 16-digit number
        for i in range(10):
            temp_card = card[:-1] + str(i)
            if is_valid_card(temp_card):
                cards.append(temp_card)
                break
    return cards


# Handler for checking BIN information
async def check_bin(client: Client, message: Message):
    bins = []
    if message.reply_to_message:
        if message.reply_to_message.document:
            # If the reply is to a document, download and read the file
            file_path = await message.reply_to_message.download()
            with open(file_path, 'r') as file:
                bins = file.read().split()
        elif message.reply_to_message.text:
            # If the reply is to a text message, split the text into BINs
            bins = message.reply_to_message.text.split()
    else:
        # If the command is used with direct input
        bins = message.text.split()[1:]

    bins = bins[:20]  # Limit to 20 BINs
    if not bins:
        await message.reply_text("Please provide BINs to check.")
        return

    fetching_message = await message.reply_text(
        "<b>FETCHING ALL BINS DETAILS FROM DATABASE PLEASE WAIT ⚡️</b>", parse_mode="html"
    )

    bin_details = []
    for bin in bins:
        response = requests.get(f"{API_URL}{bin}")
        if response.status_code == 200:
            data = response.json()
            bin_info = (
                f"• BIN: {data.get('bin')}\n"
                f"• INFO: {data.get('info')}\n"
                f"• BANK: {data.get('bank')}\n"
                f"• COUNTRY: {data.get('country')} {data.get('country_code')}\n"
            )
            bin_details.append(bin_info)
        else:
            bin_details.append(f"• BIN: {bin}\n• INFO: Not Found\n")

    await fetching_message.delete()
    result_message = "🔍 BIN Details 📋\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(bin_details)
    await message.reply_text(result_message, parse_mode="html")


# Handler for extrapolating BIN information
async def extrapolate_bin(client: Client, message: Message):
    bins = message.text.split()[1:]

    if not bins:
        await message.reply_text("Please provide a BIN for extrapolation.")
        return

    bin = bins[0]
    response = requests.get(f"{API_URL}{bin}")
    if response.status_code != 200:
        await message.reply_text("Error fetching BIN details.")
        return

    data = response.json()
    bank = data.get('bank', 'Unknown')
    country = data.get('country', 'Unknown')
    country_code = data.get('country_code', '')
    info = data.get('info', 'Unknown')

    cards = generate_credit_card(bin)

    cards_info = "\n".join([f"• {card}" for card in cards])
    response_message = (
        f"𝗘𝘅𝘁𝗿𝗮𝗽 ⇾ {bin}\n"
        f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {len(cards)}\n\n"
        f"{cards_info}\n\n"
        f"𝗕𝗮𝗻𝗸: {bank}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {country_code}\n"
        f"𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {info}\n"
    )

    await message.reply_text(
        response_message,
        parse_mode="html",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Regenerate", callback_data=f"regenerate_{bin}")]]
        )
    )


# Callback handler for regenerating card numbers
async def regenerate_cards(client: Client, message: Message):
    bin = message.text.split("_")[1]
    response = requests.get(f"{API_URL}{bin}")
    if response.status_code != 200:
        await message.reply_text("Error fetching BIN details.")
        return

    data = response.json()
    bank = data.get('bank', 'Unknown')
    country = data.get('country', 'Unknown')
    country_code = data.get('country_code', '')
    info = data.get('info', 'Unknown')

    cards = generate_credit_card(bin)

    cards_info = "\n".join([f"• {card}" for card in cards])
    response_message = (
        f"𝗘𝘅𝘁𝗿𝗮𝗽 ⇾ {bin}\n"
        f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {len(cards)}\n\n"
        f"{cards_info}\n\n"
        f"𝗕𝗮𝗻𝗸: {bank}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {country_code}\n"
        f"𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {info}\n"
    )

    await message.reply_text(
        response_message,
        parse_mode="html",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Regenerate", callback_data=f"regenerate_{bin}")]]
        )
    )


# Setup function to register all handlers
def setup_xd_handlers(app: Client):
    app.add_handler(filters.command("mbin") & filters.group | filters.private, check_bin)
    app.add_handler(filters.command("extp") & filters.group | filters.private, extrapolate_bin)
    app.add_handler(filters.regex("^regenerate_") & filters.group | filters.private, regenerate_cards)
