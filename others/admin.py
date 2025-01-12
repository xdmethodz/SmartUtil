from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

# List of owner ids (add your owner ids here)
OWNERS = [7303810912, 7886711162]  # Replace with actual owner IDs

# Dictionary to track user activity
USER_ACTIVITY = {}

# Function to update user activity
def update_user_activity(user_id):
    now = datetime.utcnow()
    if user_id not in USER_ACTIVITY:
        USER_ACTIVITY[user_id] = {"last_activity": now, "daily": 0, "weekly": 0, "monthly": 0, "yearly": 0}
    USER_ACTIVITY[user_id]["last_activity"] = now
    USER_ACTIVITY[user_id]["daily"] += 1
    USER_ACTIVITY[user_id]["weekly"] += 1
    USER_ACTIVITY[user_id]["monthly"] += 1
    USER_ACTIVITY[user_id]["yearly"] += 1

# Function to reset daily, weekly, monthly, and yearly counts
def reset_user_activity():
    now = datetime.utcnow()
    for user_id in USER_ACTIVITY:
        if USER_ACTIVITY[user_id]["last_activity"] < now - timedelta(days=1):
            USER_ACTIVITY[user_id]["daily"] = 0
        if USER_ACTIVITY[user_id]["last_activity"] < now - timedelta(weeks=1):
            USER_ACTIVITY[user_id]["weekly"] = 0
        if USER_ACTIVITY[user_id]["last_activity"] < now - timedelta(days=30):
            USER_ACTIVITY[user_id]["monthly"] = 0
        if USER_ACTIVITY[user_id]["last_activity"] < now - timedelta(days=365):
            USER_ACTIVITY[user_id]["yearly"] = 0

# Function to handle all commands to update user activity
async def command_handler(client: Client, message: Message):
    update_user_activity(message.from_user.id)

# Function to handle the /send command
async def send_handler(client: Client, message: Message):
    if message.from_user.id not in OWNERS:
        return

    if len(message.command) == 1:
        await message.reply_text("**Please Enter The Message To Broadcast 😎**", parse_mode=ParseMode.MARKDOWN)
        return

    broadcast_message = message.text.split(None, 1)[1]
    buttons = []

    if '\n' in broadcast_message:
        lines = broadcast_message.split('\n')
        message_text = lines[0]
        for line in lines[1:]:
            if ';' in line:
                button_name, button_url = line.split(';')
                buttons.append([InlineKeyboardButton(button_name.strip(), url=button_url.strip())])
    else:
        message_text = broadcast_message

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    processing_msg = await message.reply_text("**Sending Broadcast Everywhere....**", parse_mode=ParseMode.MARKDOWN)

    sent_count = 0
    for user_id in USER_ACTIVITY.keys():
        try:
            await client.send_message(chat_id=user_id, text=message_text, reply_markup=keyboard)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

    await processing_msg.delete()
    await message.reply_text("**Broadcast Successfully Sent**", parse_mode=ParseMode.MARKDOWN)

# Function to handle the /stats command
async def stats_handler(client: Client, message: Message):
    if message.from_user.id not in OWNERS:
        return

    now = datetime.utcnow()
    daily_users = sum(1 for u in USER_ACTIVITY.values() if u["last_activity"] > now - timedelta(days=1))
    weekly_users = sum(1 for u in USER_ACTIVITY.values() if u["last_activity"] > now - timedelta(weeks=1))
    monthly_users = sum(1 for u in USER_ACTIVITY.values() if u["last_activity"] > now - timedelta(days=30))
    yearly_users = sum(1 for u in USER_ACTIVITY.values() if u["last_activity"] > now - timedelta(days=365))
    total_users = len(USER_ACTIVITY)

    stats_message = f"""➠ 📊 ｢Bot Live Statistics 」 📊
┏
┣Smart Nexus Bot Status ⇾ Report ✅
━━━━━━━━━━━━━━━━
1 Day: {daily_users} users were active
1 Week: {weekly_users} users were active
1 Month: {monthly_users} users were active
1 Year: {yearly_users} users were active
━━━━━━━━━━━━━━━━
Total Smart Tools Users: {total_users}
┗━━━━━━━━━━━━━━━━━━━
👨‍💻Developer: @abirxdhackz ☑️
🔄Support: @abir_x_official_Chat ☑️
🔄Updates: @abir_x_official ☑️
🖥Server: The server for hosting  ☑️ @Smart_Nexus_Bot ✨ - Toolkit is provided by @abirxdhack. Powered by @abir_x_official ☑️
📝 Language & 🧰 Framework: Python Pyrogram Aiogram Telethon Mixed  ☑️                                                                 
💾 Databases: MongoDB ☑️
📛 ᴠᴇʀꜱɪᴏɴ : Latest ☑️
🟢 ʟᴀꜱᴛ ᴜʙᴅᴀᴛᴇ 12 Jan ,2025 ☑️
👑 ʙᴏᴛ ᴄʀᴇᴀᴛᴏʀ : @abirxdhackz 👨‍💻
❤️ ᴊᴏɪɴ ᴏᴜʀ ᴄᴏᴅɪɴɢ ᴄʜᴀɴɴᴇʟ ꜰᴏʀ ᴍᴏʀᴇ ʙᴏᴛꜱ : @abir_x_official ☑️"""

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻UpdatesChannel☑️", url="https://t.me/abir_x_official")]])

    await message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

def setup_admin_handlers(app: Client):
    """Set up command handlers for the Pyrogram bot."""
    app.add_handler(filters.command("send") & filters.private, send_handler)
    app.add_handler(filters.command("stats") & filters.private, stats_handler)
    app.add_handler(filters.all, command_handler)  # Update user activity for all commands

