import os
import logging
from pathlib import Path
from typing import Optional
import yt_dlp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    TEMP_DIR = Path("temp")
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.pinterest.com/',
    }

Config.TEMP_DIR.mkdir(exist_ok=True)

class FacebookDownloader:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        yt_dlp.utils.std_headers['User-Agent'] = Config.HEADERS['User-Agent']

    async def download_video(self, url: str) -> Optional[str]:
        self.temp_dir.mkdir(exist_ok=True)
        ydl_opts = {
            'format': 'best',
            'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'simulate': False,
            'nooverwrites': True,
        }

        try:
            loop = asyncio.get_event_loop()
            filename = await loop.run_in_executor(None, self._download_video, ydl_opts, url)
            return filename
        except Exception as e:
            logger.error(f"Facebook download error: {e}")
            return None

    def _download_video(self, ydl_opts, url):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            if os.path.exists(filename):
                return filename
            else:
                return None

def setup_dl_handlers(app: Client):
    fb_downloader = FacebookDownloader(Config.TEMP_DIR)

    @app.on_message(filters.command("fb") & (filters.private | filters.group))
    async def fb_handler(client: Client, message: Message):
        if len(message.command) <= 1:
            await message.reply_text("**Please provide a Facebook video URL after the command.**", parse_mode=ParseMode.MARKDOWN)
            return
        
        url = message.command[1]
        downloading_message = await message.reply_text("`Searching The Video`", parse_mode=ParseMode.MARKDOWN)
        
        try:
            filename = await fb_downloader.download_video(url)
            if filename:
                await downloading_message.edit_text("`Downloading Your Video ...`", parse_mode=ParseMode.MARKDOWN)
                max_telegram_size = 50 * 1024 * 1024
                
                async with aiofiles.open(filename, 'rb') as video_file:
                    file_size = os.path.getsize(filename)
                    if file_size > max_telegram_size:
                        await message.reply_document(document=video_file, caption="Large Video")
                    else:
                        await message.reply_video(video=video_file, supports_streaming=True)
                
                await downloading_message.delete()
                os.remove(filename)
            else:
                await downloading_message.edit_text("Could not download the video.")
        except Exception as e:
            logger.error(f"Error downloading Facebook video: {e}")
            await downloading_message.edit_text("An error occurred while processing your request.")

# To use the handler, call setup_dl_handlers(app) in your main script
