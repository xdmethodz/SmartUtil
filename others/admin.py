import pymongo
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from collections import defaultdict
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb+srv://abirxdhackz:CHj4RmnHai0H9DuP@cluster0.xqawe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["smart_bot"]
user_activity_collection = db["user_activity"]
group_activity_collection = db["group_activity"]

# List of owner ids (add your owner ids here)
OWNERS = [7303810912, 7886711162]  # Replace with actual owner IDs

# Load user and group activity from MongoDB
USER_ACTIVITY = defaultdict(lambda: {"last_activity": None, "daily": 0, "weekly": 0, "monthly": 0, "yearly": 0})
GROUP_ACTIVITY = defaultdict(lambda: {"last_activity": None, "active": False})

for record in user_activity_collection.find():
    USER_ACTIVITY[record["_id"]] = {
        "last_activity": record["last_activity"],
        "daily": record["daily"],
        "weekly": record["weekly"],
        "monthly": record["monthly"],
        "yearly": record["yearly"],
    }

for record in group_activity_collection.find():
    GROUP_ACTIVITY[record["_id"]] = {
        "last_activity": record["last_activity"],
        "active": record["active"],
    }

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

    user_activity_collection.update_one(
        {"_id": user_id},
        {"$set": {
            "last_activity": now,
            "daily": USER_ACTIVITY[user_id]["daily"],
            "weekly": USER_ACTIVITY[user_id]["weekly"],
            "monthly": USER_ACTIVITY[user_id]["monthly"],
            "yearly": USER_ACTIVITY[user_id]["yearly"],
        }},
        upsert=True,
    )

# Function to update group activity
def update_group_activity(group_id, active=True):
    now = datetime.utcnow()
    if GROUP_ACTIVITY[group_id]["last_activity"] is None:
        GROUP_ACTIVITY[group_id]["last_activity"] = now

    GROUP_ACTIVITY[group_id]["last_activity"] = now
    GROUP_ACTIVITY[group_id]["active"] = active

    group_activity_collection.update_one(
        {"_id": group_id},
        {"$set": {
            "last_activity": now,
            "active": active,
        }},
        upsert=True,
    )

# Function to handle all commands to update user and group activity
async def command_handler(client: Client, message: Message):
    if message.chat.type == "private":
        update_user_activity(message.from_user.id)
    elif message.chat.type in ["group", "supergroup"]:
        update_group_activity(message.chat.id)

# Function to handle the /send command
async def send_handler(client: Client, message: Message):
    if message.from_user.id not in OWNERS:
        return

    if not message.reply_to_message:
        await message.reply_text("**Please reply to the message you want to broadcast 😎**", parse_mode=ParseMode.MARKDOWN)
        return

    broadcast_message = message.reply_to_message

    # Extract buttons if present
    buttons = []
    if broadcast_message.reply_markup and isinstance(broadcast_message.reply_markup, InlineKeyboardMarkup):
        buttons = broadcast_message.reply_markup.inline_keyboard
    
    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    # Send processing message
    processing_msg = await message.reply_text("**Sending Broadcast Everywhere....**", parse_mode=ParseMode.MARKDOWN)

    sent_count = 0
    blocked_count = 0

    async def send_to_chat(chat_id):
        nonlocal sent_count, blocked_count
        try:
            await client.copy_message(
                chat_id=chat_id,
                from_chat_id=broadcast_message.chat.id,
                message_id=broadcast_message.id,
                reply_markup=keyboard
            )
            sent_count += 1
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked_count += 1
            print(f"Failed to send message to {chat_id}: {e}")

    # Send to all users
    for user_id in USER_ACTIVITY.keys():
        await send_to_chat(user_id)

    # Send to all groups
    for group_id in GROUP_ACTIVITY.keys():
        await send_to_chat(group_id)

    # Delete processing message and notify completion
    await processing_msg.delete()
    await message.reply_text(f"**Sending Of Broadcast Completed ✅**\n**Message Sent To {sent_count} Out Of {len(USER_ACTIVITY) + len(GROUP_ACTIVITY)} Users And Groups**\n**Blocked {blocked_count} Users**", parse_mode=ParseMode.MARKDOWN)

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

    active_groups = sum(1 for g in GROUP_ACTIVITY.values() if g["active"])
    inactive_groups = len(GROUP_ACTIVITY) - active_groups
    total_groups = len(GROUP_ACTIVITY)

    stats_message = (
        "**Smart Bot User Status ⇾ Report ✅**\n"
        "━━━━━━━━━━━━━━━━\n"
        f"**1 Day:** {daily_users} users were active\n"
        f"**1 Week:** {weekly_users} users were active\n"
        f"**1 Month:** {monthly_users} users were active\n"
        f"**1 Year:** {yearly_users} users were active\n"
        "━━━━━━━━━━━━━━━━\n"
        f"**Total Smart Tools Users:** {total_users}\n"
        "━━━━━━━━━━━━━━━━\n"
        f"**Connected Groups:** {total_groups}\n"
        f"**Active Groups:** {active_groups}\n"
        f"**Inactive Groups:** {inactive_groups}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Update Channel", url="https://t.me/abir_x_official")]
    ])
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
    
    # Add a general handler to track all user and group activity
    app.add_handler(
        MessageHandler(command_handler, filters.all),
        group=2,  # Lower priority so it runs after command handlers
    )
