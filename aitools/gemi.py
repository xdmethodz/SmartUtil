import requests
import json
from pyrogram import Client, filters, enums
from pyrogram.types import Message

# Define the API URL and your API Key
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
API_KEY = "AIzaSyAZRdV_C9xJj1xBwyiJgiNhkzhEVS-XoFk"  # Replace with your actual API key

async def fetch_gemini_response(prompt: str) -> str:
    """Fetch response from Gemini API."""
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            return result['contents'][0]['parts'][0]['text']
        except (IndexError, KeyError) as e:
            return f"Error parsing response: {e}\nResponse content: {json.dumps(result, indent=4)}"
    else:
        return f"Error: {response.status_code}\n{response.text}"

async def handle_gemini_request(client, message, prompt):
    if not prompt:
        await message.reply_text("**Please provide a prompt for gemini response ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    status_message = await message.reply_text("**Generating gemini response ⚡️**", parse_mode=enums.ParseMode.MARKDOWN)
    
    try:
        response_text = await fetch_gemini_response(prompt)
        await status_message.delete()
        await message.reply_text(response_text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await status_message.edit(f"❌ An error occurred: {str(e)}", parse_mode=enums.ParseMode.MARKDOWN)

async def handle_gemini_image_request(client, message, prompt):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("**Please reply to a photo for response ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    status_message = await message.reply_text("**Processing the image and generating response ⚡️**", parse_mode=enums.ParseMode.MARKDOWN)
    
    try:
        # Here you would include logic to handle image-specific processing if needed
        # For now, we'll simply send the prompt to the API as usual
        response_text = await fetch_gemini_response(prompt)
        await status_message.delete()
        await message.reply_text(response_text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await status_message.edit(f"❌ An error occurred: {str(e)}", parse_mode=enums.ParseMode.MARKDOWN)

def setup_gemini_handler(app: Client):
    @app.on_message(filters.command("gemi"))
    async def gemini_command(client, message):
        command_parts = message.text.split(maxsplit=1)
        prompt = command_parts[1] if len(command_parts) > 1 else None
        await handle_gemini_request(client, message, prompt)

    @app.on_message(filters.command("imgai"))
    async def gemini_image_command(client, message):
        command_parts = message.text.split(maxsplit=1)
        prompt = command_parts[1] if len(command_parts) > 1 else ""
        await handle_gemini_image_request(client, message, prompt)
