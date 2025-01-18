import requests
import base64
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

async def handle_quote_command(client: Client, message: Message):
    if len(message.command) <= 1:
        await message.reply_text("**Provide text to generate a sticker.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    text = " ".join(message.command[1:])
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    avatar_url = "https://example.com/default_avatar.png"  # You can use a default avatar URL

    json = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#FFFFFF",
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": [
            {
                "entities": [],
                "avatar": True,
                "from": {
                    "id": message.from_user.id,
                    "name": username,
                    "photo": {
                        "url": avatar_url
                    }
                },
                "text": text,
                "replyMessage": {}
            }
        ]
    }

    response = requests.post('https://bot.lyo.su/quote/generate', json=json).json()
    buffer = base64.b64decode(response['result']['image'].encode('utf-8'))
    sticker_path = 'Quotly.png'
    with open(sticker_path, 'wb') as f:
        f.write(buffer)

    await client.send_photo(
        chat_id=message.chat.id,
        photo=sticker_path,
        caption="Here is your quote sticker!",
        parse_mode=ParseMode.MARKDOWN
    )

def setup_quote_handler(app: Client):
    @app.on_message(filters.command("q") & filters.private)
    async def quote_command(client: Client, message: Message):
        await handle_quote_command(client, message)
