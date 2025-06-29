from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1
import os

# Your BotFather token
TOKEN = "7600108943:AAEWuOAHUn-JA9KQRpQlEMmK8nRW3U9O3so"
CHANNEL_ID = "-1002030719632"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube link to extract audio with artwork!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        # Download audio and thumbnail
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'writethumbnail': True,
            'retries': 3,
            'socket_timeout': 30,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', 'Unknown Artist')

        # Add metadata and artwork
        audio = MP3('audio.mp3', ID3=ID3)
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        if os.path.exists('audio.jpg'):
            with open('audio.jpg', 'rb') as img:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, data=img.read()))
        audio.save()

        # Send to channel
        await context.bot.send_audio(
            chat_id=CHANNEL_ID,
            audio=open('audio.mp3', 'rb'),
            title=title,
            performer=artist
        )

        # Clean up files
        os.remove('audio.mp3')
        if os.path.exists('audio.jpg'):
            os.remove('audio.jpg')

        await update.message.reply_text("Audio sent to the channel with artwork!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
