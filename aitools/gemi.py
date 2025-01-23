# setup_gem_handler.py

import os
import io
import logging
import PIL.Image
from pyrogram.types import Message
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# Configuration for Google Generative AI
GOOGLE_API_KEY = "AIzaSyAZRdV_C9xJj1xBwyiJgiNhkzhEVS-XoFk"  # Replace this Google Api Key
MODEL_NAME = "gemini-1.5-flash"  # Don't Change this model

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def setup_gem_handler(app: Client):

    @app.on_message(filters.command("gem") & (filters.private | filters.group))
    async def gemi_handler(client: Client, message: Message):
        loading_message = None
        try:
            loading_message = await message.reply_text("**Generating response, please wait...**")

            if len(message.text.strip()) <= 5:
                await message.reply_text("**Provide a prompt after the command.**")
                return

            prompt = message.text.split(maxsplit=1)[1]
            response = model.generate_content(prompt)

            response_text = response.text
            if len(response_text) > 4000:
                parts = [response_text[i:i + 4000] for i in range(0, len(response_text), 4000)]
                for part in parts:
                    await message.reply_text(part)
            else:
                await message.reply_text(response_text)

        except Exception as e:
            await message.reply_text(f"**An error occurred: {str(e)}**")
        finally:
            if loading_message:
                await loading_message.delete()

    @app.on_message(filters.command("imgai") & (filters.private | filters.group))
    async def generate_from_image(client: Client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply_text("**Please reply to a photo for a response.**")
            return

        prompt = message.command[1] if len(message.command) > 1 else message.reply_to_message.caption or "Describe this image."

        processing_message = await message.reply_text("**Processing the image and generating response ⚡️**")

        try:
            img_data = await client.download_media(message.reply_to_message, in_memory=True)
            img = PIL.Image.open(io.BytesIO(img_data.getbuffer()))

            response = model.generate_content([prompt, img])
            response_text = response.text

            await message.reply_text(response_text, parse_mode=None)
        except Exception as e:
            logging.error(f"Error during image analysis: {e}")
            await message.reply_text("**An error occurred. Please try again.**")
        finally:
            await processing_message.delete()
