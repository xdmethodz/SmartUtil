import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

def take_screenshot(url, output_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    driver.save_screenshot(output_path)
    driver.quit()

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
        await message.reply_text(f"**An error occurred: {str(e)}**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        await capturing_msg.delete()

def setup_ss_handler(app: Client):
    @app.on_message(filters.command("ss") & filters.private)
    async def ss_command(client: Client, message: Message):
        await capture_screenshot(client, message)
