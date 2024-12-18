from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv, dotenv_values 

import yt_dlp
import os

# loading variables from .env file
load_dotenv() 
# Token API Telegram
TOKEN = os.getenv("BOT_TOKEN")
print(TOKEN)
# Direktori penyimpanan sementara file yang diunduh
DOWNLOAD_DIR = "downloads/"

# Fungsi untuk memulai bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Halo! Kirimkan tautan YouTube yang ingin Anda unduh dalam format MP3.\n\nbot by CocoBoy")

# Fungsi untuk menangani pesan dengan tautan YouTube
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    if "youtube.com" in message or "youtu.be" in message:
        # Kirim opsi ke pengguna untuk memilih format MP3
        keyboard = [
            [
                InlineKeyboardButton("Unduh MP3", callback_data=f"mp3|{message}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Pilih format unduhan MP3:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Tolong kirim tautan YouTube yang valid.")

# Fungsi untuk menangani unduhan berdasarkan pilihan pengguna
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    choice, url = query.data.split("|")

    # Beritahu pengguna bahwa unduhan sedang diproses
    await query.edit_message_text(text="Mengunduh...")

    # Proses unduhan
    try:
        # Pastikan folder unduhan ada
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        if choice == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            file_extension = "mp3"  # Ekstensi file akhir

            # Unduh menggunakan yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                temp_file_path = ydl.prepare_filename(info)
                file_path = temp_file_path.replace(".webm", ".mp3")

            # Kirim file ke pengguna
            await query.message.reply_text(f"Mengirim file {file_extension}...")
            await query.message.reply_document(document=open(file_path, "rb"))

            # Hapus file setelah dikirim
            os.remove(file_path)

    except Exception as e:
        await query.message.reply_text(f"Terjadi kesalahan: {e}")

# Fungsi utama
def main():
    application = Application.builder().token(TOKEN).build()

    # Tambahkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Jalankan bot
    application.run_polling()

if __name__ == "__main__":
    main()
