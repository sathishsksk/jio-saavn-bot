import requests
import telebot
import json
import youtube_dl

TOKEN = '5822625873:AAEwff4upTEbA0nj9B6HSZsukp4kT4POIRc'

bot = telebot.TeleBot(TOKEN)

# Functions to do extra tasks!

# extract the title of the song (User Input)

def extract_string(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

# get the title from API

def song_fetcher(title):
    response = requests.get(f'{CONST_SONG_LINK}{title}')
    data = response.json()
    song = data["data"]["results"][0]["name"]
    return song

def artist_fetcher(title):
    response = requests.get(f'{CONST_SONG_LINK}{title}')
    data = response.json()
    artist_name = data["data"]["results"][0]["primaryArtists"]
    return artist_name

def image_fetcher(title):
    response = requests.get(f'{CONST_SONG_LINK}{title}')
    data = response.json()
    image_name = data["data"]["results"][0]["image"]
    return image_name

# downloading the song and saving as f'{title}.mp3'


def song_dl(title):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{title}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'{CONST_SONG_LINK}{title}'])


# -------------------- FUNCTION TERMINATION LINE --------------------
# API endpoint

CONST_SONG_LINK = 'https://saavn.me/search/songs?id='

# handeling /start and /help

@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Hi, I'm Alive!")

# handeling /song

@bot.message_handler(commands=['song'])
def song_request(request):
    chat_id = request.chat.id
    
    request_text = request.text
    title_input = extract_string(request_text, "/song")
    song_title = f'{CONST_SONG_LINK}{title_input}' 
    bot.send_message(chat_id, f"Getting {title_input}")
    
    try:
        title = song_fetcher(title_input)
        artist = artist_fetcher(title_input)
        image = image_fetcher(title_input)
        song_dl(title)
        file_to_send = open(f"{title}.mp3", 'rb')
        bot.send_audio(chat_id, file_to_send, caption=f'Title: {title}\n\nArtists: {artist}')

    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {str(e)}")

bot.infinity_polling()
