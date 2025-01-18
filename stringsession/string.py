import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, ApiIdPublishedFloodError

user_data = {}

def setup_string_handler(app):
    # Inline keyboard for start and close
    start_close_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Start", callback_data="start_session")],
        [InlineKeyboardButton("Close", callback_data="close_session")]
    ])

    # Inline keyboard for restart and close
    restart_close_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Restart", callback_data="restart_session")],
        [InlineKeyboardButton("Close", callback_data="close_session")]
    ])

    async def send_start_message(client, message, command):
        await message.reply_text(
            f"Welcome to the {command.capitalize()} session setup!\n"
            "━━━━━━━━━━━━━━━━━\n"
            "This is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.\n\n"
            "Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.",
            reply_markup=start_close_buttons
        )

    @app.on_message(filters.command(["pyro_session", "tele_session"]) & filters.private)
    async def handle_command(client, message):
        command = message.text[1:]
        user_data[message.from_user.id] = {
            "command": command,
            "api_id": None,
            "api_hash": None,
            "phone_number": None,
            "otp": None,
            "2fa": None,
            "start_time": asyncio.get_event_loop().time()
        }
        await send_start_message(client, message, command)

    @app.on_callback_query(filters.regex("start_session"))
    async def handle_start(client, callback_query):
        await callback_query.message.reply_text("**Send Your API ID**", reply_markup=restart_close_buttons)

    @app.on_callback_query(filters.regex("close_session"))
    async def handle_close(client, callback_query):
        await callback_query.message.reply_text("Command function closed.")
        await callback_query.message.delete()

    @app.on_callback_query(filters.regex("restart_session"))
    async def handle_restart(client, callback_query):
        user_id = callback_query.from_user.id
        command = user_data.get(user_id, {}).get("command", "")
        if command:
            await send_start_message(client, callback_query.message, command)

    @app.on_message(filters.text & filters.private)
    async def handle_user_input(client, message):
        user_id = message.from_user.id
        if user_id not in user_data:
            return

        data = user_data[user_id]

        if data["api_id"] is None:
            data["api_id"] = message.text
            await message.reply_text("**Send Your API Hash**", reply_markup=restart_close_buttons)
        elif data["api_hash"] is None:
            data["api_hash"] = message.text
            if await validate_api_credentials(data["api_id"], data["api_hash"]):
                await message.reply_text("**Send Your Phone Number**\n[Example: +880xxxxxxxxxx]", reply_markup=restart_close_buttons)
            else:
                await message.reply_text("**API ID & API Hash are wrong. Please start again**", reply_markup=restart_close_buttons)
                data["api_id"] = None
                data["api_hash"] = None
        elif data["phone_number"] is None:
            data["phone_number"] = message.text
            await message.reply_text("**Send The OTP as text. Please send a text message embedding the OTP like: 'AB1 CD2 EF3 GH4 IJ5'**", reply_markup=restart_close_buttons)
        elif data["otp"] is None:
            otp = "".join([part[2:] for part in message.text.split()])
            data["otp"] = otp
            if account_requires_2fa(data["phone_number"]):
                await message.reply_text("**2FA Is Required To Login Please Enter 2FA**", reply_markup=restart_close_buttons)
            else:
                session_string = generate_session_string(data["api_id"], data["api_hash"], data["phone_number"], data["otp"])
                await save_session_string(client, message, data, session_string)
        elif data["2fa"] is None and account_requires_2fa(data["phone_number"]):
            data["2fa"] = message.text
            session_string = generate_session_string(data["api_id"], data["api_hash"], data["phone_number"], data["otp"], data["2fa"])
            await save_session_string(client, message, data, session_string)

    async def validate_api_credentials(api_id, api_hash):
        try:
            client = TelegramClient('anon', api_id, api_hash)
            await client.connect()
            await client.disconnect()
            return True
        except (ApiIdInvalidError, ApiIdPublishedFloodError):
            return False

    def account_requires_2fa(phone_number):
        # Implement your logic to check if 2FA is required
        return False

    def generate_session_string(api_id, api_hash, phone_number, otp, two_fa=None):
        # Implement your session string generation logic here
        return "GeneratedSessionString"

    async def save_session_string(client, message, data, session_string):
        command = data["command"]
        await message.reply_text(f"**This string has been saved ✅ in your Saved Messages**\n\n"
                                 f"({command.capitalize()} SESSION STRING FROM Smart Tool:\n\n"
                                 f"{session_string}")
        await client.send_message(message.from_user.id, f"{command.capitalize()} SESSION STRING FROM Smart Tool:\n\n{session_string}")
        del user_data[message.from_user.id]

    @app.on_message(filters.text & filters.private)
    async def check_for_timeout(client, message):
        user_id = message.from_user.id
        if user_id in user_data:
            start_time = user_data[user_id]["start_time"]
            if asyncio.get_event_loop().time() - start_time > 600:  # 10 minutes timeout
                command = user_data[user_id]["command"]
                await message.reply_text(f"**Your time expired. Try /{command} to start again.**")
                del user_data[user_id]
