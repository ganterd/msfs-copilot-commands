from tts.engines.base import TTSEngine

class TextToSpeech():
    @staticmethod
    def createVoice(local : bool = True):
        if local:
            return TextToSpeech.createVoiceEngine("piper")
        else:
            return TextToSpeech.createVoiceEngine("edge")

    @staticmethod
    def createVoiceEngine(engine : str = "piper") -> TTSEngine:
        if engine == "text":
            from tts.engines.text import TTSTextBased
            return TTSTextBased()
        elif engine == "edge":
            from tts.engines.edge import EdgeTTS
            return EdgeTTS()
        elif engine == "piper":
            from tts.engines.piper import PiperTTS
            return PiperTTS()