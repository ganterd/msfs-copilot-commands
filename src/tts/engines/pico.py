from tts.engines.base import TTSEngine
import wave
import StringIO
from picotts import PicoTTS
import simpleaudio as sa

class PicoTTS(TTSEngine):
    def __init__(self):
        self.tts = PicoTTS()
        pass

    def say(self, text : str):
        print(f"[Copilot] {text}")
        wav_data = self.tts.synth_wav(text)
        wav = wave.open(StringIO.StringIO(wav_data))
        sa.play_buffer(wav, 1, 2, 16000)

        #print(wav)
        #self.tts.tts_to_file(text=text, file_path=f"output{text}.wav")
        pass

