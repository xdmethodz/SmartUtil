import os
import yt_dlp
from pyrogram import Client, filters, enums
import re
import math
import time
import requests
from PIL import Image
from typing import Optional

YT_COOKIES_PATH = "./cookies/cookies.txt"

async def sanitize_filename(title: str) -> str:
    """
    Sanitize file name by removing invalid characters.
    """
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.replace(' ', '_')
    return f"{title[:50]}_{int(time.time())}"

async def validate_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid YouTube link.
    """
    return url.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/'))

async def format_size(size_bytes: int) -> str:
    """
    Format file size into human-readable string.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

async def format_duration(seconds: int) -> str:
    """
    Format video duration into human-readable string.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

async def progress_bar(current, total, status_message, start_time, last_update_time):
    """
    Display a progress bar for uploads.
    """
    elapsed_time = time.time() - start_time
    percentage = (current / total) * 100
    progress = "▓" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
    speed = current / elapsed_time / 1024 / 1024  # Speed in MB/s
    uploaded = current / 1024 / 1024  # Uploaded size in MB
    total_size = total / 1024 / 1024  # Total size in MB

    # Throttle updates: Only update if at least 2 seconds have passed since the last update
    if time.time() - last_update_time[0] < 2:
        return
    last_update_time[0] = time.time()  # Update the last update time

    text = (
        f"📥 Upload Progress 📥\n\n"
        f"{progress}\n\n"
        f"🚧 Percentage: {percentage:.2f}%\n"
        f"⚡️ Speed: {speed:.2f} MB/s\n"
        f"📶 Uploaded: {uploaded:.2f} MB of {total_size:.2f} MB"
    )
    try:
        await status_message.edit(text)
    except Exception as e:
        print(f"Error updating progress: {e}")

def get_ydl_opts(output_filename: str, format: str) -> dict:
    """
    Return yt-dlp options based on the format.
    """
    if format == 'video':
        return {
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': output_filename,
            'cookiefile': YT_COOKIES_PATH,
            'quiet': True,
            'noprogress': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
        }
    elif format == 'audio':
        return {
            'format': 'bestaudio/best',
            'outtmpl': output_filename,
            'cookiefile': YT_COOKIES_PATH,
            'quiet': True,
            'noprogress': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
            ]
        }

async def download_media(url: str, format: str) -> tuple:
    """
    Download media using yt-dlp, along with its thumbnail.
    """
    if not await validate_url(url):
        return None, "Invalid YouTube URL"

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'cookiefile': YT_COOKIES_PATH}) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return None, "Could not fetch video information"

        title = info.get('title', 'Unknown Title')
        views = info.get('view_count', 0)
        duration = info.get('duration', 0)
        duration_str = await format_duration(duration)
        thumbnail_url = info.get('thumbnail', None)

        safe_title = await sanitize_filename(title)
        output_path = f"temp_media/{safe_title}.{'mp4' if format == 'video' else 'mp3'}"
        os.makedirs("temp_media", exist_ok=True)

        opts = get_ydl_opts(output_path, format)
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path):
            return None, "Download failed: File not created"

        file_size = os.path.getsize(output_path)
        if file_size > 2_000_000_000:
            os.remove(output_path)
            return None, "File exceeds Telegram's 2GB limit."

        # Download and prepare thumbnail
        thumbnail_path = None
        if thumbnail_url and format == 'video':
            thumbnail_path = await prepare_thumbnail(thumbnail_url, output_path)

        return {
            'file_path': output_path,
            'title': title,
            'views': views,
            'duration': duration_str,
            'file_size': await format_size(file_size),
            'thumbnail_path': thumbnail_path
        }, None

    except yt_dlp.utils.DownloadError as e:
        print(f"DownloadError: {e}")
        return None, "Download failed: Media unavailable or restricted"
    except Exception as e:
        print(f"Exception: {e}")
        return None, f"An unexpected error occurred: {str(e)}"

async def prepare_thumbnail(thumbnail_url: str, output_path: str) -> str:
    """
    Download and prepare the thumbnail image.
    """
    try:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            thumbnail_temp_path = f"{output_path}_thumbnail.jpg"
            with open(thumbnail_temp_path, 'wb') as f:
                f.write(response.content)

            thumbnail_resized_path = f"{output_path}_thumb.jpg"
            with Image.open(thumbnail_temp_path) as img:
                img = img.convert('RGB')
                img.thumbnail((320, 320), Image.Resampling.LANCZOS)
                background = Image.new('RGB', (320, 320), (255, 255, 255))
                offset = ((320 - img.width) // 2, (320 - img.height) // 2)
                background.paste(img, offset)
                background.save(thumbnail_resized_path, "JPEG", quality=85)

            os.remove(thumbnail_temp_path)
            return thumbnail_resized_path
    except Exception as e:
        print(f"Error preparing thumbnail: {e}")
    return None

async def handle_download_request(client, message, url, format):
    search_message = await message.reply_text("`Searching the media...`", parse_mode=enums.ParseMode.MARKDOWN)

    try:
        result, error = await download_media(url, format)
        if error:
            await search_message.edit(f"❌ {error}", parse_mode=enums.ParseMode.MARKDOWN)
            return

        await search_message.delete()
        downloading_message = await message.reply_text("`Found ☑️ Downloading...`", parse_mode=enums.ParseMode.MARKDOWN)

        media_path = result['file_path']
        title = result['title']
        views = result['views']
        duration = result['duration']
        file_size = result['file_size']
        thumbnail_path = result.get('thumbnail_path')

        if format == 'video':
            media_caption = (
                f"🎵 **Title:** `{title}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👁️‍🗨️ **Views:** `{views}` views\n"
                f"🔗 [Watch On YouTube]({url})\n"
                f"⏱️ **Duration:** `{duration}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"Downloaded By: [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )
        else:
            media_caption = (
                f"🎵 **Title:** `{title}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👁️‍🗨️ **Views:** `{views}` views\n"
                f"🔗 [Listen On YouTube]({url})\n"
                f"⏱️ **Duration:** `{duration}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"Downloaded By: [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )

        last_update_time = [0]
        start_time = time.time()

        if format == 'video':
            await client.send_video(
                chat_id=message.chat.id,
                video=media_path,
                caption=media_caption,
                parse_mode=enums.ParseMode.MARKDOWN,
                supports_streaming=True,
                thumb=thumbnail_path,
                progress=progress_bar,
                progress_args=(downloading_message, start_time, last_update_time)
            )
        else:
            await client.send_audio(
                chat_id=message.chat.id,
                audio=media_path,
                caption=media_caption,
                parse_mode=enums.ParseMode.MARKDOWN,
                progress=progress_bar,
                progress_args=(downloading_message, start_time, last_update_time)
            )

        await downloading_message.delete()

        # Cleanup
        if os.path.exists(media_path):
            os.remove(media_path)
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    except Exception as e:
        await search_message.edit(f"❌ An error occurred: {str(e)}", parse_mode=enums.ParseMode.MARKDOWN)

def setup_downloader_handler(app: Client):
    @app.on_message(filters.command(["video", "yt"]))
    async def video_command(client, message):
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) == 1:
            await message.reply_text("**Please provide your video link ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        else:
            url = command_parts[1]
            if not await validate_url(url):
                await message.reply_text("**Invalid YouTube URL ❌**", parse_mode=enums.ParseMode.MARKDOWN)
            else:
                await handle_download_request(client, message, url, 'video')

    @app.on_message(filters.command("song"))
    async def song_command(client, message):
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) == 1:
            await message.reply_text("**Please provide a Music Link ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        else:
            url = command_parts[1]
            if not await validate_url(url):
                await message.reply_text("**Invalid YouTube URL ❌**", parse_mode=enums.ParseMode.MARKDOWN)
            else:
                await handle_download_request(client, message, url, 'audio')
