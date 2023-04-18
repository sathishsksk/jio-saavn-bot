import requests
import youtube_dl
import telebot
import os

# API endpoint
CONST_SONG_LINK = 'https://saavn.me/search/songs?query='

# Telegram bot token
TOKEN = '5822625873:AAEwff4upTEbA0nj9B6HSZsukp4kT4POIRc'

# initialize the Telegram bot
bot = telebot.TeleBot(TOKEN)

# function to extract song metadata from saavn.me API
def song_fetcher(title):
    response = requests.get(f'{CONST_SONG_LINK}{title}')
    data = response.json()
    song = data["data"]["results"][0]["name"]
    artist_name = data["data"]["results"][0]["primaryArtists"]
    image_name = data["data"]["results"][0]["image"]
    return song, artist_name, image_name

# function to download the song and save it as an MP3 file
def song_dl(title):
    response = requests.get(f'{CONST_SONG_LINK}{title}')
    data = response.json()
    url = data["data"]["results"][0]["media_url"]
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
        ydl.download([url])
    return f'{title}.mp3'

# handler for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, I'm a music bot. Send me the name of a song and I'll try to find and send it to you.")

# handler for all other messages
@bot.message_handler(func=lambda message: True)
def send_song(message):
    chat_id = message.chat.id
    song_title = message.text
    
    # extract song metadata
    try:
        song, artist, image = song_fetcher(song_title)
        bot.send_message(chat_id, f"Downloading {song} by {artist}...")
        
        # download and extract audio
        song_file = song_dl(song_title)
        
        # send audio file
        with open(song_file, 'rb') as audio:
            bot.send_audio(chat_id, audio, caption=f'{song} by {artist}')
        
        # delete audio file after sending
        os.remove(song_file)
    
    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {str(e)}")

bot.polling()
