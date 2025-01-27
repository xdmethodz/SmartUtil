import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from asyncio import sleep
import pycountry
from faker import Faker

# Initialize Faker
fake = Faker()

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

# Dictionary of phone number formats by country code
phone_formats = {
    "AF": "+93 70XXXXXXX",
    "AL": "+355 67XXXXXXX",
    "DZ": "+213 55XXXXXXX",
    "AR": "+54 911XXXXXXXX",
    "AU": "+61 41XXXXXXX",
    "AT": "+43 650XXXXXXX",
    "BD": "+88 17XXXXXXXX",
    "BE": "+32 49XXXXXXX",
    "BR": "+55 119XXXXXXXX",
    "CA": "+1 416XXXXXXX",
    "CN": "+86 13XXXXXXXXX",
    "CO": "+57 321XXXXXXX",
    "DK": "+45 20XXXXXX",
    "EG": "+20 100XXXXXXX",
    "FR": "+33 6XXXXXXXX",
    "DE": "+49 15XXXXXXXXX",
    "GR": "+30 69XXXXXXXX",
    "IN": "+91 91XXXXXXXX",
    "ID": "+62 81XXXXXXXXX",
    "IR": "+98 91XXXXXXXX",
    "IE": "+353 85XXXXXXX",
    "IL": "+972 50XXXXXXX",
    "IT": "+39 33XXXXXXXX",
    "JP": "+81 80XXXXXXXX",
    "KZ": "+7 70XXXXXXXX",
    "KE": "+254 71XXXXXXX",
    "MY": "+60 12XXXXXXXX",
    "MX": "+52 12XXXXXXXXX",
    "NP": "+977 98XXXXXXXX",
    "NL": "+31 6XXXXXXXX",
    "NZ": "+64 21XXXXXXX",
    "NG": "+234 70XXXXXXXX",
    "PK": "+92 3XXXXXXXXX",
    "PH": "+63 917XXXXXXX",
    "PL": "+48 51XXXXXXX",
    "PT": "+351 91XXXXXXX",
    "RU": "+7 91XXXXXXXX",
    "SA": "+966 50XXXXXXX",
    "SG": "+65 81XXXXXX",
    "ZA": "+27 72XXXXXXX",
    "KR": "+82 10XXXXXXXX",
    "ES": "+34 6XXXXXXXX",
    "LK": "+94 71XXXXXXX",
    "SE": "+46 70XXXXXXX",
    "CH": "+41 79XXXXXXX",
    "TH": "+66 81XXXXXXX",
    "TR": "+90 53XXXXXXXX",
    "UA": "+380 50XXXXXXX",
    "AE": "+971 50XXXXXXX",
    "GB": "+44 79XXXXXXXX",
    "US": "+1 202XXXXXXX",
    "VN": "+84 91XXXXXXX"
}

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
                "full_name": fake.name(),
                "gender": fake.random_element(elements=("Male", "Female")),
                "street": country_info["working_address"]["street"],
                "city": country_info["working_address"]["city"],
                "state": "N/A",
                "postal_code": country_info["working_address"]["postal_code"],
                "phone_number": generate_phone_number(country_info["phone_format"]),
                "country_name": country.name
            }

        else:
            # Fetch fake address from API for other countries
            locale = f"{country.alpha_2.lower()}_{country.alpha_2.upper()}"
            api_url = f"https://fakerapi.it/api/v2/addresses?_quantity=1&_locale={locale}&_country_code={country.alpha_2}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                await message.reply_text("**❌ Failed to fetch fake address. Try again later.**")
                return

            data = response.json()['data'][0]

            # Parse the API response correctly
            fake_address = {
                "full_name": fake.name(),
                "gender": fake.random_element(elements=("Male", "Female")),
                "street": data.get('street', 'N/A'),
                "city": data.get('city', 'N/A'),
                "state": "N/A",  # Assuming the API does not provide state
                "postal_code": data.get('zipcode', 'N/A'),
                "phone_number": generate_phone_number(phone_formats.get(country.alpha_2, "+XXXXXXXXXXX")),
                "country_name": data.get('country', 'N/A')
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
    phone_number = phone_format
    for _ in range(phone_number.count('X')):
        phone_number = phone_number.replace('X', str(fake.random_digit()), 1)
    return phone_number

# To use the handler, call setup_fake_handler(app) in your main script
