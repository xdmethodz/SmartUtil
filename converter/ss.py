import os
import imgkit
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

def take_screenshot(url, output_path):
    # Configure options for imgkit
    options = {
        'format': 'png',
        'crop-w': '1920',
        'crop-h': '1080'
    }
    imgkit.from_url(url, output_path, options=options)

async def capture_screenshot(client: Client, message: Message):
    # Check if the user provided a URL
    if len(message.command) <= 1:
        await message.reply_text("**Please provide a URL after the command.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    url = message.command[1]

    # Notify the user that the screenshot is being captured
    capturing_msg = await message.reply_text("**⏳ Capturing screenshot, please wait...**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    try:
        # Capture the screenshot
        screenshot_path = os.path.join("screenshots", "screenshot.png")
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        take_screenshot(url, screenshot_path)

        # Delete the capturing message
        await capturing_msg.delete()

        # Send the screenshot to the user
        await client.send_photo(
            chat_id=message.chat.id,
            photo=screenshot_path,
            caption=f"Screenshot of {url}",
            parse_mode=ParseMode.MARKDOWN
        )

        # Delete the screenshot file after sending
        os.remove(screenshot_path)

    except Exception as e:
        error_message = "**An error occurred: {}**".format(str(e).replace('_', '\\_'))
        await message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        await capturing_msg.delete()

def setup_ss_handler(app: Client):
    @app.on_message(filters.command("ss") & filters.private)
    async def ss_command(client: Client, message: Message):
        await capture_screenshot(client, message)
