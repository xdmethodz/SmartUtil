import os
import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from spellchecker import SpellChecker
from gtts import gTTS

# Initialize the spell checker
spell = SpellChecker()

async def check_grammar(text):
    url = "https://api.languagetool.org/v2/check"
    data = {
        'text': text,
        'language': 'en-US'
    }
    response = requests.post(url, data=data)
    result = response.json()
    corrected_text = text
    for match in result['matches']:
        offset = match['offset']
        length = match['length']
        replacement = match['replacements'][0]['value'] if match['replacements'] else ''
        corrected_text = corrected_text[:offset] + replacement + corrected_text[offset + length:]
    return corrected_text

async def grammar_check(client: Client, message):
    user_input = message.text.split(maxsplit=1)  # Split the message text
    if len(user_input) < 2:
        await message.reply_text("**Provide some text to fix Grammar..**", parse_mode=ParseMode.MARKDOWN)
    else:
        checking_message = await message.reply_text("**Checking Grammar Please Wait...**", parse_mode=ParseMode.MARKDOWN)
        corrected_text = await check_grammar(user_input[1])
        await checking_message.delete()
        await message.reply_text(f"`{corrected_text}`", parse_mode=ParseMode.MARKDOWN)

async def check_spelling(word):
    # Use Pyspellchecker to check spelling
    misspelled = spell.unknown([word])
    if misspelled:
        corrected_word = spell.correction(list(misspelled)[0])
    else:
        corrected_word = word
    return corrected_word

async def spell_check(client: Client, message):
    user_input = message.text.split(maxsplit=1)  # Split the message text
    if len(user_input) < 2:
        await message.reply_text("**Provide some text to check spelling..**", parse_mode=ParseMode.MARKDOWN)
    else:
        checking_message = await message.reply_text("**Checking Spelling Please Wait...**", parse_mode=ParseMode.MARKDOWN)
        corrected_word = await check_spelling(user_input[1])
        await checking_message.delete()
        await message.reply_text(f"`{corrected_word}`", parse_mode=ParseMode.MARKDOWN)

# Dictionary API key directly included in the script
api_key = "4097542e-560f-4c5d-8e2e-bb2d343c2dd8"

async def fetch_pronunciation_info(word):
    # Use the dictionary API with the directly included API key
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"
    response = requests.get(url)
    
    # Check if the response is successful
    if response.status_code != 200:
        return None
    
    try:
        result = response.json()
    except ValueError:
        return None

    # Parse the result to get the required information
    pronunciation_info = {
        "word": word.capitalize(),
        "breakdown": "",  # You will need to parse this from the API response
        "pronunciation": "",  # You will need to parse this from the API response
        "stems": [],  # You will need to parse this from the API response
        "definition": ""  # You will need to parse this from the API response
    }

    # Example parsing (this will depend on the actual API response structure)
    if result and isinstance(result, list) and 'meta' in result[0]:
        pronunciation_info['breakdown'] = result[0]['hwi']['hw']
        pronunciation_info['pronunciation'] = result[0]['hwi']['prs'][0]['mw']
        pronunciation_info['stems'] = result[0]['meta']['stems']
        pronunciation_info['definition'] = result[0]['shortdef'][0]

    return pronunciation_info

async def generate_pronunciation_audio(word):
    tts = gTTS(text=word, lang='en')
    audio_filename = f"Smart Tool ⚙️ {word}.mp3"
    tts.save(audio_filename)
    return audio_filename

async def pronunciation_check(client: Client, message):
    user_input = message.text.split(maxsplit=1)  # Split the message text
    if len(user_input) < 2:
        await message.reply_text("**Provide a word to check its pronunciation.**", parse_mode=ParseMode.MARKDOWN)
    else:
        word = user_input[1]
        checking_message = await message.reply_text("**Checking Pronunciation...**", parse_mode=ParseMode.MARKDOWN)

        # Fetch pronunciation information
        pronunciation_info = await fetch_pronunciation_info(word)
        
        # Handle case where pronunciation info could not be fetched
        if pronunciation_info is None:
            await checking_message.delete()
            await message.reply_text("**Could not fetch pronunciation information. Please try again later.**", parse_mode=ParseMode.MARKDOWN)
            return

        audio_filename = await generate_pronunciation_audio(word)

        caption = (f"Word: {pronunciation_info['word']}\n"
                   f"- Breakdown: {pronunciation_info['breakdown']}\n"
                   f"- Pronunciation: {pronunciation_info['pronunciation']}\n\n"
                   f"Word Stems:\n{', '.join(pronunciation_info['stems'])}\n\n"
                   f"Definition:\n{pronunciation_info['definition']}")

        # Send the audio file with caption
        await client.send_audio(
            chat_id=message.chat.id,
            audio=audio_filename,
            caption=caption
        )

        # Delete the temporary audio file
        os.remove(audio_filename)
        await checking_message.delete()

def setup_eng_handler(app: Client):
    app.add_handler(MessageHandler(grammar_check, filters.command("gra")))
    app.add_handler(MessageHandler(spell_check, filters.command("spell")))
    app.add_handler(MessageHandler(pronunciation_check, filters.command("prn")))
