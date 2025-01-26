import asyncio
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import aiohttp
from pathlib import Path

# Configurations
class Config:
    TEMP_DIR = Path("./downloads")
    MAX_CONCURRENT_DOWNLOADS = 5

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("others.pin")

# Progress tracking class
class ProgressTracker:
    def __init__(self, message: Message, total_size: int):
        self.message = message
        self.total_size = total_size
        self.last_edited_msg = None
        self.current_progress = 0

    async def update_progress(self, current: int, total: int):
        percentage = (current / total) * 100
        if percentage - self.current_progress >= 10 or current == total:
            self.current_progress = percentage
            try:
                self.last_edited_msg = await self.message.edit_text(
                    f"Progress: {percentage:.2f}%"
                )
            except Exception as e:
                logger.error(f"Error updating progress message: {e}")

# PinterestDownloader class
class PinterestDownloader:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def extract_pin_id(self, url: str) -> str:
        """Extract the pin ID from a Pinterest URL."""
        if "pin/" in url:
            try:
                return url.split("pin/")[1].split("/")[0]
            except IndexError:
                return None
        return None

    async def get_pin_data(self, pin_id: str):
        """Fetch media data for the given pin ID."""
        api_url = f"https://api.pinterest.com/v1/pins/{pin_id}/"
        async with self.session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                media_url = data.get("media_url")
                media_type = data.get("media_type")
                return MediaData(url=media_url, media_type=media_type)
            else:
                return None

    async def download_file(self, url: str, file_path: Path):
        """Download a file from the provided URL to the given path."""
        async with self.session.get(url) as response:
            if response.status == 200:
                with open(file_path, "wb") as f:
                    while chunk := await response.content.read(1024):
                        f.write(chunk)
                return True
        return False

    async def cleanup(self):
        await self.session.close()

# MediaData structure
class MediaData:
    def __init__(self, url: str, media_type: str):
        self.url = url
        self.media_type = media_type

# Handle Pinterest request
async def handle_pinterest_request(client, message, url):
    async with client.download_semaphore:
        try:
            status_msg = await message.reply_text("`Processing your request...`", parse_mode=ParseMode.MARKDOWN)
            pin_id = await client.downloader.extract_pin_id(url)

            if not pin_id:
                await status_msg.edit_text('Invalid Pinterest URL. Please send a valid pin URL.')
                return

            media_data = await client.downloader.get_pin_data(pin_id)
            if not media_data:
                await status_msg.edit_text('Could not find media in this Pinterest link.')
                return

            file_path = Config.TEMP_DIR / f"temp_{message.chat.id}_{message.id}_{pin_id}"
            file_path = file_path.with_suffix('.mp4' if media_data.media_type == 'video' else '.jpg')

            success = await client.downloader.download_file(media_data.url, file_path)

            if not success:
                await status_msg.edit_text('Failed to download media. Please try again later.')
                return

            await status_msg.delete()
            downloading_message = await message.reply_text("`Found ☑️ Downloading...`", parse_mode=ParseMode.MARKDOWN)

            file_size = os.path.getsize(file_path)
            progress = ProgressTracker(message, file_size)

            try:
                if media_data.media_type == "video":
                    await message.reply_video(
                        video=str(file_path),
                        progress=progress.update_progress
                    )
                else:
                    await message.reply_photo(
                        photo=str(file_path),
                        progress=progress.update_progress
                    )

                await downloading_message.delete()
                if progress.last_edited_msg:
                    await progress.last_edited_msg.delete()

            except Exception as e:
                logger.error(f"Error sending media: {e}")
                await status_msg.edit_text('Failed to send media. Please try again later.')

            os.remove(file_path)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await message.reply_text('An error occurred while processing your request.')

# Setup Pinterest handler
def setup_pinterest_handler(app: Client):
    @app.on_message(filters.command(["pin", "pnt"]) & (filters.private | filters.group))
    async def pin_command(client, message):
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) == 1:
            await message.reply_text("**Please provide a Pinterest video link ❌**", parse_mode=ParseMode.MARKDOWN)
        else:
            url = command_parts[1]
            await handle_pinterest_request(client, message, url)

    app.downloader = PinterestDownloader()
    app.download_semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_DOWNLOADS)


