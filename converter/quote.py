import requests
import base64
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

def setup_q_handler(app: Client):
    @app.on_message(filters.command("q") & filters.private)
    async def generate_quote(client: Client, message: Message):
        # Get the text to quote from the message
        if len(message.command) < 2:
            await message.reply_text("**Please provide the text to quote.**", parse_mode=ParseMode.MARKDOWN)
            return

        text = " ".join(message.command[1:])
        user = message.from_user
        full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

        # Get the user's profile photo
        avatar_file_path = None
        if user.photo:
            avatar_file_path = await client.download_media(user.photo.big_file_id)
        else:
            await message.reply_text("**You do not have a profile photo set.**", parse_mode=ParseMode.MARKDOWN)
            return

        # Convert the avatar to base64
        with open(avatar_file_path, "rb") as file:
            avatar_data = file.read()
        avatar_base64 = base64.b64encode(avatar_data).decode()

        json_data = {
            "type": "quote",
            "format": "webp",
            "backgroundColor": "#FFFFFF",
            "width": 512,
            "height": 768,
            "scale": 2,
            "messages": [
                {
                    "entities": [],
                    "avatar": True,
                    "from": {
                        "id": user.id,
                        "name": full_name,
                        "photo": {
                            "url": f"data:image/jpeg;base64,{avatar_base64}"
                        },
                        "fontSize": "small"  # Ensure the profile name is small
                    },
                    "text": text,
                    "textFontSize": "small",  # Ensure the text is small
                    "replyMessage": {}
                }
            ]
        }

        response = requests.post('https://bot.lyo.su/quote/generate', json=json_data).json()
        buffer = base64.b64decode(response['result']['image'].encode('utf-8'))
        file_path = 'Quotly.webp'
        with open(file_path, 'wb') as f:
            f.write(buffer)

        await client.send_sticker(message.chat.id, file_path)
        os.remove(file_path)  # Clean up the file
        os.remove(avatar_file_path)  # Clean up the downloaded avatar file
