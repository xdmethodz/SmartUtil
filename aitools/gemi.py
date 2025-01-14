import os
import io
import base64
import logging
import PIL.Image
from pyrogram.types import Message
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# Hardcoded API key and model name
API_KEY = "AIzaSyAZRdV_C9xJj1xBwyiJgiNhkzhEVS-XoFk"
MODEL_NAME = "gemini-1.5-flash:generateContent"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(MODEL_NAME)

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

async def generate_from_image(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("**Please reply to a photo for a response.**")
        return

    prompt = message.command[1] if len(message.command) > 1 else message.reply_to_message.caption or "Describe this image."

    processing_message = await message.reply_text("**Processing the image and generating response ⚡️**")

    try:
        img_data = await client.download_media(message.reply_to_message, in_memory=True)
        img = PIL.Image.open(io.BytesIO(img_data.getbuffer()))

        # Ensure the image is in a format supported by the model (e.g., base64 encoded string)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        response = model.generate_content([prompt, img_str])
        response_text = response.text

        await message.reply_text(response_text, parse_mode=None)
    except Exception as e:
        logging.error(f"Error during image analysis: {e}")
        await message.reply_text("**An error occurred. Please try again.**")
    finally:
        await processing_message.delete()

def setup_gemini_handler(app: Client):
    app.add_handler(filters.command("gem")(gemi_handler))
    app.add_handler(filters.command("imgai")(generate_from_image))
