from pyrogram import Client
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ParseMode

def setup_alive_handler(app: Client):
    @app.on_chat_member_updated()
    async def welcome_on_add(client: Client, chat_member_updated: ChatMemberUpdated):
        if chat_member_updated.new_chat_member is not None:
            if chat_member_updated.new_chat_member.user.is_self and chat_member_updated.new_chat_member.status == ChatMemberStatus.MEMBER:
                chat_id = chat_member_updated.chat.id
                await client.send_message(
                    chat_id,
                    "**Thank You For Adding Me In This Group👨‍💻**",
                    parse_mode=ParseMode.MARKDOWN
                )
