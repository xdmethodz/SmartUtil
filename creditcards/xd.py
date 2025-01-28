from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random

API_URL = "https://data.handyapi.com/bin/"
HEADERS = {'Referer': 'your-domain'}

# Helper Functions
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


def generate_credit_card(bin_prefix, count=5):
    cards = []
    while len(cards) < count:
        card = bin_prefix + "".join([str(random.randint(0, 9)) for _ in range(10)])
        for i in range(10):
            temp_card = card[:-1] + str(i)
            if is_valid_card(temp_card):
                cards.append(temp_card)
                break
    return cards


def get_bin_info(bin_prefix):
    """
    Fetch BIN information from the API with headers.
    """
    response = requests.get(f"{API_URL}{bin_prefix}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None


# Command Handlers
async def check_bin(client: Client, message: Message):
    bins = []
    if message.reply_to_message:
        if message.reply_to_message.document:
            file_path = await message.reply_to_message.download()
            with open(file_path, 'r') as file:
                bins = file.read().split()
        elif message.reply_to_message.text:
            bins = message.reply_to_message.text.split()
    else:
        bins = message.text.split()[1:]

    bins = bins[:20]
    if not bins:
        await message.reply_text("Please provide BINs to check.")
        return

    fetching_message = await message.reply_text(
        "<b>FETCHING ALL BIN DETAILS FROM DATABASE PLEASE WAIT ⚡️</b>", 
        parse_mode=ParseMode.HTML
    )

    bin_details = []
    for bin_prefix in bins:
        data = get_bin_info(bin_prefix)
        if data:
            bin_info = (
                f"• BIN: {data.get('bin')}\n"
                f"• INFO: {data.get('info')}\n"
                f"• BANK: {data.get('bank')}\n"
                f"• COUNTRY: {data.get('country')} {data.get('country_code')}\n"
            )
            bin_details.append(bin_info)
        else:
            bin_details.append(f"• BIN: {bin_prefix}\n• INFO: Not Found\n")

    await fetching_message.delete()
    result_message = "🔍 BIN Details 📋\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(bin_details)
    await message.reply_text(result_message, parse_mode=ParseMode.HTML)


async def extrapolate_bin(client: Client, message: Message):
    bins = message.text.split()[1:]

    if not bins:
        await message.reply_text("Please provide a BIN for extrapolation.")
        return

    bin_prefix = bins[0]
    data = get_bin_info(bin_prefix)
    if not data:
        await message.reply_text("Error fetching BIN details.")
        return

    bank = data.get('bank', 'Unknown')
    country = data.get('country', 'Unknown')
    country_code = data.get('country_code', '')
    info = data.get('info', 'Unknown')

    cards = generate_credit_card(bin_prefix)

    cards_info = "\n".join([f"• {card}" for card in cards])
    response_message = (
        f"𝗘𝘅𝘁𝗿𝗮𝗽 ⇾ {bin_prefix}\n"
        f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {len(cards)}\n\n"
        f"{cards_info}\n\n"
        f"𝗕𝗮𝗻𝗸: {bank}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {country_code}\n"
        f"𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {info}\n"
    )

    await message.reply_text(
        response_message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Regenerate", callback_data=f"regenerate_{bin_prefix}")]]
        )
    )


# Setup Function for Handlers
def setup_xd_handlers(app: Client):
    app.add_handler(MessageHandler(check_bin, filters.command("mbin")), group=1)
    app.add_handler(MessageHandler(extrapolate_bin, filters.command("extp")), group=2)
