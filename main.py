from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from pyrogram.enums import ParseMode
# Import the handlers
from decoders.decoders import setup_decoders_handler
from others.privacy import setup_privacy_handler
from others.yth import setup_yth_handler
from others.info import setup_info_handler
from others.times import setup_time_handler
from others.privacy import setup_privacy_handler
from crypto.binance import setup_binance_handler
from tempmail.tempmail import setup_temp_mail_handler
from crypto.crypto import setup_crypto_handler
from others.fake import setup_fake_handler
from educationutils.education import setup_education_handler
from aitools.gpt import setup_gpt_handlers 
from others.ip import setup_ip_handlers
from others.admin import setup_admin_handlers
from others.downloaders import setup_downloader_handler
from others.pin import setup_pinterest_handler
from others.dl import setup_dl_handlers
from others.spotify import setup_spotify_handler
from creditcards.gen import setup_handlers
from educationutils.grammar import setup_eng_handler
# Replace these with your actual API details
API_ID = "24602058"  # Replace with your API ID
API_HASH = "b976a44ccb8962b20113113f84aeebf6"  # Replace with your API Hash
BOT_TOKEN = "7941865929:AAFh8u_6r7FCEAG564vZ3bvvdphZ-QRFBPg"  # Replace with your Bot Token

# Initialize the app client
app = Client(
    "app_session",  # Session name
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Setup handlers
setup_decoders_handler(app)
setup_privacy_handler(app)
setup_yth_handler(app)
setup_info_handler(app)
setup_time_handler(app)
setup_binance_handler(app)
setup_temp_mail_handler(app)
setup_crypto_handler(app)
setup_fake_handler(app)
setup_education_handler(app)
setup_gpt_handlers(app)
setup_ip_handlers(app)
setup_admin_handlers(app)
setup_downloader_handler(app)
setup_pinterest_handler(app)
setup_dl_handlers(app)
setup_spotify_handler(app)
setup_handlers(app)
setup_eng_handler(app)
# Inline keyboard for the main menu
main_menu_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("AI Tools", callback_data="ai_tools"),
        InlineKeyboardButton("Credit Cards", callback_data="credit_cards"),
    ],
    [
        InlineKeyboardButton("Crypto", callback_data="crypto"),
        InlineKeyboardButton("Decoders", callback_data="decoders"),
    ],
    [
        InlineKeyboardButton("Downloaders", callback_data="downloaders"),
        InlineKeyboardButton("Education Utils", callback_data="education_utils"),
    ],
    [
        InlineKeyboardButton("Mail Tools", callback_data="mail_tools"),
        InlineKeyboardButton("Temp Mail", callback_data="temp_mail"),
    ],
    [
        InlineKeyboardButton("String Session", callback_data="string_session"),
        InlineKeyboardButton("Stripe Keys", callback_data="stripe_keys"),
    ],
    [
        InlineKeyboardButton("Others", callback_data="others"),
        InlineKeyboardButton("Close", callback_data="close"),
    ]
])

@app.on_message(filters.command("start") & filters.private)
async def send_start_message(client, message):
    chat_id = message.chat.id
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name

    # Animation messages
    animation_message = await message.reply_text("<b>Starting Smart Tool ⚙️...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)  # Use asyncio.sleep instead of sleep
    await animation_message.edit_text("<b>Generating Session Keys Please Wait...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)  # Use asyncio.sleep instead of sleep
    await animation_message.delete()

    # Main welcome message
    start_message = (
        f"<b>Hi — {full_name}! Welcome to this bot</b>\n"
        "<b>________________________________</b>\n"
        "<b><a href='https://t.me/Smart_Nexus_Bot'>Smart Tool ⚙️</a></b>: The ultimate toolkit on Telegram, offering education, AI, downloaders, temp mail, credit card tool, and more. Simplify your tasks with ease!\n"
        "<b>________________________________</b>\n"
        "<b>Don't forget to <a href='https://t.me/abir_x_official'>join</a> for updates!</b>"
    )

    await message.reply_text(
        start_message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Main Menu", callback_data="main_menu")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/abir_x_official"),
             InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")]
        ]),
        disable_web_page_preview=True,
    )

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    call = callback_query
    responses = {
        "ai_tools": (
            "Smart Tool ⚙️ Ai-Tool Usage Cmds\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /gpt - Ask a question to ChatGPT 3.5\n"
            "➢ /gpt4 - Ask a question to ChatGPT 4\n"
            "➢ /gem - Ask a question to Gemini Ai\n"
            "➢ /imgai - Image analysis that can read image\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "credit_cards": (
            "Smart Tool ⚙️ Credit Cards Related Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /gen - CC Generator\n"
            "➢ /bin - Check BIN\n"
            "➢ /scr - CC Scrape\n"
            "➢ /fcc - For Filter CCS\n"
            "➢ /extp - CC Extrapolate\n"
            "➢ /mgen - Multi CC Generator\n"
            "➢ /mc - Multi CC Scrape\n"
            "➢ /topbin - Find Top BIN From Combo\n"
            "➢ /binbank - Find BIN Database By Bank Name\n"
            "➢ /bindb - Find BIN Database By Country Name\n"
            "➢ /adbin - Filter Specific BIN CARDS From Combo\n"
            "➢ /rmbin - Remove Specific BIN Cards From Combo\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "decoders": (
            "Smart Tool ⚙️ All Encode & Decode Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /b64en [text] - Base64 encode\n"
            "➢ /b64de [text] - Base64 decode\n"
            "➢ /b32en [text] - Base32 encode\n"
            "➢ /b32de [text] - Base32 decode\n"
            "➢ /binen [text] - Binary encode\n"
            "➢ /binde [text] - Binary decode\n"
            "➢ /hexen [text] - Hex encode\n"
            "➢ /hexde [text] - Hex decode\n"
            "➢ /octen [text] - Octal encode\n"
            "➢ /octde [text] - Octal decode\n"
            "➢ /trev [text] - Reverse text\n"
            "➢ /tcap [text] - Transform to capital letters\n"
            "➢ /tsm [text] - Transform to small letters\n"
            "➢ /wc [text] - Count words\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "downloaders": (
            "Smart Tool ⚙️ Downloader Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /fb - Download Facebook Video\n"
            "➢ /pin - Download Pinterest Video\n"
            "➢ /in - Download Instagram Reels\n"
            "➢ /sp - Download Spotify Track\n"
            "➢ /video - Download Youtube Video\n"
            "➢ /song - Download Youtube Video as Mp3 Format\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "education_utils": (
            "Smart Tool ⚙️ Educational Cmds\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /spell [Words] - For Fixing Word Spelling\n"
            "➢ /gra [Sentence]  - For Fixing Grammatical Issues\n"
            "➢ /syn [Word]  - For check synonyms and antonyms\n"
            "➢ /prn [Word]  - For check pronunciation\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "mail_tools": (
            "Smart Tool ⚙️ Mail - Tools\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /fmail - Filter/Extract Mails\n"
            "➢ /fpass - Filter/Extract Mail - Pass\n"
            "➢ /scrmail - Mail-Pass Scrape target GC\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "temp_mail": (
            "Smart Tool ⚙️ TempMail Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /tmail - Command for Generate Random Mail with Pass\n"
            "➢ /tmail [username]:[pass] - For Generate a Specific Mail with a Password\n"
            "➢ /cmail [mail token] - For Check Recent 10 Mails\n\n"
            "✨ Note : When you generate a mail pass, then you will receive a mail token. With the token, you can check 10 recent mails each mail has a different token. So keep it privately.\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "string_session": (
            "Smart Tool ⚙️ String_Session\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /pyro - PyroGram Telegram String Session\n"
            "➢ /tele - TeleThon Telegram String Session\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "stripe_keys": (
            "Smart Tool ⚙️ Stripe Key Related Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /sk - Get Information about SK\n"
            "➢ /skinfo - SK Checker Live/Dead\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "crypto": (
            "Smart Tool ⚙️ Crypto Related Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /price -[token name] Real-Time Token Prices\n"
            "➢ /p2p to get Latest P2P Trades Currency BDT\n"
            "➢ /gainers - Cryptos with highest price increases for potential profits\n"
            "➢ /losers - Cryptos with largest price drops for potential buy opportunities\n"
            "✨ Note : Smart Tool ⚙️ uses the Binance API to fetch the latest price, p2p, gainers & losers data for cryptocurrency\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "others": (
            "Smart Tool ⚙️ Other Commands\n"
            "━━━━━━━━━━━━━━━━\n"
            "➢ /ip - Get IP Information\n"
            "➢ /px - HTTP/HTTPS Proxy Checker\n"
            "➢ /ss - Take Screenshot of Webpage\n"
            "➢ /ytag - Extract YouTube Video Tags\n"
            "➢ /ocr - Extract ENG Text From Image\n"
            "➢ /fake - Generate Random Address\n"
            "➢ /ws - Download Source Code of Website\n"
            "➢ /info - Get Any user/group/channel Info\n"
            "➢ /privacy - Privacy Policy for Smart Tool\n"
            "➢ /yth - Download YouTube Video Thumbnail\n"
            "➢ /time - Current Time and Date of Any Country\n"
            "➢ /tren [en lang code] - Google Translator Translates Words\n"
            "➢ /price [token name] - Real-Time Token Prices\n"
            "➢ /p2p - Get Latest P2P Trades Currency BDT\n"
            "➢ /aud - Reply to a Video to Convert to Audio\n"
            "➢ /q - Generate a Sticker\n"
            "➢ /kang - Kang Any Image, Sticker, or Animated Sticker\n"
            "━━━━━━━━━━━━━━━━\n"
            "For Smart Tool ⚙️ Bot Update News : <a href='https://t.me/abir_x_official'>Join Now</a>",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
        "about_me": (
            "<b>Name:</b> Smart Util ⚙️\n"
            "<b>Version:</b> 3.0 (Beta Testing) 🛠\n\n"
            "<b>Development Team:</b>\n"
            "- <b>Creator:</b> <a href='https://t.me/abirxdhackz'>⏤͟͞〲ᗩᗷiᖇ 𓊈乂ᗪ𓊉 👨‍💻</a>\n"
            "- <b>Contributor:</b> <a href='https://t.me/hmm_Smokie'>HMM٭SMOKIE 🤝</a>\n\n"
            "<b>Technical Stack:</b>\n"
            "- <b>Language:</b> Python 🐍\n"
            "- <b>Libraries:</b> Aiogram, Pyrogram 📚\n"
            "- <b>Database:</b> MongoDB 🗄\n"
            "- <b>Hosting:</b> Hostinger 🌐\n\n"
            "<b>About:</b> The all-in-one Telegram toolkit for seamless education, AI, downloads, and more!",
            {'parse_mode': ParseMode.HTML, 'disable_web_page_preview': True}
        ),
    }

    if call.data in responses:
        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu" if call.data != "about_me" else "start_message")]
        ])
        await call.message.edit_text(
            responses[call.data][0],  # text is the first element in the tuple
            parse_mode=ParseMode.HTML,  # Correct way to set parse_mode
            disable_web_page_preview=True,
            reply_markup=back_button
        )
    elif call.data == "main_menu":
        await call.message.edit_text(
            "Here are the Smart Tool ⚙️ Options:",
            reply_markup=main_menu_keyboard
        )
    elif call.data == "close":
        await call.message.delete()
    elif call.data == "start_message":
        full_name = f"{call.message.from_user.first_name} {call.message.from_user.last_name}" if call.message.from_user.last_name else call.message.from_user.first_name

        # Main welcome message
        start_message = (
            f"<b>Hi — {full_name}! Welcome to this bot</b>\n"
            "<b>________________________________</b>\n"
            "<b><a href='https://t.me/Smart_Nexus_Bot'>Smart Tool ⚙️</a></b>: The ultimate toolkit on Telegram, offering education, AI, downloaders, temp mail, credit card tool, and more. Simplify your tasks with ease!\n"
            "<b>________________________________</b>\n"
            "<b>Don't forget to <a href='https://t.me/abir_x_official'>join</a> for updates!</b>"
        )

        await call.message.edit_text(
            start_message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([  # Inline keyboard for main menu
                [InlineKeyboardButton("⚙️ Main Menu", callback_data="main_menu")],
                [InlineKeyboardButton("🔄 Updates", url="https://t.me/abir_x_official"),
                 InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")]
            ]),
            disable_web_page_preview=True,
        )

print("Bot is running...")
app.run()
