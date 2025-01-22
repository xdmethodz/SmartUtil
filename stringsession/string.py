import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode
from telethon.sync import TelegramClient as TelethonClient
from telethon.sessions import StringSession as TelethonStringSession
from pyrogram import Client as PyroClient
from pyrogram.errors import BadRequest

# Define this dictionary outside to store session data
session_data = {}

async def ask_user(client, message, question, buttons):
    reply_markup = InlineKeyboardMarkup(buttons)
    sent_message = await message.reply_text(question, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return sent_message

async def handle_start(client, message, platform):
    session_data[message.chat.id] = {"platform": platform}
    buttons = [
        [InlineKeyboardButton("Go", callback_data=f"session_go_{platform}"), InlineKeyboardButton("Close", callback_data="session_close")]
    ]
    await ask_user(client, message, f"**Welcome to the {platform} session setup!**\n━━━━━━━━━━━━━━━━━\nThis is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.\n\n**Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.**", buttons)

async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "session_close":
        await callback_query.message.edit_text("Session setup closed.", parse_mode=ParseMode.MARKDOWN)
        if chat_id in session_data:
            del session_data[chat_id]
        return

    if data.startswith("session_go_"):
        platform = data.split("_")[2]
        session_data[chat_id] = {"platform": platform}
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_go_{platform}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        await callback_query.message.edit_text("**Send Your API ID**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        session_data[chat_id]["step"] = "api_id"

async def handle_text(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in session_data:
        return

    data = session_data[chat_id]
    step = data.get("step")

    if step == "api_id":
        data["api_id"] = message.text
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_go_{data['platform']}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        await message.reply_text("**Send Your API Hash**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        data["step"] = "api_hash"

    elif step == "api_hash":
        data["api_hash"] = message.text
        try:
            if data["platform"] == "PyroGram":
                async with PyroClient("session_test", api_id=int(data["api_id"]), api_hash=data["api_hash"]):
                    pass
            elif data["platform"] == "Telethon":
                with TelethonClient("session_test", api_id=int(data["api_id"]), api_hash=data["api_hash"]):
                    pass
        except Exception:
            await message.reply_text("**API ID & API Hash are wrong. Please start again**", parse_mode=ParseMode.MARKDOWN)
            del session_data[chat_id]
            return

        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_go_{data['platform']}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        await message.reply_text("**Send Your Phone Number\n[Example: +880xxxxxxxxxx]**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        data["step"] = "phone_number"

    elif step == "phone_number":
        data["phone_number"] = message.text
        buttons = [
            [InlineKeyboardButton("Resume", callback_data=f"session_go_{data['platform']}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]
        await message.reply_text("**Send The OTP as text. Please send a text message embedding the OTP like: 'AB1 CD2 EF3 GH4 IJ5'**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
        data["step"] = "otp"

    elif step == "otp":
        otp = ''.join(filter(str.isdigit, message.text))
        data["otp"] = otp

        if data["platform"] == "PyroGram":
            client = PyroClient(name="pyro_session", api_id=int(data["api_id"]), api_hash=data["api_hash"], phone_number=data["phone_number"])
            try:
                await client.connect()
                await client.send_code(data["phone_number"])
                await client.sign_in(data["phone_number"], code=data["otp"])
                session_string = await client.export_session_string()
                await client.stop()
                # Remove the session file
                client.session.delete()
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
                await client.send_code_request(data["phone_number"])
                await client.sign_in(data["phone_number"], code=data["otp"])
                session_string = client.session.save()
                await client.disconnect()
                # Remove the session file
                client.session.delete()
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
            await client.sign_in(data["phone_number"], code=data["otp"], password=data["2fa"])
            session_string = await client.export_session_string()
            await client.stop()
            # Remove the session file
            client.session.delete()

        elif data["platform"] == "Telethon":
            client = TelethonClient(TelethonStringSession(), api_id=int(data["api_id"]), api_hash=data["api_hash"])
            await client.connect()
            await client.sign_in(data["phone_number"], code=data["otp"], password=data["2fa"])
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

    @app.on_callback_query(filters.regex(r"^session_close$"))
    async def callback_query_close_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_message(filters.text)
    async def text_handler(client, message: Message):
        await handle_text(client, message)
