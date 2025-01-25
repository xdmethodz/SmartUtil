from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from datetime import datetime, timedelta
from collections import defaultdict
import pymongo

# MongoDB connection setup
MONGO_URL = "mongodb+srv://abirxdhackzinfome:BqU8yZt8JENDYkIx@cluster0.mbj0a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URL)
db = client["user_activity_db"]
user_activity_collection = db["user_activity"]

# List of owner ids (add your owner ids here)
OWNERS = [7303810912, 7886711162]  # Replace with actual owner IDs

# Function to update user activity in the MongoDB database
def update_user_activity(user_id):
    now = datetime.utcnow()
    user = user_activity_collection.find_one({"user_id": user_id})
    if not user:
        user_activity_collection.insert_one({
            "user_id": user_id,
            "last_activity": now,
            "daily": 0,
            "weekly": 0,
            "monthly": 0,
            "yearly": 0
        })
    else:
        user_activity_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_activity": now}},
            upsert=True
        )
        user_activity_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"daily": 1, "weekly": 1, "monthly": 1, "yearly": 1}},
        )

# Function to handle the /send command (works in private)
async def send_handler(client: Client, message: Message):
    if message.from_user.id not in OWNERS:
        return

    # Check if the message contains media (e.g., photo, video, document, etc.)
    if not message.command and not message.text and not message.media:
        await message.reply_text("**Please send a message or media to broadcast 😎**", parse_mode=ParseMode.MARKDOWN)
        return

    # Send processing message
    processing_msg = await message.reply_text("**Sending Broadcast Everywhere....**", parse_mode=ParseMode.MARKDOWN)

    sent_count = 0

    # Broadcast the exact copy of the owner's message to all users
    for user in user_activity_collection.find():
        try:
            await client.copy_message(
                chat_id=user["user_id"],  # User ID to send the broadcast to
                from_chat_id=message.chat.id,  # Owner's chat ID
                message_id=message.message_id  # The message ID to copy
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send message to {user['user_id']}: {e}")

    # Delete processing message and notify completion
    await processing_msg.delete()
    await message.reply_text(f"**Broadcast Successfully Sent to {sent_count} users**", parse_mode=ParseMode.MARKDOWN)

# Function to handle the /stats command (works in both private and group)
async def stats_handler(client: Client, message: Message):
    now = datetime.utcnow()
    daily_users = user_activity_collection.count_documents({"last_activity": {"$gt": now - timedelta(days=1)}})
    weekly_users = user_activity_collection.count_documents({"last_activity": {"$gt": now - timedelta(weeks=1)}})
    monthly_users = user_activity_collection.count_documents({"last_activity": {"$gt": now - timedelta(days=30)}})
    yearly_users = user_activity_collection.count_documents({"last_activity": {"$gt": now - timedelta(days=365)}})
    total_users = user_activity_collection.count_documents({})

    stats_text = (
        "**Smart Bot Status ⇾ Report ✅**\n"
        "**━━━━━━━━━━━━━━━━**\n"
        "**Name:** Smart Tool ⚙️\n"
        "**Version:** 3.0 (Beta Testing) 🛠\n\n"
        "**Development Team:**\n"
        "**- Creator:**  [⏤͟͞〲ᗩᗷiᖇ 𓊈乂ᗪ𓊉 👨‍💻](https://t.me/abirxdhackz)\n"
        "**Technical Stack:**\n"
        "**- Language:** Python 🐍\n"
        "**- Libraries:** Aiogram, Pyrogram, and Telethon 📚\n"
        "**- Database:** MongoDB Database 🗄\n"
        "**- Hosting:** Hostinger VPS 🌐\n\n"
        "**About:** Smart Tool ⚙️ The ultimate Telegram toolkit! Education, AI, downloaders, temp mail, finance tools & more—simplify life!\n\n"
        ">🔔 For Bot Update News: [Join Now](https://t.me/ModVipRM)\n"
        "**━━━━━━━━━━━━━━━━**\n"
        f"**1 Day:** {daily_users} users were active\n"
        f"**1 Week:** {weekly_users} users were active\n"
        f"**1 Month:** {monthly_users} users were active\n"
        f"**1 Year:** {yearly_users} users were active\n"
        "**━━━━━━━━━━━━━━━━**\n"
        f"**Total Smart Tools Users:** {total_users}"
    )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔔 Bot Updates", url="https://t.me/ModVipRM")]])
    await message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard, disable_web_page_preview=True)

# Function to set up the admin handlers for the bot
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
    
    # Add the /stats command handler for bot statistics (works in both private and group)
    app.add_handler(
        MessageHandler(stats_handler, filters.command("stats")),
        group=1,  # High priority to ensure it executes first
    )
    
    # Add a general handler to track all user activity
    app.add_handler(
        MessageHandler(lambda client, message: update_user_activity(message.from_user.id), filters.all),
        group=2,  # Lower priority so it runs after command handlers
    )
