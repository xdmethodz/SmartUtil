import os
import time
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from typing import Optional

SPOTIFY_CLIENT_ID = '5941bb8af55d4a52a91c5297f616e325'
SPOTIFY_CLIENT_SECRET = '408f04b237aa4dd2ba1b8bfc5da9eff8'  # Replace this with your actual Spotify client secret

# Initialize Spotipy client
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

YT_COOKIES_PATH = "./cookies/cookies.txt"

async def sanitize_filename(title: str) -> str:
    """Sanitize file name by removing invalid characters."""
    import re
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.replace(' ', '_')
    return f"{title[:50]}_{int(time.time())}"

async def format_duration(ms: int) -> str:
    """Format duration from milliseconds to human-readable string."""
    seconds = ms // 1000
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{minutes}m {seconds}s"

async def get_audio_opts(output_filename: str) -> dict:
    """Return yt-dlp options for audio download."""
    return {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_filename}.%(ext)s',
        'cookiefile': YT_COOKIES_PATH,
        'quiet': True,
        'noprogress': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

async def download_audio(url: str, output_filename: str) -> Optional[str]:
    """Download audio using yt-dlp."""
    opts = await get_audio_opts(output_filename)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        output_path = f"{output_filename}.mp3"
        if os.path.exists(output_path):
            return output_path
        return None
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

async def handle_spotify_request(client, message, url):
    if not url:
        await message.reply_text("**Please provide a track Spotify URL ❌**", parse_mode=enums.ParseMode.MARKDOWN)
        return

    status_message = await message.reply_text("`Processing your request...`", parse_mode=enums.ParseMode.MARKDOWN)

    try:
        # Extract track ID from the Spotify URL
        track_id = url.split("/")[-1]
        track = spotify.track(track_id)

        title = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        duration = await format_duration(track['duration_ms'])

        # Use YouTube search to find the track
        search_query = f"{title} {artists}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1:',
            'quiet': True,
            'cookiefile': YT_COOKIES_PATH,
            'no_warnings': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'simulate': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and info['entries']:
                yt_url = info['entries'][0]['webpage_url']
            else:
                await status_message.edit("❌ Could not find the track on YouTube.")
                return

        # Download audio using yt-dlp
        safe_title = await sanitize_filename(title)
        output_filename = f"temp_media/{safe_title}"
        os.makedirs("temp_media", exist_ok=True)
        audio_path = await download_audio(yt_url, output_filename)

        if not audio_path:
            await status_message.edit("❌ Download failed: File not created.")
            return

        await status_message.delete()

        downloading_message = await message.reply_text("`Found ☑️ Downloading...`", parse_mode=enums.ParseMode.MARKDOWN)

        audio_caption = (
            f"🎵 **Title:** `{title}`\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Artist:** `{artists}`\n"
            f"⏱️ **Duration:** `{duration}`\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Downloaded By: [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )

        last_update_time = [0]
        start_time = time.time()

        await client.send_audio(
            chat_id=message.chat.id,
            audio=audio_path,
            caption=audio_caption,
            title=title,
            performer=artists,
            parse_mode=enums.ParseMode.MARKDOWN,
            progress=progress_bar,
            progress_args=(downloading_message, start_time, last_update_time)
        )

        os.remove(audio_path)
        await downloading_message.delete()
    except Exception as e:
        await status_message.edit(f"❌ An error occurred: {str(e)}")

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

def setup_spotify_handler(app: Client):
    @app.on_message(filters.command("sp"))
    async def spotify_command(client, message):
        # Check if the message contains a Spotify URL
        command_parts = message.text.split(maxsplit=1)
        url = command_parts[1] if len(command_parts) > 1 else None
        await handle_spotify_request(client, message, url)
