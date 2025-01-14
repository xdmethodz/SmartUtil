import os
import time
import instaloader
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from typing import Optional
import re
import traceback

# Initialize Instaloader
L = instaloader.Instaloader()

async def sanitize_filename(title: str) -> str:
    """Sanitize file name by removing invalid characters."""
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.replace(' ', '_')
    return f"{title[:50]}_{int(time.time())}"

async def validate_instagram_url(url: str) -> bool:
    """Validate if the provided URL is a valid Instagram link for reels or posts."""
    pattern = r"https://www\.instagram\.com/(reel|p)/[a-zA-Z0-9_-]+/?"
    return re.match(pattern, url) is not None

async def download_instagram_video(url: str, output_directory: str) -> Optional[str]:
    """Download Instagram video using Instaloader."""
    try:
        # Extract shortcode safely
        shortcode = url.rstrip('/').split('/')[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Download post
        L.download_post(post, target=output_directory)

        # Find downloaded .mp4 file
        for file in os.listdir(output_directory):
            if file.endswith('.mp4'):
                return os.path.join(output_directory, file)
        return None
    except Exception as e:
        print(f"Error downloading Instagram video: {e}")
        traceback.print_exc()
        return None

async def handle_instagram_request(client, message, url):
    if not url:
        await message.reply_text("**Please provide an Instagram link ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        return

    if not await validate_instagram_url(url):
        await message.reply_text("**Provide a Valid Instagram URL ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        return

    status_message = await message.reply_text("`Processing Your Request...`", parse_mode=enums.ParseMode.MARKDOWN)

    try:
        safe_title = await sanitize_filename("instagram_video")
        output_directory = f"temp_media/{safe_title}"
        os.makedirs(output_directory, exist_ok=True)

        video_path = await download_instagram_video(url, output_directory)

        if not video_path:
            await status_message.edit("❌ Download failed: File not created.")
            return

        await status_message.delete()

        downloading_message = await message.reply_text("`Found☑️ Downloading...`", parse_mode=enums.ParseMode.MARKDOWN)

        video_caption = (
            f"🎵 **Downloaded By:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )

        last_update_time = [0]
        start_time = time.time()

        await client.send_video(
            chat_id=message.chat.id,
            video=video_path,
            caption=video_caption,
            parse_mode=enums.ParseMode.MARKDOWN,
            supports_streaming=True,
            progress=progress_bar,
            progress_args=(downloading_message, start_time, last_update_time)
        )

        await downloading_message.delete()

        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_directory):
            for file in os.listdir(output_directory):
                os.remove(os.path.join(output_directory, file))
            os.rmdir(output_directory)

    except Exception as e:
        await status_message.edit(f"❌ An error occurred: {str(e)}")
        traceback.print_exc()

async def progress_bar(current, total, status_message, start_time, last_update_time):
    """Display a progress bar for uploads."""
    elapsed_time = time.time() - start_time
    percentage = (current / total) * 100
    progress = "▓" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
    speed = current / elapsed_time / 1024 / 1024  # Speed in MB/s
    uploaded = current / 1024 / 1024  # Uploaded size in MB
    total_size = total / 1024 / 1024  # Total size in MB

    # Throttle updates: Only update if at least 2 seconds have passed since the last update
    if time.time() - last_update_time[0] < 2:
        return
    last_update_time[0] = time.time()

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

def setup_instagram_handler(app: Client):
    @app.on_message(filters.command("in"))
    async def instagram_command(client, message):
        # Check if the message contains an Instagram URL
        command_parts = message.text.split(maxsplit=1)
        url = command_parts[1] if len(command_parts) > 1 else None
        await handle_instagram_request(client, message, url)
