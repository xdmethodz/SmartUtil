import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode
from telethon.sync import TelegramClient as TelethonClient
from telethon.sessions import StringSession as TelethonStringSession
from pyrogram import Client as PyroClient
from pyrogram.errors import BadRequest, PhoneCodeExpired

# Define this dictionary outside to store session data
session_data = {}
TIMEOUT = 600  # Timeout in seconds (10 minutes)

async def ask_user(client, message, question, buttons):
    reply_markup = InlineKeyboardMarkup(buttons)
    sent_message = await message.reply_text(question, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return sent_message

async def handle_start(client, message, platform):
    chat_id = message.chat.id
    session_data[chat_id] = {"platform": platform}
    buttons = [
        [InlineKeyboardButton("Go", callback_data=f"session_go_{platform}"), InlineKeyboardButton("Close", callback_data="session_close")]
    ]
    await ask_user(client, message, f"**Welcome to the {platform} session setup!**\n**━━━━━━━━━━━━━━━━━**\n**This is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.**\n\n**Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.**", buttons)
    # Start a timeout coroutine
    asyncio.create_task(timeout_session(client, chat_id, platform))

async def timeout_session(client, chat_id, platform):
    await asyncio.sleep(TIMEOUT)
    if chat_id in session_data:
        await client.send_message(chat_id, f"**Your time expired. Try /{platform.lower()} to start again.**", parse_mode=ParseMode.MARKDOWN)
        del session_data[chat_id]

async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "session_close":
        platform = session_data[chat_id]["platform"]
        await callback_query.message.edit_text(f"**Operation Cancelled. You can start by sending /{platform.lower()}.**", parse_mode=ParseMode.MARKDOWN)
        if chat_id in session_data:
            del session_data[chat_id]
        return

    if data.startswith("session_go_"):
        platform = data.split("_")[2]
        if chat_id not in session_data:
            session_data[chat_id] = {"platform": platform}
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{platform}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        new_text = "**Send Your API ID**"
        # Check if the new text is different from the current text
        if callback_query.message.text != new_text:
            await callback_query.message.edit_text(new_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        else:
            await callback_query.answer("The message is already up-to-date.", show_alert=True)
        session_data[chat_id]["step"] = "api_id"

    if data.startswith("session_resume_"):
        platform = data.split("_")[2]
        await handle_start(client, callback_query.message, platform)

async def handle_text(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in session_data:
        return

    data = session_data[chat_id]
    step = data.get("step")

    if step == "api_id":
        if not message.text.isdigit():
            await message.reply_text("**API ID should be an integer. Please Enter A Valid API ID**", parse_mode=ParseMode.MARKDOWN)
            return
        
        data["api_id"] = message.text
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{data['platform']}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        await message.reply_text("**Send Your API Hash**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        data["step"] = "api_hash"

    elif step == "api_hash":
        data["api_hash"] = message.text
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{data['platform']}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        await message.reply_text("**Send Your Phone Number\n[Example: +880xxxxxxxxxx]**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        data["step"] = "phone_number"

    elif step == "phone_number":
        data["phone_number"] = message.text
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{data['platform']}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]

        # Attempt to send the OTP
        try:
            if data["platform"] == "PyroGram":
                client = PyroClient("otp_test", api_id=int(data["api_id"]), api_hash=data["api_hash"])
                await client.connect()
                sent_code = await client.send_code(data["phone_number"])
                data["phone_code_hash"] = sent_code.phone_code_hash
                await client.disconnect()
            elif data["platform"] == "Telethon":
                client = TelethonClient(TelethonStringSession(), api_id=int(data["api_id"]), api_hash=data["api_hash"])
                await client.connect()
                sent_code = await client.send_code_request(data["phone_number"])
                data["phone_code_hash"] = sent_code.phone_code_hash
                await client.disconnect()
        except Exception as e:
            await message.reply_text(f"**Failed to send OTP: {str(e)}**", parse_mode=ParseMode.MARKDOWN)
            del session_data[chat_id]
            return

        await message.reply_text("**Send The OTP as text. Please send a text message embedding the OTP like: 'AB1 CD2 EF3 GH4 IJ5'**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        data["step"] = "otp"

    elif step == "otp":
        otp = ''.join(filter(str.isdigit, message.text))
        data["otp"] = otp

        if data["platform"] == "PyroGram":
            client = PyroClient(name="pyro_session", api_id=int(data["api_id"]), api_hash=data["api_hash"], phone_number=data["phone_number"])
            try:
                await client.connect()
                await client.sign_in(phone_number=data["phone_number"], phone_code_hash=data["phone_code_hash"], phone_code=data["otp"])
                session_string = await client.export_session_string()
                await client.stop()
                # Remove the session file
                client.session.delete()
            except PhoneCodeExpired:
                await message.reply_text("**The confirmation code has expired. Please request a new code by sending your phone number again.**", parse_mode=ParseMode.MARKDOWN)
                data["step"] = "phone_number"
                return
            except BadRequest as e:
                if e.value == "2FA is required":
                    await message.reply_text("**2FA Is Required To Login Please Enter 2FA**", parse_mode=ParseMode.MARKDOWN)
                    data["step"] = "2fa"
                    return
                else:
                    await message.reply_text(f"Error: {e}", parse_mode=ParseMode.MARKDOWN)
                    del session_data[chat_id]
                    return

        elif data["platform"] == "Telethon":
            client = TelethonClient(TelethonStringSession(), api_id=int(data["api_id"]), api_hash=data["api_hash"])
            try:
                await client.connect()
                await client.sign_in(phone=data["phone_number"], code=data["otp"])
                session_string = client.session.save()
                await client.disconnect()
                # Remove the session file
                client.session.delete()
            except PhoneCodeExpired:
                await message.reply_text("**The confirmation code has expired. Please request a new code by sending your phone number again.**", parse_mode=ParseMode.MARKDOWN)
                data["step"] = "phone_number"
                return
            except Exception as e:
                if "2FA" in str(e):
                    await message.reply_text("**2FA Is Required To Login Please Enter 2FA**", parse_mode=ParseMode.MARKDOWN)
                    data["step"] = "2fa"
                    return
                else:
                    await message.reply_text(f"Error: {e}", parse_mode=ParseMode.MARKDOWN)
                    del session_data[chat_id]
                    return

        await message.reply_text("**This string has been saved ✅ in your Saved Messages**", parse_mode=ParseMode.MARKDOWN)
        await client.send_message("me", f"{data['platform']} SESSION STRING FROM Smart Tool:\n\n{session_string}")
        del session_data[chat_id]

    elif step == "2fa":
        data["2fa"] = message.text

        if data["platform"] == "PyroGram":
            client = PyroClient(name="pyro_session", api_id=int(data["api_id"]), api_hash=data["api_hash"], phone_number=data["phone_number"])
            await client.connect()
            await client.sign_in(phone_number=data["phone_number"], phone_code_hash=data["phone_code_hash"], phone_code=data["otp"], password=data["2fa"])
            session_string = await client.export_session_string()
            await client.stop()
            # Remove the session file
            client.session.delete()

        elif data["platform"] == "Telethon":
            client = TelethonClient(TelethonStringSession(), api_id=int(data["api_id"]), api_hash=data["api_hash"])
            await client.connect()
            await client.sign_in(phone=data["phone_number"], code=data["otp"], password=data["2fa"])
            session_string = client.session.save()
            await client.disconnect()
            # Remove the session file
            client.session.delete()

        await message.reply_text("**This string has been saved ✅ in your Saved Messages**", parse_mode=ParseMode.MARKDOWN)
        await client.send_message("me", f"{data['platform']} SESSION STRING FROM Smart Tool:\n\n{session_string}")
        del session_data[chat_id]

def setup_string_handler(app: Client):
    @app.on_message(filters.command(["pyro", "tele"]))
    async def session_setup(client, message: Message):
        platform = "PyroGram" if message.command[0] == "pyro" else "Telethon"
        await handle_start(client, message, platform)

    @app.on_callback_query(filters.regex(r"^session_go_"))
    async def callback_query_go_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_callback_query(filters.regex(r"^session_resume_"))
    async def callback_query_resume_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_callback_query(filters.regex(r"^session_close$"))
    async def callback_query_close_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_message(filters.text & filters.create(lambda _, __, message: message.chat.id in session_data))
    async def text_handler(client, message: Message):
        await handle_text(client, message)
