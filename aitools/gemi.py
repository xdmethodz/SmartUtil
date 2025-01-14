import os
import io
import base64
import logging
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message
import google.generativeai as genai

# API key and model configuration
API_KEY = "AIzaSyAZRdV_C9xJj1xBwyiJgiNhkzhEVS-XoFk"
MODEL_NAME = "models/text-bison-001"  # Replace with a valid model name

# Configure the generative AI client
genai.configure(api_key=API_KEY)

async def gemi_handler(client: Client, message: Message):
    """Handles text generation requests."""
    loading_message = None
    try:
        loading_message = await message.reply_text("**Generating response, please wait...**")

        if len(message.text.strip()) <= 5:
            await message.reply_text("**Provide a prompt after the command.**")
            return

        prompt = message.text.split(maxsplit=1)[1]

        # Generate text using the AI model
        response = genai.generate_text(model=MODEL_NAME, prompt=prompt)
        response_text = response.get("candidates", [{}])[0].get("output", "No response generated.")

        # Split long responses into parts if needed
        if len(response_text) > 4000:
            parts = [response_text[i:i + 4000] for i in range(0, len(response_text), 4000)]
            for part in parts:
                await message.reply_text(part)
        else:
            await message.reply_text(response_text)

    except Exception as e:
        logging.error(f"Error during text generation: {e}")
        await message.reply_text(f"**An error occurred: {str(e)}**")
    finally:
        if loading_message:
            await loading_message.delete()

async def generate_from_image(client: Client, message: Message):
    """Handles image-based generation requests."""
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("**Please reply to a photo for a response.**")
        return

    prompt = message.command[1] if len(message.command) > 1 else message.reply_to_message.caption or "Describe this image."

    processing_message = await message.reply_text("**Processing the image and generating response ⚡️**")

    try:
        img_data = await client.download_media(message.reply_to_message, in_memory=True)
        img = Image.open(io.BytesIO(img_data.getbuffer()))

        # Encode the image to Base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        # Send prompt and image data to the model
        response = genai.generate_text(
            model=MODEL_NAME,
            prompt=f"{prompt}\nImage: {img_str}"  # Pass image info as part of the prompt
        )
        response_text = response.get("candidates", [{}])[0].get("output", "No response generated.")

        await message.reply_text(response_text)
    except Exception as e:
        logging.error(f"Error during image analysis: {e}")
        await message.reply_text("**An error occurred. Please try again.**")
    finally:
        await processing_message.delete()

def setup_gemini_handler(app: Client):
    """Sets up handlers for the AI commands."""
    app.add_handler(filters.command("gem"), gemi_handler)
    app.add_handler(filters.command("imgai"), generate_from_image)
