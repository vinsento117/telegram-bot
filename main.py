from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import logging
import yt_dlp
import instaloader
from io import BytesIO

# Загружаем переменные окружения
load_dotenv()

# Получаем токен бота из окружения
TOKEN = os.getenv("BOT_TOKEN")


if not TOKEN:
    raise ValueError("Токен бота не найден. Проверьте файл .env или секреты!")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Функции для загрузки видео из TikTok и Instagram
def download_tiktok_video(url):
    ydl_opts = {
        "format": "bestaudio+bestaudio/best",
        "outtmpl": "video.mp4",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)
    return "video.mp4"

def download_instagram_video(url):
    loader = instaloader.Instaloader()
    try:
        loader.download_post(
            instaloader.Post.from_shortcode(loader.context, url.split("/")[-2]), 
            target="."
        )
        return "Видео успешно скачано"
    except Exception as e:
        return f"Ошибка при загрузке видео: {e}"

# Обработчики команд и сообщений
async def start(update, context):
    await update.message.reply_text("Привет! Отправь мне ссылку на TikTok или Instagram видео.")

async def handle_message(update, context):
    url = update.message.text
    if "tiktok.com" in url:
        await update.message.reply_text("Скачиваю видео из TikTok...")
        try:
            video_path = download_tiktok_video(url)
            with open(video_path, "rb") as video:
                await update.message.reply_video(video)
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {e}")
    elif "instagram.com" in url:
        await update.message.reply_text("Скачиваю видео из Instagram...")
        result = download_instagram_video(url)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Не удалось распознать ссылку. Попробуй снова.")

# Создание и запуск приложения
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
