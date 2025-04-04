import os
import logging
import requests
from datetime import datetime
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, AUDIO_DIR


def synthesize_voice_with_yandex(text: str, voice: str = "jane") -> str | None:
    try:
        url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        headers = {"Authorization": f"Api-Key {YANDEX_API_KEY}"}
        data = {
            "text": text,
            "lang": "ru-RU",
            "voice": voice,
            "emotion": "good",
            "format": "mp3",
            "folderId": YANDEX_FOLDER_ID
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            logging.error(f"Yandex TTS Error: {response.text}")
            return None

        filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        audio_path = os.path.join(AUDIO_DIR, filename)
        with open(audio_path, "wb") as f:
            f.write(response.content)

        return audio_path
    except Exception as e:
        logging.error(f"TTS synthesis error: {e}")
        return None
