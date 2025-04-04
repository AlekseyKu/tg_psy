import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
XAI_API_KEY = os.getenv("AI_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Проверка на наличие токенов
required = [TELEGRAM_TOKEN, XAI_API_KEY, YANDEX_API_KEY, YANDEX_FOLDER_ID, OPENAI_API_KEY]
if not all(required):
    raise ValueError("❌ Отсутствуют переменные окружения в .env")

# Каталог для аудио
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)
