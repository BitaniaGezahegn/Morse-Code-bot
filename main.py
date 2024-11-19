import json
from translate import Translator
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from typing import Final
import langdetect
import wave
from english_words import get_english_words_set
import random

#####################################Telegram###################################################
TOKEN: Final = '6414275116:AAGfTTw5fyt2YcI08ZIYznPno1pTtMs1L_c'
BOT_USERNAME: Final = '@Morse_code_all_bot'

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    message_id = update.message.message_id
    await update.message.reply_chat_action('typing', message_id)

    start_message = """Welcome to the Telegram Morse Encoding/Decoding bot!
    <a href="https://t.me/morse_code_all_bot" style="font-weight:'Bold'">
    .--.-. -- --- .-. ... . ..--.- -.-. --- -.. . ..--.- .- .-.. .-.. ..--.- -... --- -</a>

Send me a Morse code message to decode, or a message in plain text to generate a Morse code message."""
    
    await update.message.reply_html(start_message)
    # Send Something beautiful but instead if replying_text use replying_html

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    processed: str = text.lower().replace('/help ', '')
    await update.message.reply_text("Some Help Guide", parse_mode='html')


async def textToMorse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    message_id = update.message.message_id
    await update.message.reply_chat_action('typing', message_id)
    processed: str = text.lower().replace('/texttomorse ', '')
    command = '/texttomorse'
    if processed == command:
        return await update.message.reply_text("Send me your text and i will encode it for you")    
    
    morse_code = texttomorse(processed)
    await update.message.reply_text(morse_code.title(), parse_mode='html')


async def MorseToText_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = update.message.message_id
    await update.message.reply_chat_action('typing', message_id)
    text: str = update.message.text
    processed: str = text.lower().replace('/morsetotext ', '')
    
    command: str = '/morsetotext'
    if processed == command:
        return await update.message.reply_text("Send me your Morse Code and i will decode it for you")
    
    text_ = morsetotext(processed)
    await update.message.reply_text(text=text_.title(), parse_mode='html')

async def languageMorse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = update.message.message_id
    await update.message.reply_chat_action('typing', message_id)
    text: str = update.message.text
    processed: str = text.lower().replace('/languagemorse ', '')
    command = '/languagemorse'

    if processed == command:
        return await update.message.reply_text('You can send me Non English languages and I will Translate them to English and Encode them Example: /languagemorse ሞርስ ኮድ -> -- --- .-. ... . ....... -.-. --- -.. .(Morse Code) For more info send /help')
        
    en_text = toEnglish(processed)
    result = texttomorse(en_text)
    await update.message.reply_text(result, parse_mode='html')

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    await update.message.reply_chat_action("upload_voice", )
    random_word = fetch_random_word()
    unprocessed = texttomorse(random_word).removeprefix('<code>').removesuffix('</code>')
    random_morse = unprocessed.replace('-', '\-')
    processed = random_morse.replace('.', '\.')
    audio = convert_to_audio(random_morse, 1)
    await context.bot.send_audio(chat_id,
                                audio, 
                                caption=f'Word: ||{random_word}||\nMorse Code: ||{processed}||', parse_mode='MarkdownV2',
                                write_timeout=60.0,
                                read_timeout=60.0,
                                pool_timeout=60.0,
                                connect_timeout=60.0
    )


#def Chart Command
async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    processed: str = text.lower().replace('/chart ', '')
    chat_id = update.message.chat_id
    message_id = update.message.id

    if processed.lower() == 'photo' or processed.lower() == 'pic' or processed.lower() == 'picture':
        await context.bot.send_photo(chat_id, 'Photos/Tree.jpg', caption='Tree Chart')
        await context.bot.send_chat_action(chat_id, 'upload_photo')
    elif processed.lower() == 'text':
        await context.bot.send_chat_action(chat_id, 'typing')
        with open('chart.txt', 'r') as r:
            chart = r.read()
        await context.bot.send_message(chat_id=chat_id, text=chart)
    else:
        await context.bot.send_chat_action(chat_id, 'typing')
        await update.message.reply_text(
        'Choose a Chart to map Morse codes From:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Text Chart', callback_data='text-chart')],
            [InlineKeyboardButton('Picture Chart', callback_data='picture-chart')],
        ]))

async def generate_audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    message_id = update.message.message_id
    chat_id = update.message.chat_id
    await update.message.reply_chat_action('upload_audio', message_id)
    processed: str = text.lower().replace('/generateaudio ', '')

    is_morse = check_if_morse(processed)[1]

    if is_morse: #Its Morse
        path = convert_to_audio(processed, 2)
        translation = morsetotext(processed)
    else:
        morse = texttomorse(processed)
        path = convert_to_audio(morse, 2)
        translation = morse.title()
        
    await context.bot.send_audio(chat_id,
                                path, 
                                caption=translation, 
                                write_timeout=60.0,
                                read_timeout=60.0,
                                pool_timeout=60.0,
                                connect_timeout=60.0, 
                                parse_mode='html')


#Responses to Messages
def handle_response(text: str) -> str:
    processed: str = text.lower()

    result= check_if_morse(processed)[0]

    return result

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = update.message.message_id
    chat_id = update.message.chat_id
    await update.message.reply_chat_action('typing', message_id)
    text: str = update.message.text
    user_name = update.message.from_user.username
    fullname = update.message.from_user.full_name
    
    #Logic Goes Here ...
    length_of_text = len(text)
    allowed_len = 920

    if is_too_long(text):
        await update.message.reply_text(f'Your Message is too long Only {allowed_len} of characters can be Decoded at a time, your message has {length_of_text} Characters')
        return
    print(f'User: {fullname}(@{user_name}) sent: {text}')
    
    response: str = handle_response(text)

    await update.message.reply_text(response.title(), parse_mode='html')

async def callback_quiery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback = update.callback_query
    message_id = callback.message.id
    chat_id = callback.message.chat_id
    choice = callback.data
    if str(choice) == 'text-chart':
        await context.bot.send_chat_action(chat_id, 'typing')
        with open('chart.txt', 'r') as r:
            chart = r.read()
        await context.bot.send_message(chat_id=chat_id, text=chart)

    elif str(choice) == 'picture-chart':
        await context.bot.send_chat_action(chat_id, 'upload_photo')
        await context.bot.send_photo(chat_id, 'Photos/Tree.jpg', caption='Tree Chart')
    
    await context.bot.delete_message(chat_id, message_id)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Caused error: {context.error}')
    if str(context.error) == 'Timed out':
        await update.message.reply_text(f"Their was a {context.error} Error, The Bot might take a few minutes to Upload your Code, Please Send Shorter Texts")

#####################################Telegram###################################################


# Define Morse code dictionary
with open('morse_code.json', 'r') as f:
    morse_code = json.load(f)

# Takes in Mourse code and dificulty(1 or 2) and makes audio files ... and returns the path to the audio file
def convert_to_audio(MorseCode: str, difficulty: int):
    Short_Audio = 'Audios/dit.wav'
    Long_Audio = 'Audios/dash.wav'
    Silence = 'Audios/ssh.wav'

    # get the frames for the short wave
    s_obj = wave.open(Short_Audio, 'rb')
    s_signal_wave = s_obj.readframes(-1) #!Important
    s_Number_of_channels = s_obj.getnchannels()

    s_Number_of_frames = s_obj.getnframes()

    s_obj.close()

    # get the frames for the Long wave
    L_obj = wave.open(Long_Audio, 'rb')

    L_Sample_Width = L_obj.getsampwidth()
    L_Frame_Rate = L_obj.getframerate()
    L_signal_wave = L_obj.readframes(-1) #!Important

    L_obj.close()

    S_obj = wave.open(Silence, 'rb')

    S_signal_wave = S_obj.readframes(-1) #!Important

    # concatinate those frames 
    frames = [L_signal_wave, s_signal_wave, S_signal_wave]

    new_frames = []

    for code in MorseCode:
        if code == '.':
            new_frames.append(frames[1])
        elif code == '-':
            new_frames.append(frames[0])
        elif code == ' ':
            new_frames.append(frames[2])


    # save to new file
    file_path = 'Audios/morse .mp3'
    obj_new = wave.open(file_path, 'wb')
    obj_new.setnchannels(s_Number_of_channels)
    obj_new.setsampwidth(L_Sample_Width * difficulty)
    obj_new.setframerate(int(L_Frame_Rate / difficulty))
    obj_new.setnframes(s_Number_of_frames)

    obj_new.writeframes(b''.join(new_frames))

    obj_new.close()

    return file_path

def is_too_long(text: str) -> bool:
    allowed_len = 920
    length_of_text = len(text)
    if length_of_text > allowed_len:
        return True
    return False

def check_if_morse(processed: str) -> tuple:
    # it takes in a str that has been lowered
    is_morse = False
    with open('morse_code.json', 'r') as r:
        morse_ = json.load(r)
    keyboard = morse_['keyboard']

    strings: list = []

    # Checking raw text (if Morse code or text)
    for letter in processed:
        for key in keyboard:
            if letter == key:
                strings.append(letter)

    if len(strings) <= 0: # It's a string(text)
        result: str = morsetotext(processed)
        strings: list = []
        is_morse = False

    else: #Its a Morse Code
        result: str = texttomorse(processed)
        strings: list = []
        is_morse = True

    return result, not is_morse


def fetch_random_word() -> str:
    web2lowerset = get_english_words_set(['web2'], lower=True)
    words = [i for i in web2lowerset]
    return str(words[random.randrange(0, len(words))])


def splitter(morse='', text=''):
    # Split Morse code string into words
    morse_code_words = ''
    text_words = ''
    try:
        morse_code_words = morse.split(' ')
    except:
        pass
    try:
        text_words = list(text.casefold())
    except:
        pass

    return [morse_code_words, text_words]
trash = []
notEmpty = False


def morsetotext(morse):
    global trash
    global notEmpty
    if is_too_long(morse):
        return f'Your Message({len(morse)} Characters) is too long'
    if morse == '.......': #Space
        return '" "'
    elif morse == '-..-.--': #New Line
        return 'New\nLine\nCharacter'
    
    if notEmpty:
        trash = []
        notEmpty = False
    # Decode Morse code words into human readable words
    decoded_text = ""
    code = splitter(morse=morse)[0]

    for i in range(len(code)):
        morse_code_word = code[i]
        if morse_code_word in morse_code['morsetostring'][0]:
            decoded_text += morse_code['morsetostring'][0][morse_code_word]
        else:
            trash.append(morse_code_word)

    # Error message!
    if trash != []:
        notEmpty = True
        return f'Unexeptable syntax for morse:\n this characters cannot be used for morse code: {trash}\n\nDecripted Code: {decoded_text.title()}'
    return '<code>' +  decoded_text.title()  + '</code>'

text_trash = []
text_notEmpty = False


def texttomorse(text):
    global text_notEmpty
    global text_trash
    if is_too_long(text):
        return f'Your Message({len(text)} Characters) is too long'
    if text_notEmpty:
        text_trash = []
        text_notEmpty = False
    decoded_text = ""
    code = splitter(text=text)[1]

    for i in range(len(code)):
        morse_code_word = code[i]
        if morse_code_word in morse_code['stringtomorse'][0]:
            decoded_text += (morse_code['stringtomorse'][0][morse_code_word] + ' ')
        else:
            text_trash.append(morse_code_word)
            if text_trash != []:
                text_notEmpty = True
            return f'Unexeptable syntax for morse:\n this characters cannot be used for morse code: {trash}\n\nDecripted Code: <code>{decoded_text}</code>'
    return '<code>' +  decoded_text  + '</code>'

def toEnglish(text: str):
    to_lang = 'en-US'
    try:
        from_lang = langdetect.detect(text)
    except:
        from_lang = 'am-ETH'

    # Setting Default Languages
    if not to_lang:
        to_lang = 'en-us'
    if not from_lang:
        from_lang = 'am-ETH'
    try:
        trans = Translator(from_lang=from_lang, to_lang=to_lang)
        translation = trans.translate(text)
        return translation
    except:
        return text.title()

if __name__ == "__main__":

    #App
    print('Starting Program ...')
    app = Application.builder().token(TOKEN).build()
    #commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('texttomorse', textToMorse_command))
    app.add_handler(CommandHandler('Morsetotext', MorseToText_command))
    app.add_handler(CommandHandler('languagemorse', languageMorse_command))
    app.add_handler(CommandHandler('test', test_command))
    app.add_handler(CommandHandler('chart', chart_command))
    app.add_handler(CommandHandler('generateaudio', generate_audio_command))
    #MEssages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    #QUERIES
    app.add_handler(CallbackQueryHandler(callback_quiery))

    #Errors
    app.add_error_handler(error)

    #Polling
    print('Polling ...')
    app.run_polling(poll_interval=10)