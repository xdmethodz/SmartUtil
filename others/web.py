import os
import re
import shutil
import aiohttp
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler

class URLDownloader:
    """Download the webpage components based on the input URL."""
    def __init__(self, img_flg=True, link_flg=True, script_flg=True):
        self.soup = None
        self.img_flg = img_flg
        self.link_flg = link_flg
        self.script_flg = script_flg
        self.link_types = ('css', 'png', 'ico', 'jpg', 'jpeg', 'mov', 'ogg', 'gif', 'xml', 'js')

    async def save_page(self, url, page_folder='page'):
        """Save the web page components based on the input URL and directory name.

        Args:
            url (str): Web URL string.
            page_folder (str, optional): Path to save the web components.

        Returns:
            bool: Whether the components were saved successfully.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html_content = await response.text()
                    self.soup = BeautifulSoup(html_content, features="lxml")

            if not os.path.exists(page_folder):
                os.mkdir(page_folder)

            if self.img_flg:
                await self._find_and_save(url, page_folder, 'img', 'src')
            if self.link_flg:
                await self._find_and_save(url, page_folder, 'link', 'href')
            if self.script_flg:
                await self._find_and_save(url, page_folder, 'script', 'src')

            with open(os.path.join(page_folder, 'page.html'), 'wb') as file:
                file.write(self.soup.prettify('utf-8'))
            return True

        except Exception as e:
            print(f"Error in save_page: {e}")
            return False

    async def _find_and_save(self, url, page_folder, tag_to_find='img', attr='src'):
        """Save specific components (e.g., images, CSS) from the page."""
        sub_folder = os.path.join(page_folder, tag_to_find)
        if not os.path.exists(sub_folder):
            os.mkdir(sub_folder)

        for tag in self.soup.findAll(tag_to_find):
            try:
                if not tag.has_attr(attr):
                    continue

                filename = re.sub(r'\W+', '.', os.path.basename(tag[attr]))
                if tag_to_find == 'link' and not any(ext in filename for ext in self.link_types):
                    filename += '.html'

                file_url = urljoin(url, tag.get(attr))
                file_path = os.path.join(sub_folder, filename)

                tag[attr] = os.path.join(os.path.basename(sub_folder), filename)

                if not os.path.isfile(file_path):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as file_response:
                            content = await file_response.read()
                            if content:
                                with open(file_path, 'wb') as file:
                                    file.write(content)
            except Exception as exc:
                print(f"Error in _find_and_save: {exc}")

async def download_url(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ **Provide at least one URL**", parse_mode=ParseMode.MARKDOWN)
        return

    url = message.command[1]
    downloading_message = await message.reply_text(
        "**Downloading Source Code.... This message will be deleted after downloading the source code**",
        parse_mode=ParseMode.MARKDOWN
    )

    downloader = URLDownloader()
    success = await downloader.save_page(url)

    await downloading_message.delete()

    if success:
        user_profile_link = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        caption = (
            f"Source code Download\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Site: {url}\n"
            f"Type: HTML, CSS, JS\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Source Downloaded By: {user_profile_link}"
        )
        file_path = "page/page.html"
        try:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=caption,
                file_name=f"Source Code - {url}",
                parse_mode=ParseMode.MARKDOWN
            )
        finally:
            shutil.rmtree("page", ignore_errors=True)
    else:
        await message.reply_text("❌ **Sorry! Failed to download source code.**", parse_mode=ParseMode.MARKDOWN)

def setup_ws_handler(app: Client):
    app.add_handler(MessageHandler(filters.command("ws") & filters.private, download_url))
