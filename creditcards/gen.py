import requests
import random
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# Your Neutrino API credentials
USER_ID = "dicynukoke"
API_KEY = "OJHZ7JHQgNYmdS8C6BgNadavoywbHUdENHFOx3YTZctJb0DS"

def calculate_luhn(card_number: str):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    checksum = 0
    odd_even = len(digits) & 1
    for i, digit in enumerate(digits):
        if i & 1 ^ odd_even:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return (10 - (checksum % 10)) % 10

def generate_cc(bin: str, month: str, year: str, amount: int = 10):
    generated_cards = []
    for _ in range(amount):
        card_number = bin + ''.join([str(random.randint(0, 9)) for _ in range(16 - len(bin) - 1)])
        card_number += str(calculate_luhn(card_number))
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        generated_cards.append(f"{card_number}|{month}|{year}|{cvv}")
    return generated_cards

def check_bin(bin: str):
    url = 'https://neutrinoapi.net/bin-lookup'
    data = {
        'bin-number': bin,
        'customer-ip': ''
    }
    headers = {
        'User-ID': USER_ID,
        'API-Key': API_KEY
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

async def gen_handler(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 5:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return
        
        bin = args[1]
        month = args[2]
        year = args[3]
        amount = int(args[4]) if len(args) > 4 else 10

        if len(bin) < 6:
            await message.reply_text("**Provide a valid BIN at least 6 digits ❌**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return
        
        bin_info = check_bin(bin)
        if not bin_info or not bin_info.get('valid', False):
            await message.reply_text("**Invalid BIN provided ❌**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return

        processing_msg = await message.reply_text("**Generating Credit Cards...☑️**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        generated_cards = generate_cc(bin, month, year, amount)

        bank_name = bin_info.get('issuer', 'N/A')
        country = bin_info.get('country', 'N/A')
        card_type = bin_info.get('card-type', 'N/A')
        card_category = bin_info.get('category', 'N/A')
        card_brand = bin_info.get('brand', 'N/A')

        response = f"**𝗕𝗜𝗡 ⇾ {bin}**\n**𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {amount}**\n\n"
        response += "```\n" + "\n".join(generated_cards) + "\n```\n\n"
        response += f"**𝗕𝗮𝗻𝗸:** {bank_name}\n**𝗖𝗼𝘂𝗻𝘁𝗿𝘆:** {country}\n**𝗕𝗜𝗡 𝗜𝗻𝗳𝗼:** {card_category} - {card_type} - {card_brand}"

        if amount <= 10:
            await message.reply_text(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        else:
            filename = f"{bin} x {amount}.txt"
            with open(filename, 'w') as file:
                file.write("\n".join(generated_cards))

            user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
            user_profile_link = f"https://t.me/{message.from_user.username}"
            caption = (
                f"{amount} {card_type} credit card numbers for BIN {bin}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"**𝗕𝗮𝗻𝗸:** {bank_name}\n"
                f"**𝗖𝗼𝘂𝗻𝘁𝗿𝘆:** {country}\n"
                f"**𝗕𝗜𝗡 𝗜𝗻𝗳𝗼:** {card_category} - {card_type} - {card_brand}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"Generate By: [{user_full_name}]({user_profile_link})"
            )
            await message.reply_document(document=filename, caption=caption, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            os.remove(filename)

        await processing_msg.delete()
    except Exception as e:
        await message.reply_text(f"**Error:** {e}\nUsage: /gen [BIN] [MM] [YY] [Amount]", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def setup_card_handlers(app: Client):
    app.add_handler(filters.command("gen", prefixes=['/', '.']) & filters.private, gen_handler)

