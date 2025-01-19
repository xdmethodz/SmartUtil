import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

API_BASE_URL = "https://webss.yasirapi.eu.org/api"

def setup_ss_handler(app: Client):
    @app.on_message(filters.command("ss") & filters.private)
    async def capture_screenshot(client: Client, message: Message):
        # Check if a URL is provided
        if len(message.command) < 2:
            await message.reply_text("**Please Give At Least One URL**", parse_mode=ParseMode.MARKDOWN)
            return
        
        url = message.command[1]
        
        # Inform the user that the screenshot capturing process has started
        capturing_message = await message.reply_text("**⏳ Capturing Screenshot Please Wait..**", parse_mode=ParseMode.MARKDOWN)
        
        # Construct the API URL
        api_url = f"{API_BASE_URL}?url={url}&width=1280&height=720"
        
        # Capture the screenshot using the API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    # Save the screenshot to a file
                    file_name = f"screenshot_{message.from_user.id}.png"
                    with open(file_name, 'wb') as f:
                        f.write(await resp.read())
                    
                    # Send the screenshot to the user
                    await client.send_photo(message.chat.id, file_name)
                    
                    # Delete the screenshot file
                    os.remove(file_name)
                else:
                    await message.reply_text(f"Failed to capture screenshot. Status code: {resp.status}")
        
        # Delete the "Capturing Screenshot" message
        await capturing_message.delete()

# Example usage in main.py
if __name__ == '__main__':
    from ss import setup_ss_handler

    # Replace these with your actual API details
    API_ID = "YOUR_API_ID"  # Replace with your API ID
    API_HASH = "YOUR_API_HASH"  # Replace with your API Hash
    BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your Bot Token

    # Initialize the bot client
    app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    
    # Setup handlers
    setup_ss_handler(app)
    
    # Run the bot
    app.run()
