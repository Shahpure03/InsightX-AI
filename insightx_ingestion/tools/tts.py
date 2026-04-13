import uuid
import os
import asyncio
from gtts import gTTS

async def generate_audio(text: str, lang: str = "en") -> str:
    """Generates TTS locally and saves to /tmp/ for retrieval."""
    def _create_tts():
        os.makedirs("/tmp", exist_ok=True)
        file_path = f"/tmp/{uuid.uuid4()}.mp3"
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        return file_path
        
    try:
        # Offload blocking IO to thread
        return await asyncio.to_thread(_create_tts)
    except Exception as e:
        print(f"TTS Failed: {e}")
        return ""
