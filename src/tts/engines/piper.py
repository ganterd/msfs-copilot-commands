from tts.engines.base import TTSEngine
import piper
from piper import PiperVoice
from typing import Dict
import random
import numpy as np
from audio import AudioHandler

class PiperTTS(TTSEngine):
    voices_dir : str = "resources/piper_voices/"
    synthesize_args : Dict[str, object] = { "length_scale": 0.7 }
    model_name : str
    piper_voice : PiperVoice

    def __init__(self):

        # Download voices
        from piper.download import get_voices, ensure_voice_exists
        voices = get_voices(self.voices_dir, update_voices=True)

        en_voices = []
        for v in voices:
            if v.startswith("en") and v.endswith("medium"):
                en_voices.append(v)

        for v in en_voices:
            ensure_voice_exists(v, [self.voices_dir], self.voices_dir, voices)

        self.model_name = en_voices[random.randint(0, len(en_voices) - 1)]
        print(f"Using {self.model_name}")
        
        self.piper_voice = piper.PiperVoice.load(
            model_path=self.voices_dir + self.model_name +".onnx",
            config_path=self.voices_dir + self.model_name + ".onnx.json",
            use_cuda=False)
        

    def say(self, text : str, audioHandler : AudioHandler):
        print(f"[Copilot] {text}")

        voice_bytes = bytearray()            
        for b in self.piper_voice.synthesize_stream_raw(text, **self.synthesize_args):
            voice_bytes.extend(b)

        # Convert to float32
        voice_data = np.frombuffer(voice_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # Play audio
        audioHandler.play(voice_data, self.piper_voice.config.sample_rate)