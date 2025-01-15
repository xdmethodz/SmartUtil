import os
import math
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

START_TEXT = """
Hey! I'm {}, and I'm a bot which allows you to create a sticker pack from other stickers, images and documents!
I only have a few commands so I don't have a help menu or anything like that.
You can also check out the source code for the bot [here](https://github.com/breakdowns/kang-stickerbot)
"""

def setup_handlers(app: Client):
    @app.on_message(filters.command("start"))
    async def start(client: Client, message: Message):
        if message.chat.type == "private":
            await message.reply_text(
                START_TEXT.format(client.me.first_name), 
                parse_mode="markdown"
            )

    @app.on_message(filters.command("kang"))
    async def kang(client: Client, message: Message):
        if not message.reply_to_message:
            await message.reply_text("**Reply to a sticker or image to kang it**")
            return

        msg = message.reply_to_message
        user = message.from_user

        if msg.sticker:
            file_id = msg.sticker.file_id
            sticker_emoji = msg.sticker.emoji if msg.sticker.emoji else "🤔"
        elif msg.photo:
            file_id = msg.photo.file_id
            sticker_emoji = "🤔"
        elif msg.document:
            file_id = msg.document.file_id
            sticker_emoji = "🤔"
        else:
            await message.reply_text("**I can't kang that.**")
            return

        # Notify the user that the bot is kanging the sticker
        progress_message = await message.reply_text("**Kanging this Sticker...**")

        # Download the file
        kang_file = await client.download_media(file_id, file_name="kangsticker.png")
        kangsticker = "kangsticker.png"

        try:
            im = Image.open(kangsticker)
            if im.width < 512 or im.height < 512:
                size1, size2 = im.size
                if im.width > im.height:
                    scale = 512 / size1
                    size1new, size2new = 512, math.floor(size2 * scale)
                else:
                    scale = 512 / size2
                    size1new, size2new = math.floor(size1 * scale), 512
                im = im.resize((size1new, size2new))
            else:
                im.thumbnail((512, 512))
            im.save(kangsticker, "PNG")
        except OSError as e:
            await progress_message.edit("**I can only kang images.**")
            logger.error(e)
            return

        packnum = 0
        packname = f"a{str(user.id)}_by_{client.me.username}"
        max_stickers = 120
        while True:
            try:
                stickerset = await client.get_sticker_set(packname)
                if len(stickerset.stickers) >= max_stickers:
                    packnum += 1
                    packname = f"a{packnum}_{str(user.id)}_by_{client.me.username}"
                else:
                    break
            except Exception as e:
                if "Stickerset_invalid" in str(e):
                    break
                logger.error(e)
                return

        try:
            await client.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                png_sticker=kangsticker,
                emojis=sticker_emoji,
            )
            await progress_message.delete()
            await message.reply_text(
                f"**Sticker Kanged!**\n**Sticker Emoji:** {sticker_emoji}",
                parse_mode="markdown",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("View Pack", url=f"t.me/addstickers/{packname}")]]
                ),
            )
        except Exception as e:
            logger.error(e)
            await progress_message.edit("**Failed to kang the sticker.**")

        if os.path.isfile(kangsticker):
            os.remove(kangsticker)

    return app
