from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import BadRequest
from pyrogram.raw.functions.stickers import CreateStickerSet
from pyrogram.raw.types import InputStickerSetItem, InputDocument, InputUser
import random
import string
from pyrogram.handlers import MessageHandler

async def kang_sticker(client: Client, message: Message):
    # Log message for debugging
    print("Received /kang command")

    if not message.reply_to_message:
        await message.reply_text("**Reply to a sticker or image to kang it.**", parse_mode=enums.ParseMode.MARKDOWN)
        return

    reply = message.reply_to_message

    if not (reply.sticker or reply.photo):
        await message.reply_text("**Reply to a sticker or image to kang it.**", parse_mode=enums.ParseMode.MARKDOWN)
        return

    fetching_message = await message.reply_text("**Changing This Sticker....**", parse_mode=enums.ParseMode.MARKDOWN)
    
    # Generate a random short name for the sticker pack
    short_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + f"_by_{client.me.username.lower()}"
    title = "Kanged Stickers"
    
    # Prepare the sticker input
    if reply.sticker:
        file_id = reply.sticker.file_id
        emoji = reply.sticker.emoji or "🤩"
        sticker_file = await client.download_media(file_id)
    elif reply.photo:
        file_id = reply.photo.file_id
        emoji = "🤩"
        sticker_file = await client.download_media(file_id)
    else:
        await fetching_message.delete()
        await message.reply_text("**Reply to a sticker or image to kang it.**", parse_mode=enums.ParseMode.MARKDOWN)
        return

    # Send the sticker to the bot to upload it
    sent_sticker = await client.send_sticker(chat_id=message.chat.id, sticker=sticker_file)

    user = await client.resolve_peer(message.from_user.id)
    try:
        # The following invocation sends a request to create a sticker set
        await client.invoke(
            CreateStickerSet(
                user_id=InputUser(user_id=user.user_id, access_hash=user.access_hash),
                title=title,
                short_name=short_name,
                stickers=[InputStickerSetItem(
                    document=InputDocument(id=sent_sticker.sticker.file_id, access_hash=0, file_reference=b""),
                    emoji=emoji
                )]
            )
        )
    except BadRequest as e:
        await fetching_message.delete()
        await message.reply_text(f"Error: {e}")
        return

    await fetching_message.delete()
    await message.reply_text(
        f"**Sticker Kannged**\n**Sticker Emoji {emoji}**",
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("View Sticker Pack", url=f"t.me/addstickers/{short_name}")
        ]])
    )

# Set up the message handler
def setup_kang_handler(app: Client):
    # Add a message handler to listen for the /kang command and reply to a sticker/photo
    handler = MessageHandler(kang_sticker, filters.command("kang") & filters.reply)
    app.add_handler(handler)
