import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import subprocess

# Directory to save the downloaded files temporarily
DOWNLOAD_DIRECTORY = "./downloads/"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)

async def aud_handler(client: Client, message: Message):
    # Check if the message is a reply to a video
    if not message.reply_to_message or not message.reply_to_message.video:
        await message.reply_text("**Reply to a video with the command followed by an audio file name.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    # Check if the user provided an audio file name
    if len(message.command) <= 1:
        await message.reply_text("**Reply to a video with the command followed by an audio file name.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    # Get the audio file name from the command
    audio_file_name = message.command[1]

    # Notify the user that the video is being downloaded
    downloading_msg = await message.reply_text("**Downloading Video...**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    try:
        # Download the video
        video_file_path = await message.reply_to_message.download(DOWNLOAD_DIRECTORY)

        # Delete the downloading message
        await downloading_msg.delete()

        # Notify the user that the video is being converted to audio
        converting_msg = await message.reply_text("**Converting To .mp3 ....**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        # Define the output audio file path
        audio_file_path = os.path.join(DOWNLOAD_DIRECTORY, f"{audio_file_name}.mp3")

        # Convert the video to audio using ffmpeg
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", video_file_path, 
            audio_file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"ffmpeg error: {stderr.decode()}")

        # Delete the converting message
        await converting_msg.delete()

        # Notify the user that the audio is being uploaded
        uploading_msg = await message.reply_text("**Uploading Audio...**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        # Upload the audio file to the user
        await client.send_audio(
            chat_id=message.chat.id,
            audio=audio_file_path,
            caption=f"`{audio_file_name}`",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.reply_text(f"**An error occurred: {str(e)}**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    finally:
        # Delete the temporary video and audio files
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        # Delete the uploading message
        if 'uploading_msg' in locals():
            await uploading_msg.delete()

# Function to set up handlers for the Pyrogram bot
def setup_aud_handler(app: Client):
    @app.on_message(filters.command("aud") & (filters.private | filters.group))
    async def aud_command(client: Client, message: Message):
        await aud_handler(client, message)
