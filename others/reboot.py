import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message

# Admin ID
ADMIN_ID = 7303810912

async def restart_bot(client: Client, message: Message):
    # Send initial "Bot Restarting..." message
    restarting_message = await message.reply_text("**Bot Restarting...**", parse_mode=enums.ParseMode.MARKDOWN)
    
    # Wait for 30 seconds
    await asyncio.sleep(30)
    
    # Delete the initial message and send "Bot Restarted Successfully" message
    await restarting_message.delete()
    await message.reply_text("**Bot Restarted Successfully**", parse_mode=enums.ParseMode.MARKDOWN)

def setup_reboot_handler(app: Client):
    @app.on_message(filters.command("restart") & (filters.private | filters.group))
    async def restart_command(client, message):
        if message.from_user.id == ADMIN_ID:
            await restart_bot(client, message)
        else:
            await message.reply_text("You are not authorized to use this command.")
    
    @app.on_message(filters.command("reload") & (filters.private | filters.group))
    async def reload_command(client, message):
        if message.from_user.id == ADMIN_ID:
            await restart_bot(client, message)
        else:
            await message.reply_text("You are not authorized to use this command.")

# To use the handler, call setup_reboot_handler(app) in your main script.
