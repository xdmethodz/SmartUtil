from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from collections import defaultdict
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode

# List of owner ids (add your owner ids here)
OWNERS = [7303810912, 7886711162]  # Replace with actual owner IDs

# Dictionary to track user activity
USER_ACTIVITY = defaultdict(lambda: {"last_activity": None, "daily": 0, "weekly": 0, "monthly": 0, "yearly": 0})

# Function to update user activity
def update_user_activity(user_id):
    now = datetime.utcnow()
    if USER_ACTIVITY[user_id]["last_activity"] is None:
        USER_ACTIVITY[user_id]["last_activity"] = now
    USER_ACTIVITY[user_id]["last_activity"] = now
    USER_ACTIVITY[user_id]["daily"] += 1
    USER_ACTIVITY[user_id]["weekly"] += 1
    USER_ACTIVITY[user_id]["monthly"] += 1
    USER_ACTIVITY[user_id]["yearly"] += 1

# Function to reset daily, weekly, monthly, and yearly counts
def reset_user_activity():
    now = datetime.utcnow()
    for user_id, activity in USER_ACTIVITY.items():
        if activity["last_activity"] < now - timedelta(days=1):
            activity["daily"] = 0
        if activity["last_activity"] < now - timedelta(weeks=1):
            activity["weekly"] = 0
        if activity["last_activity"] < now - timedelta(days=30):
            activity["monthly"] = 0
        if activity["last_activity"] < now - timedelta(days=365):
            activity["yearly"] = 0

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

    # Extract buttons if present
    if '\n' in broadcast_message:
        lines = broadcast_message.split('\n')
        message_text = []
        for line in lines:
            if line.startswith('(') and ')' in line and ':' in line:
                try:
                    button_name = line[line.find('(') + 1:line.find(')')].strip()
                    button_url = line[line.find(':') + 1:].strip()
                    buttons.append(InlineKeyboardButton(button_name, url=button_url))
                except Exception as e:
                    print(f"Failed to parse button: {line}. Error: {e}")
            else:
                message_text.append(line)
        message_text = "\n".join(message_text)
    else:
        message_text = broadcast_message

    # Group buttons into rows of 2
    keyboard = InlineKeyboardMarkup(
        [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    ) if buttons else None

    # Send processing message
    processing_msg = await message.reply_text("**Sending Broadcast Everywhere....**", parse_mode=ParseMode.MARKDOWN)

    sent_count = 0
    for user_id in USER_ACTIVITY.keys():
        try:
            await client.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,  # Use Markdown for formatting
                disable_web_page_preview=True  # Disable link previews
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

    # Delete processing message and notify completion
    await processing_msg.delete()
    await message.reply_text(f"**Broadcast Successfully Sent to {sent_count} users**", parse_mode=ParseMode.MARKDOWN)

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

    stats_message = f"""➠ 📊 ｢Smart Tool ⚙️ Bot Live Statistics 」 📊
━━━━━━━━━━━━━━━━
☑️1 Day: {daily_users} users were active☑️

☑️1 Week: {weekly_users} users were active☑️

☑️1 Month: {monthly_users} users were active☑️

☑️1 Year: {yearly_users} users were active☑️

━━━━━━━━━━━━━━━━
Total Users: {total_users}
━━━━━━━━━━━━━━━━

👨‍💻Developer: @abirxdhackz ☑️

👮🏻‍Support: @abir_x_official_Chat ☑️

🔄Updates: @abir_x_official ☑️

💰Server: @Smart_Nexus_Bot Hosted by @abirxdhackz. Powered by @abir_x_official ☑️

📝 Framework: Python + Program + Telethon + Aiogram Mixed ☑️

💾 Database: MongoDB ☑️

📛 Version: Latest ☑️

👑 Creator: @abirxdhackz 👨‍💻"""

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 Updates Channel ☠️", url="https://t.me/abir_x_official")]])
    await message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

def setup_admin_handlers(app: Client):
    """
    Set up command handlers for the Pyrogram bot.
    This includes specific commands like /send and /stats, as well as general activity tracking.
    """
    # Add the /send command handler for broadcasting messages
    app.add_handler(
        MessageHandler(send_handler, filters.command("send") & filters.private),
        group=1,  # High priority to ensure it executes first
    )
    
    # Add the /stats command handler for bot statistics
    app.add_handler(
        MessageHandler(stats_handler, filters.command("stats") & filters.private),
        group=1,  # High priority to ensure it executes first
    )
    
    # Add a general handler to track all user activity
    app.add_handler(
        MessageHandler(command_handler, filters.all),
        group=2,  # Lower priority so it runs after command handlers
    )
