from tts.engines.base import TTSEngine
import pyttsx3

class PYTTSX3(TTSEngine):
    def __init__(self):
        self.tts = pyttsx3.init(driverName = "sapi5")
        voices = self.tts.getProperty('voices')
        self.tts.setProperty("voice", voices[1].id)
        pass

    def say(self, text : str):
        print(f"[Copilot] {text}")
        self.tts.say(text)
        self.tts.runAndWait()
        pass

