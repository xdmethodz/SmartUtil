import time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError,
)

# Constants for timeouts
TIMEOUT_OTP = 600  # 10 minutes
TIMEOUT_2FA = 300  # 5 minutes

sessions = {}

def setup_string_handler(app: Client):
    @app.on_message(filters.command("pyro") & filters.private)
    def pyro_command(client, message):
        proceed_session(client, message, telethon=False)

    @app.on_message(filters.command("tele") & filters.private)
    def tele_command(client, message):
        proceed_session(client, message, telethon=True)

    def proceed_session(client, message, telethon=False):
        session_type = "Telethon" if telethon else "Pyrogram"
        sessions[message.chat.id] = {"type": session_type}
        message.reply(
            f"**Welcome to the {session_type} session setup!**\n"
            "**━━━━━━━━━━━━━━━━━**\n"
            "**This is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.**\n\n"
            "**Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Start", callback_data=f"start_{session_type.lower()}"),
                InlineKeyboardButton("Close", callback_data="close")
            ]])
        )

    @app.on_callback_query(filters.regex(r"^start_(pyrogram|telethon)"))
    def on_start_callback(client, callback_query):
        session_type = callback_query.data.split('_')[1]
        callback_query.message.edit_text(
            "<b>Send Your API ID</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Restart", callback_data=f"restart_{session_type}"),
                InlineKeyboardButton("Close", callback_data="close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        sessions[callback_query.message.chat.id]["stage"] = "api_id"

    @app.on_callback_query(filters.regex(r"^restart_(pyrogram|telethon)"))
    def on_restart_callback(client, callback_query):
        session_type = callback_query.data.split('_')[1]
        proceed_session(client, callback_query.message, telethon=(session_type == "telethon"))

    @app.on_callback_query(filters.regex(r"^close"))
    def on_close_callback(client, callback_query):
        callback_query.message.edit_text("Session generation process has been closed.")
        if callback_query.message.chat.id in sessions:
            del sessions[callback_query.message.chat.id]

    @app.on_message(filters.text & filters.private)
    def on_text_message(client, message):
        chat_id = message.chat.id
        if chat_id not in sessions:
            return

        session = sessions[chat_id]
        stage = session.get("stage")

        if cancelled(message):
            return

        if stage == "api_id":
            handle_api_id(client, message, session)
        elif stage == "api_hash":
            handle_api_hash(client, message, session)
        elif stage == "phone_number":
            handle_phone_number(client, message, session)
        elif stage == "otp":
            handle_otp(client, message, session)
        elif stage == "2fa":
            handle_2fa(client, message, session)

    def handle_api_id(client, message, session):
        try:
            api_id = int(message.text)
            session["api_id"] = api_id
            message.reply(
                "<b>Send Your API Hash</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="close")
                ]]),
                parse_mode=ParseMode.HTML
            )
            session["stage"] = "api_hash"
        except ValueError:
            message.reply("Invalid API ID. Please enter a valid integer.")

    def handle_api_hash(client, message, session):
        session["api_hash"] = message.text
        message.reply(
            "<b>Send Your Phone Number\n[Example: +880xxxxxxxxxx]</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                InlineKeyboardButton("Close", callback_data="close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        session["stage"] = "phone_number"

    def handle_phone_number(client, message, session):
        session["phone_number"] = message.text
        message.reply("Sending OTP.....")
        send_otp(client, message)

    def handle_otp(client, message, session):
        otp = ''.join([char for char in message.text if char.isdigit()])
        session["otp"] = otp
        message.reply("Validating OTP.....")
        validate_otp(client, message)

    def handle_2fa(client, message, session):
        session["password"] = message.text
        validate_2fa(client, message)

    def send_otp(client, message):
        session = sessions[message.chat.id]
        api_id = session["api_id"]
        api_hash = session["api_hash"]
        phone_number = session["phone_number"]
        telethon = session["type"] == "Telethon"

        if telethon:
            client_obj = TelegramClient(StringSession(), api_id, api_hash)
        else:
            client_obj = Client(in_memory=True, api_id=api_id, api_hash=api_hash)

        client_obj.connect()

        try:
            if telethon:
                code = client_obj.send_code_request(phone_number)
            else:
                code = client_obj.send_code(phone_number)
            session["client_obj"] = client_obj
            session["code"] = code
            session["stage"] = "otp"
            message.reply(
                "<b>Send The OTP as text. Please send a text message embedding the OTP like: 'AB1 CD2 EF3 GH4 IJ5'</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="close")
                ]]),
                parse_mode=ParseMode.HTML
            )
        except (ApiIdInvalid, ApiIdInvalidError):
            message.reply('API ID & API Hash are wrong. Please start again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return
        except (PhoneNumberInvalid, PhoneNumberInvalidError):
            message.reply('PHONE NUMBER is invalid. Please start again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return

    def validate_otp(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        phone_number = session["phone_number"]
        otp = session["otp"]
        code = session["code"]
        telethon = session["type"] == "Telethon"

        try:
            if telethon:
                client_obj.sign_in(phone_number, otp, password=None)
            else:
                client_obj.sign_in(phone_number, code.phone_code_hash, otp)
            generate_session(client, message)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            message.reply('OTP is invalid. Please start again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            message.reply('OTP is expired. Please start again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            session["stage"] = "2fa"
            message.reply(
                "<b>2FA Is Required To Login. Please Enter 2FA</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="close")
                ]]),
                parse_mode=ParseMode.HTML
            )

    def validate_2fa(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        password = session["password"]
        telethon = session["type"] == "Telethon"

        try:
            if telethon:
                client_obj.sign_in(password=password)
            else:
                client_obj.check_password(password=password)
            generate_session(client, message)
        except (PasswordHashInvalid, PasswordHashInvalidError):
            message.reply('Invalid Password Provided. Please start again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return

    def generate_session(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        telethon = session["type"] == "Telethon"

        if telethon:
            string_session = client_obj.session.save()
        else:
            string_session = client_obj.export_session_string()

        text = f"**{session['type'].upper()} SESSION STRING FROM Smart Tool**:\n\n{string_session}"

        try:
            client_obj.send_message("me", text)
        except KeyError:
            pass

        client_obj.disconnect()
        message.reply("<b>This string has been saved ✅ in your Saved Messages</b>", parse_mode=ParseMode.HTML)
        del sessions[message.chat.id]

    def cancelled(message):
        if "/cancel" in message.text:
            message.reply("Cancelled the Process!", quote=True)
            return True
        elif "/restart" in message.text:
            message.reply("Restarted the Bot!", quote=True)
            return True
        elif message.text.startswith("/"):  # Bot Commands
            message.reply("Cancelled the process!", quote=True)
            return True
        else:
            return False
