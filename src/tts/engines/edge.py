from tts.engines.base import TTSEngine
import edge_tts
import asyncio
import tempfile
import random
from pygame import mixer
import time
import os
from pedalboard.io import AudioFile
import numpy
from audio import AudioHandler

class EdgeTTS(TTSEngine):
    def __init__(self) -> None:
        super().__init__()
        voices = asyncio.run(edge_tts.list_voices())
        en_voices = []
        for v in voices:
            if v['ShortName'].startswith("en"):
                en_voices.append(v)

        v = en_voices[random.randint(0, len(en_voices) - 1)]
        self.voice = v['ShortName']

    def say(self, text : str, audioHandler : AudioHandler):
        print(f"[Copilot] {text}")
        
        f = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        f.close()
        f = f.name

        asyncio.run(self._sayAsync(text, f))

        with AudioFile(f) as tmp_mp3:
            audio = tmp_mp3.read(int(tmp_mp3.samplerate * tmp_mp3.duration))
            audioHandler.play(audio, tmp_mp3.samplerate)

        os.unlink(f)

    async def _sayAsync(self, text : str, output : str):
        comm = edge_tts.Communicate(text, self.voice, rate="+40%")
        await comm.save(output)