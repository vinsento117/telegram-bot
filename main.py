from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import logging
import yt_dlp
import instaloader
from io import BytesIO

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из .env
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен бота не найден. Проверьте файл .env или секреты!")

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Функции для загрузки видео из TikTok и Instagram
def download_tiktok_video(url):
    ydl_opts = {"format": "bestvideo+bestaudio/best", "outtmpl": "video.mp4", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)
    return "video.mp4"

def download_instagram_video(url):
    loader = instaloader.Instaloader()
    try:
        post = instaloader.Post.from_url(loader.context, url)
        return post.url
    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        return None

async def start(update, context):
    await update.message.reply_text("Привет! Отправь ссылку на видео из TikTok или Instagram.")

async def handle_message(update, context):
    url = update.message.text
    if "tiktok.com" in url:
        try:
            video_path = download_tiktok_video(url)
            with open(video_path, "rb") as video:
                await update.message.reply_video(video)
            os.remove(video_path)
        except Exception as e:
            await update.message.reply_text(f"Ошибка загрузки из TikTok: {e}")
    elif "instagram.com" in url:
        try:
            video_url = download_instagram_video(url)
            if video_url:
                await update.message.reply_text(f"Видео доступно по ссылке: {video_url}")
            else:
                await update.message.reply_text("Не удалось скачать видео с Instagram.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка загрузки из Instagram: {e}")
    else:
        await update.message.reply_text("Отправь ссылку на видео из TikTok или Instagram.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
