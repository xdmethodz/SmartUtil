import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import asyncio

# Define a function to generate a new sticker pack name
def generate_sticker_pack_name(user_id):
    return f"{user_id}_kang_pack_by_bot"

def setup_kang_handler(app: Client):
    @app.on_message(filters.command("Kang") & filters.private)
    async def kang_sticker(client: Client, message: Message):
        # Check if the message is a reply to a sticker or image
        if not message.reply_to_message or not (message.reply_to_message.sticker or message.reply_to_message.photo):
            await message.reply_text("**Reply to a sticker or image to kang it.**", parse_mode=ParseMode.MARKDOWN)
            return

        # Inform the user that kanging has started
        kanging_message = await message.reply_text("**Kanging this Sticker...**", parse_mode=ParseMode.MARKDOWN)

        # Process the sticker or image
        sticker = message.reply_to_message.sticker
        photo = message.reply_to_message.photo
        emoji = "🤔"  # Default emoji for photos

        if sticker:
            file_id = sticker.file_id
            emoji = sticker.emoji or "🤔"
            is_animated = sticker.is_animated
            is_video = sticker.is_video
        elif photo:
            file_id = photo.file_id
            is_animated = False
            is_video = False

        # Download the sticker or image
        file_path = await client.download_media(file_id)

        # Generate the new sticker pack name
        user_id = message.from_user.id
        sticker_pack_name = generate_sticker_pack_name(user_id)
        sticker_pack_title = f"{message.from_user.first_name}'s Kanged Pack"

        try:
            # Try to add the sticker to the existing pack
            if is_animated:
                await client.add_sticker_to_set(
                    user_id=user_id,
                    name=sticker_pack_name,
                    emojis=emoji,
                    tgs_sticker=file_path
                )
            elif is_video:
                await client.add_sticker_to_set(
                    user_id=user_id,
                    name=sticker_pack_name,
                    emojis=emoji,
                    webm_sticker=file_path
                )
            else:
                await client.add_sticker_to_set(
                    user_id=user_id,
                    name=sticker_pack_name,
                    emojis=emoji,
                    png_sticker=file_path
                )
        except Exception as e:
            # If the pack does not exist, create a new one
            try:
                if is_animated:
                    await client.create_new_sticker_set(
                        user_id=user_id,
                        name=sticker_pack_name,
                        title=sticker_pack_title,
                        emojis=emoji,
                        tgs_sticker=file_path
                    )
                elif is_video:
                    await client.create_new_sticker_set(
                        user_id=user_id,
                        name=sticker_pack_name,
                        title=sticker_pack_title,
                        emojis=emoji,
                        webm_sticker=file_path
                    )
                else:
                    await client.create_new_sticker_set(
                        user_id=user_id,
                        name=sticker_pack_name,
                        title=sticker_pack_title,
                        emojis=emoji,
                        png_sticker=file_path
                    )
            except Exception as e:
                await kanging_message.delete()
                await message.reply_text(f"**Failed to kang the sticker:** {e}", parse_mode=ParseMode.MARKDOWN)
                os.remove(file_path)
                return

        # Delete the kanging message
        await kanging_message.delete()

        # Inform the user that kanging is complete
        await message.reply_text(
            f"Sticker Kanged!\nSticker Emoji: {emoji}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("View Sticker Pack", url=f"t.me/addstickers/{sticker_pack_name}")]]
            )
        )

        # Clean up the downloaded file
        os.remove(file_path)
