from tts.engines.base import TTSEngine
import wave
from io import StringIO
import piper
import tempfile
from pygame import mixer
import os
import time
from pedalboard.io import AudioFile
from pedalboard import *
import random

class PiperTTS(TTSEngine):
    def __init__(self):
        mixer.init()

        self.voices_dir = "piper_voices/"

        # Download voices
        from piper.download import get_voices, ensure_voice_exists
        voices = get_voices(self.voices_dir, update_voices=True)

        en_voices = []
        for v in voices:
            if v.startswith("en") and v.endswith("medium"):
                en_voices.append(v)

        for v in en_voices:
            ensure_voice_exists(v, [self.voices_dir], self.voices_dir, voices)

        self.model = en_voices[random.randint(0, len(en_voices) - 1)]
        print(f"Using {self.model}")
        

        self.synthesize_args = {
            "length_scale": 0.7,
            # "noise_scale": 1.0,
            # "noise_w": 1.0,
            "sentence_silence": 0.0,
        }
        self.tts = piper.PiperVoice.load(
            model_path=self.voices_dir + self.model +".onnx",
            config_path=self.voices_dir + self.model + ".onnx.json",
            use_cuda=False)
        
        self.simulate_microphone = True
        self.board = Pedalboard([
            LadderFilter(mode=LadderFilter.Mode.BPF24, cutoff_hz=2000, drive=7.0),
            Limiter()
        ])
        
        pass

    def say(self, text : str):
        print(f"[Copilot] {text}")
        f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        f.close()
        f = f.name

        with wave.open(str(f), "wb") as wav_file:
            self.tts.synthesize(text, wav_file, **self.synthesize_args)

        if self.simulate_microphone:
            with AudioFile(f) as f_in:
                f_out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                f_out.close()
                f_out = f_out.name
                with AudioFile(f_out, "w", f_in.samplerate, 1) as o:
                    while f_in.tell() < f_in.frames:
                        chunk = f_in.read(f_in.samplerate)
                        
                        # Run the audio through our pedalboard:
                        effected = self.board(chunk, f_in.samplerate, reset=False)
                        
                        # Write the output to our output file:
                        o.write(effected)

        mixer.music.load(f_out)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)

        mixer.music.unload()

        os.unlink(f)
        if f_out is not None:
            print("Unlinking modified");
            os.unlink(f_out)

