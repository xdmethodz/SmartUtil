import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

# Define the BIN databases for each country
bin_databases = {
    "Bangladesh": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BD Bin Database\n\n"
        "BIN: `400462`\n**Bank:** PUBALI BANK, LTD.\n**Country:** Bangladesh\n\n"
        "BIN: `400465`\n**Bank:** PUBALI BANK, LTD.\n**Country:** Bangladesh\n\n"
        "BIN: `400468`\n**Bank:** PUBALI BANK, LTD.\n**Country:** Bangladesh\n\n"
        "BIN: `400469`\n**Bank:** PUBALI BANK, LTD.\n**Country:** Bangladesh\n\n"
        "BIN: `400470`\n**Bank:** PUBALI BANK, LTD.\n**Country:** Bangladesh",
        "https://telegra.ph/Smart-Tool-01-17"
    ),
    "Algeria": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Algeria Bin Database\n\n"
        "BIN: `400622`\n**Bank:** BANQUE EXTERIEURE D'ALGERIE\n**Country:** Algeria\n\n"
        "BIN: `400946`\n**Bank:** SOCIETE GENERALE ALGERIE\n**Country:** Algeria\n\n"
        "BIN: `405060`\n**Bank:** SOCIETE GENERALE ALGERIE\n**Country:** Algeria\n\n"
        "BIN: `417203`\n**Bank:** CREDIT POPULAIRE D'ALGERIE\n**Country:** Algeria\n\n"
        "BIN: `417217`\n**Bank:** CREDIT POPULAIRE D'ALGERIE\n**Country:** Algeria\n\n"
        "BIN: `417231`\n**Bank:** CREDIT POPULAIRE D'ALGERIE\n**Country:** Algeria",
        "https://telegra.ph/Smart-Tool-01-17-2"
    ),
    "India": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "India Bin Database\n\n"
        "BIN: `400016`\n**Bank:** STATE BANK OF INDIA\n**Country:** India\n\n"
        "BIN: `400017`\n**Bank:** STATE BANK OF INDIA\n**Country:** India\n\n"
        "BIN: `400018`\n**Bank:** STATE BANK OF INDIA\n**Country:** India\n\n"
        "BIN: `400019`\n**Bank:** STATE BANK OF INDIA\n**Country:** India\n\n"
        "BIN: `400032`\n**Bank:** STATE BANK OF INDIA\n**Country:** India",
        "https://telegra.ph/Smart-Tool-01-17-3"
    ),
    "China": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "China Bin Database\n\n"
        "BIN: `400201`\n**Bank:** YUANTA COMMERCIAL BANK CO., LTD.\n**Country:** Taiwan\n\n"
        "BIN: `400211`\n**Bank:** YUANTA COMMERCIAL BANK CO., LTD.\n**Country:** Taiwan\n\n"
        "BIN: `400212`\n**Bank:** CITIBANK, N.A.\n**Country:** China\n\n"
        "BIN: `400221`\n**Bank:** BANK OF CHINA\n**Country:** China\n\n"
        "BIN: `400292`\n**Bank:** BANK OF CHINA\n**Country:** China\n\n"
        "BIN: `400353`\n**Bank:** MEGA INTERNATIONAL COMMERCIAL BANK CO., LTD.\n**Country:** Taiwan",
        "https://telegra.ph/Smart-Tool-01-17-4"
    ),
    "Brazil": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Brazil Bin Database\n\n"
        "BIN: `400102`\n**Bank:** BANCO DO BRASIL, S.A.\n**Country:** Brazil\n\n"
        "BIN: `400106`\n**Bank:** BANCO DO BRASIL, S.A.\n**Country:** Brazil\n\n"
        "BIN: `400107`\n**Bank:** BANCO DO BRASIL, S.A.\n**Country:** Brazil\n\n"
        "BIN: `400130`\n**Bank:** BANCO DO BRASIL, S.A.\n**Country:** Brazil\n\n"
        "BIN: `400136`\n**Bank:** BANCO DO BRASIL, S.A.\n**Country:** Brazil",
        "https://telegra.ph/Smart-Tool-01-17-5"
    ),
    "Argentina": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Argentina Bin Database\n\n"
        "BIN: `400103`\n**Bank:** VISA ARGENTINA, S.A.\n**Country:** Argentina\n\n"
        "BIN: `400104`\n**Bank:** VISA ARGENTINA, S.A.\n**Country:** Argentina\n\n"
        "BIN: `400276`\n**Bank:** VISA ARGENTINA, S.A.\n**Country:** Argentina\n\n"
        "BIN: `400440`\n**Bank:** CAJA POPULAR DE AHORROS DE LA PROVINCIA DE TUCUMAN\n**Country:** Argentina\n\n"
        "BIN: `400448`\n**Bank:** CITIBANK\n**Country:** Argentina",
        "https://telegra.ph/Smart-Tool-01-17-6"
    ),
    "Japan": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Japan Bin Database\n\n"
        "BIN: `400142`\n**Bank:** SONY BANK, INC.\n**Country:** Japan\n\n"
        "BIN: `400673`\n**Bank:** MUFG BANK, LTD\n**Country:** Japan\n\n"
        "BIN: `401924`\n**Bank:** VANDLE CARD\n**Country:** Japan\n\n"
        "BIN: `402854`\n**Bank:** CITI CARDS JAPAN, INC.\n**Country:** Japan\n\n"
        "BIN: `405283`\n**Bank:** INTERPAYMENT SERVICES, LTD.\n**Country:** Japan",
        "https://telegra.ph/Smart-Tool-01-17-7"
    ),
    "Mexico": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Mexico Bin Database\n\n"
        "BIN: `400443`\n**Bank:** BANCO INBURSA S.A. INSTITUCION DE BANCA MULTIPLE GRUPO FINANCIERO INBURSA\n**Country:** Mexico\n\n"
        "BIN: `400523`\n**Bank:** BANCO AUTOFIN MEXICO, S.A.\n**Country:** Mexico\n\n"
        "BIN: `400819`\n**Bank:** BANCOPPEL S.A. INSTITUCION DE BANCA MULTIPLE\n**Country:** Mexico\n\n"
        "BIN: `400829`\n**Bank:** BANCA MIFEL, S.A.\n**Country:** Mexico\n\n"
        "BIN: `400994`\n**Bank:** BANCO NACIONAL DE MEXICO, S.A.\n**Country:** Mexico",
        "https://telegra.ph/Smart-Tool-01-17-8"
    ),
    "United States": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400002`\n**Bank:** RIVER VALLEY C.U.\n**Country:** United States\n\n"
        "BIN: `400009`\n**Bank:** UNIVERSITY FIRST F.C.U.\n**Country:** United States\n\n"
        "BIN: `400010`\n**Bank:** UNIVERSITY FIRST F.C.U.\n**Country:** United States\n\n"
        "BIN: `400011`\n**Bank:** UNIVERSITY FIRST F.C.U.\n**Country:** United States\n\n"
        "BIN: `400012`\n**Bank:** BANK OF AMERICA, NATIONAL ASSOCIATION\n**Country:** United States\n\n"
        "BIN: `400022`\n**Bank:** NAVY F.C.U.\n**Country:** United States\n\n"
        "BIN: `400023`\n**Bank:** NAVY F.C.U.\n**Country:** United States\n\n"
        "BIN: `400024`\n**Bank:** JUSTICE F.C.U.\n**Country:** United States\n\n"
        "BIN: `400028`\n**Bank:** KEESLER F.C.U.\n**Country:** United States\n\n"
        "BIN: `400041`\n**Bank:** BBVA USA\n**Country:** United States"
    ),
    "United Kingdom": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400626`\n**Bank:** HABIB ALLIED INTERNATIONAL BANK PLC\n**Country:** United Kingdom\n\n"
        "BIN: `400837`\n**Bank:** RAPHAELS BANK\n**Country:** United Kingdom\n\n"
        "BIN: `400838`\n**Bank:** RAPHAELS BANK\n**Country:** United Kingdom\n\n"
        "BIN: `400839`\n**Bank:** TRAVELEX (R.RAPHAEL & SONS PLC)\n**Country:** United Kingdom\n\n"
        "BIN: `400846`\n**Bank:** LLOYDS BANK PLC\n**Country:** United Kingdom\n\n"
        "BIN: `400860`\n**Bank:** HALIFAX\n**Country:** United Kingdom\n\n"
        "BIN: `400880`\n**Bank:** THE ROYAL BANK OF SCOTLAND PLC\n**Country:** United Kingdom\n\n"
        "BIN: `401039`\n**Bank:** HSBC BANK PLC\n**Country:** United Kingdom\n\n"
        "BIN: `401040`\n**Bank:** HSBC BANK PLC\n**Country:** United Kingdom\n\n"
        "BIN: `401064`\n**Bank:** LLOYDS BANK PLC\n**Country:** United Kingdom"
    ),
    "Spain": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400293`\n**Bank:** BANKINTER, S.A.\n**Country:** Spain\n\n"
        "BIN: `400740`\n**Bank:** CAIXABANK, S.A.\n**Country:** Spain\n\n"
        "BIN: `400741`\n**Bank:** CAIXABANK, S.A.\n**Country:** Spain\n\n"
        "BIN: `400882`\n**Bank:** BANKINTER, S.A.\n**Country:** Spain\n\n"
        "BIN: `400884`\n**Bank:** CAIXABANK S.A.\n**Country:** Spain\n\n"
        "BIN: `400885`\n**Bank:** BANCO BILBAO VIZCAYA ARGENTARIA S.A.\n**Country:** Spain\n\n"
        "BIN: `400921`\n**Bank:** ABANCA CORPORACION BANCARIA, S.A.\n**Country:** Spain\n\n"
        "BIN: `401021`\n**Bank:** CAIXABANK\n**Country:** Spain\n\n"
        "BIN: `401727`\n**Bank:** CAIXABANK, S.A.\n**Country:** Spain\n\n"
        "BIN: `401728`\n**Bank:** DEUTSCHE BANK\n**Country:** Spain"
    ),
    "Russia": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400079`\n**Bank:** JOINT STOCK COMMERCIAL BANK AK BARS\n**Country:** Russia\n\n"
        "BIN: `400171`\n**Bank:** JOINT-STOCK BANK ROSEVROBANK\n**Country:** Russia\n\n"
        "BIN: `400244`\n**Bank:** PUBLIC JOINT STOCK COMPANY BANK URALSIB\n**Country:** Russia\n\n"
        "BIN: `400628`\n**Bank:** EVROFINANCE MOSNARBANK\n**Country:** Russia\n\n"
        "BIN: `400648`\n**Bank:** CB CENTER-INVEST\n**Country:** Russia\n\n"
        "BIN: `400680`\n**Bank:** SBERBANK OF RUSSIA\n**Country:** Russia\n\n"
        "BIN: `400758`\n**Bank:** CREDIT UNION PAYMENT CENTER (LIMITED LIABILITY COMPANY)\n**Country:** Russia\n\n"
        "BIN: `400763`\n**Bank:** CREDIT UNION PAYMENT CENTER (LIMITED LIABILITY COMPANY)\n**Country:** Russia\n\n"
        "BIN: `400774`\n**Bank:** BANK FREEDOM FINANCE\n**Country:** Russia\n\n"
        "BIN: `400787`\n**Bank:** BANK FREEDOM FINANCE\n**Country:** Russia"
    ),
    "Canada": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400128`\n**Bank:** FEDERATION DES CAISSES DESJARDINS DU QUEBEC\n**Country:** Canada\n\n"
        "BIN: `400129`\n**Bank:** FEDERATION DES CAISSES DESJARDINS DU QUEBEC\n**Country:** Canada\n\n"
        "BIN: `400203`\n**Bank:** MBNA\n**Country:** Canada\n\n"
        "BIN: `400204`\n**Bank:** MBNA\n**Country:** Canada\n\n"
        "BIN: `400379`\n**Bank:** DIRECTCASH BANK\n**Country:** Canada\n\n"
        "BIN: `401098`\n**Bank:** MBNA\n**Country:** Canada\n\n"
        "BIN: `401742`\n**Bank:** COLUMBUS BANK AND TRUST\n**Country:** Canada\n\n"
        "BIN: `402371`\n**Bank:** PEOPLES TRUST COMPANY\n**Country:** Canada\n\n"
        "BIN: `402372`\n**Bank:** PEOPLES TRUST COMPANY\n**Country:** Canada\n\n"
        "BIN: `403274`\n**Bank:** CANADIAN IMPERIAL BANK OF COMMERCE\n**Country:** Canada"
    ),
    "Germany": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400188`\n**Bank:** LUFTHANSA AIRPLUS SERVICEKARTEN GMBH\n**Country:** Germany\n\n"
        "BIN: `400272`\n**Bank:** COMMERZBANK AG\n**Country:** Germany\n\n"
        "BIN: `400697`\n**Bank:** COMMERZBANK AG\n**Country:** Germany\n\n"
        "BIN: `401004`\n**Bank:** WUSTENROT BANK AG PFANDBRIEFBANK\n**Country:** Germany\n\n"
        "BIN: `401080`\n**Bank:** PKO BANK POLSKI SA\n**Country:** Germany\n\n"
        "BIN: `401786`\n**Bank:** DEUTSCHE POSTBANK AG\n**Country:** Germany\n\n"
        "BIN: `401839`\n**Bank:** WEBERBANK BERLINER INDUSTRIEBANK KGAA\n**Country:** Germany\n\n"
        "BIN: `401849`\n**Bank:** COMMERZBANK AG\n**Country:** Germany\n\n"
        "BIN: `401850`\n**Bank:** COMMERZBANK AG\n**Country:** Germany\n\n"
        "BIN: `402007`\n**Bank:** UNICREDIT BANK AG\n**Country:** Germany"
    ),
    "Saudi Arabia": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `400067`\n**Bank:** ARAB NATIONAL BANK\n**Country:** Saudi Arabia\n\n"
        "BIN: `400399`\n**Bank:** NATIONAL COMMERCIAL BANK\n**Country:** Saudi Arabia\n\n"
        "BIN: `400795`\n**Bank:** AL BILAD BANK\n**Country:** Saudi Arabia\n\n"
        "BIN: `400861`\n**Bank:** AL-RAJHI BANKING AND INVESTMENT CORPORATION\n**Country:** Saudi Arabia\n\n"
        "BIN: `401560`\n**Bank:** RIYAD BANK\n**Country:** Saudi Arabia\n\n"
        "BIN: `401758`\n**Bank:** BANK AL JAZIRA\n**Country:** Saudi Arabia\n\n"
        "BIN: `401812`\n**Bank:** BANQUE SAUDI FRANSI\n**Country:** Saudi Arabia\n\n"
        "BIN: `401883`\n**Bank:** BANQUE SAUDI FRANSI\n**Country:** Saudi Arabia\n\n"
        "BIN: `401884`\n**Bank:** BANQUE SAUDI FRANSI\n**Country:** Saudi Arabia\n\n"
        "BIN: `401978`\n**Bank:** BANQUE SAUDI FRANSI\n**Country:** Saudi Arabia"
    ),
    "France": (
        "Smart Tool ⚙️ - Bin database 📋\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "BIN: `401005`\n**Bank:** CREDIT DU NORD\n**Country:** France\n\n"
        "BIN: `401006`\n**Bank:** CREDIT DU NORD\n**Country:** France\n\n"
        "BIN: `401010`\n**Bank:** 1\n**Country:** France\n\n"
        "BIN: `401030`\n**Bank:** ORANGE BANK\n**Country:** France\n\n"
        "BIN: `401031`\n**Bank:** ORANGE BANK\n**Country:** France\n\n"
        "BIN: `401032`\n**Bank:** ORANGE BANK\n**Country:** France\n\n"
        "BIN: `401034`\n**Bank:** ORANGE BANK\n**Country:** France\n\n"
        "BIN: `401035`\n**Bank:** ORANGE BANK\n**Country:** France\n\n"
        "BIN: `402096`\n**Bank:** NATIXIS\n**Country:** France\n\n"
        "BIN: `402097`\n**Bank:** NATIXIS\n**Country:** France"
    )
}

# List of accepted countries
accepted_countries = list(bin_databases.keys())

def setup_db_handlers(app: Client):
    @app.on_message(filters.command("bindb") & (filters.private | filters.group))
    async def bindb_handler(client: Client, message: Message):
        user_input = message.text.split(maxsplit=1)
        if len(user_input) == 1:
            await message.reply_text("**Please provide a full country name for bin database ❌**")
            return

        country = user_input[1].capitalize()
        if country not in accepted_countries:
            await message.reply_text("**Please provide a valid country name ❌**")
            return

        fetching_message = await message.reply_text(f"**Fetching Bin Database With Country Name ({country})...**")

        # Simulate fetching delay
        await asyncio.sleep(2)

        await fetching_message.delete()

        # Handle the case where "Brasil" is used instead of "Brazil"
        if country == "Brasil":
            country = "Brazil"

        bin_data, url = bin_databases[country]
        button = InlineKeyboardButton("Full Output", url=url)
        reply_markup = InlineKeyboardMarkup([[button]])

        await message.reply_text(f"**{bin_data}**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    return app
