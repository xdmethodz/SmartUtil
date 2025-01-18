import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import zipfile
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

class URLDownloader:
    """Download the webpage components based on the input URL."""
    
    def __init__(self, img_flg=True, link_flg=True, script_flg=True):
        self.soup = None
        self.img_flg = img_flg
        self.link_flg = link_flg
        self.script_flg = script_flg
        self.link_type = ('css', 'png', 'ico', 'jpg', 'jpeg', 'mov', 'ogg', 'gif', 'xml', 'js')
        self.session = requests.Session()
        
    def save_page(self, url, page_folder='page'):
        """Save the web page components based on the input URL and directory name."""
        try:
            # Ensure the URL has a scheme
            if not urlparse(url).scheme:
                url = "https://" + url

            response = self.session.get(url)
            self.soup = BeautifulSoup(response.text, "html.parser")  # Use html.parser if lxml is not available
            if not os.path.exists(page_folder):
                os.mkdir(page_folder)
                
            if self.img_flg:
                self._soup_find_and_save(url, page_folder, tag_to_find='img', inner='src')
            if self.link_flg:
                self._soup_find_and_save(url, page_folder, tag_to_find='link', inner='href')
            if self.script_flg:
                self._soup_find_and_save(url, page_folder, tag_to_find='script', inner='src')
                
            with open(os.path.join(page_folder, 'page.html'), 'wb') as file:
                file.write(self.soup.prettify('utf-8'))
                
            self._zip_folder(page_folder)
            return True
        except Exception as e:
            print(f"> save_page(): Create files failed: {str(e)}")
            return False

    def _soup_find_and_save(self, url, page_folder, tag_to_find='img', inner='src'):
        """Save specified tag_to_find objects in the page_folder."""
        page_folder = os.path.join(page_folder, tag_to_find)
        if not os.path.exists(page_folder):
            os.mkdir(page_folder)
            
        for res in self.soup.findAll(tag_to_find):
            try:
                if not res.has_attr(inner):
                    continue  # Check if inner tag (file object) exists
                
                filename = re.sub(r'\W+', '.', os.path.basename(res[inner]))
                if tag_to_find == 'link' and (not any(ext in filename for ext in self.link_type)):
                    filename += '.html'
                    
                file_url = urljoin(url, res.get(inner))
                file_path = os.path.join(page_folder, filename)
                
                res[inner] = os.path.join(os.path.basename(page_folder), filename)
                if not os.path.isfile(file_path):
                    with open(file_path, 'wb') as file:
                        file_bin = self.session.get(file_url)
                        if len(file_bin.content) > 0:
                            file.write(file_bin.content)
            except Exception as exc:
                print(exc, file=sys.stderr)
                
    def _zip_folder(self, folder_path):
        """Zip the folder."""
        zip_path = f"{folder_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=folder_path)
                    zipf.write(file_path, arcname)

async def download_web_source(client: Client, message: Message):
    # Check if the user provided a URL
    if len(message.command) <= 1:
        await message.reply_text("**❌ Provide at least one URL.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    url = message.command[1]

    # Notify the user that the source code is being downloaded
    downloading_msg = await message.reply_text("**Downloading Source Code...**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    try:
        # Download the webpage components
        downloader = URLDownloader()
        page_folder = os.path.join("downloads", urlparse(url).netloc)
        if downloader.save_page(url, page_folder):
            zip_path = f"{page_folder}.zip"

            # Send the zip file to the user
            user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
            user_profile_link = f"https://t.me/{message.from_user.username}"
            caption = (
                f"**Source code Download**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**Site:** {url}\n"
                f"**Type:** HTML, CSS, JS\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**Source Downloaded By:** [{user_full_name}]({user_profile_link})"
            )

            await client.send_document(
                chat_id=message.chat.id,
                document=zip_path,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )

            # Delete the zip file after sending
            os.remove(zip_path)

            # Delete the temporary files
            for root, dirs, files in os.walk(page_folder):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(page_folder)

    except Exception as e:
        await message.reply_text(f"**An error occurred: {str(e)}**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    finally:
        # Delete the downloading message
        await downloading_msg.delete()

def setup_ws_handler(app: Client):
    @app.on_message(filters.command("ws") & filters.private)
    async def ws_command(client: Client, message: Message):
        await download_web_source(client, message)
