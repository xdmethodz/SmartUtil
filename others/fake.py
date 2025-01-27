import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from asyncio import sleep
import pycountry

# Keep only Algeria's information
countries_info = [
    {
        "name": "Algeria",
        "alpha_2": "DZ",
        "phone_format": "+213XXXXXXXXX",
        "cities": ["Algiers", "Oran", "Constantine"],
        "regions": ["Algiers Province", "Oran Province", "Constantine Province"],
        "postal_codes": ["16000", "25100", "25000"],
        "streets": ["Rue Didouche Mourad", "Rue Larbi Ben M'hidi", "Rue Hassiba Ben Bouali"],
        "working_address": {
            "street": "20 centre Culturel 99 Islamique",
            "city": "Chlef",
            "postal_code": "02000"
        }
    }
]

def get_country_info(alpha_2):
    for country in countries_info:
        if country["alpha_2"] == alpha_2:
            return country
    return None

def setup_fake_handler(app: Client):
    @app.on_message(filters.command(["fake", "rnd", ".fake", ".rnd"]) & (filters.private | filters.group))
    async def fake_handler(client: Client, message: Message):
        if len(message.command) <= 1:
            await message.reply_text("**❌ Provide a valid country name or country code.**")
            return
        
        country_code = message.command[1]
        country = pycountry.countries.get(alpha_2=country_code.upper()) or pycountry.countries.get(name=country_code.title())
        
        if not country:
            await message.reply_text("**❌ Provide a valid country name or country code.**")
            return

        # Check if the country is Algeria
        if country.alpha_2 == "DZ":
            country_info = get_country_info(country.alpha_2)
            if not country_info:
                await message.reply_text("**❌ Country details not available.**")
                return

            fake_address = {
                "full_name": "N/A",
                "gender": "N/A",
                "street": country_info["working_address"]["street"],
                "city": country_info["working_address"]["city"],
                "state": "N/A",
                "postal_code": country_info["working_address"]["postal_code"],
                "phone_number": generate_phone_number(country_info["phone_format"]),
                "country_name": country.name
            }

        else:
            # Fetch fake address from API for other countries
            api_url = f"https://fakerapi.it/api/v2/addresses?_quantity=1&_locale={country.alpha_2.lower()}_{country.alpha_2.upper()}&_country_code={country.alpha_2}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                await message.reply_text("**❌ Failed to fetch fake address. Try again later.**")
                return

            data = response.json()['data'][0]

            fake_address = {
                "full_name": data['firstname'] + " " + data['lastname'],
                "gender": data['gender'],
                "street": data['street'],
                "city": data['city'],
                "state": data['county'],
                "postal_code": data['zipcode'],
                "phone_number": data['phone'],
                "country_name": country.name
            }
        
        generating_message = await message.reply_text(f"**Generating Fake Address For {fake_address['country_name']}...**")
        await sleep(2)
        await generating_message.delete()
        
        await message.reply_text(f"""
**Address for {fake_address['country_name']}:**
━━━━━━━━━━━━━━━━━
**Full Name:** `{fake_address['full_name']}`
**Gender:** `{fake_address['gender']}`
**Street:** `{fake_address['street']}`
**City/Town/Village:** `{fake_address['city']}`
**State/Province/Region:** `{fake_address['state']}`
**Postal code:** `{fake_address['postal_code']}`
**Phone Number:** `{fake_address['phone_number']}`
**Country:** `{fake_address['country_name']}`
""", parse_mode=ParseMode.MARKDOWN)

def generate_phone_number(phone_format):
    """
    Generate a phone number based on the country phone format.
    """
    from faker import Faker
    fake = Faker()
    phone_number = phone_format
    for _ in range(phone_number.count('X')):
        phone_number = phone_number.replace('X', str(fake.random_digit()), 1)
    return phone_number

# To use the handler, call setup_fake_handler(app) in your main script
