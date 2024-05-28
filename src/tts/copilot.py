
def createVoice(engine : str = "edge"):
    if engine == "text":
        from tts.engines.text import TTSTextBased
        return TTSTextBased()
    elif engine == "coqui":
        from tts.engines.coqui import TTSPyTTS
        return TTSPyTTS()
    elif engine == "pico":
        from tts.engines.pico import PicoTTS
        return PicoTTS()
    elif engine == "pyttsx":
        from tts.engines.pyttsx import PYTTSX3
        return PYTTSX3()
    elif engine == "edge":
        from tts.engines.edge import EdgeTTS
        return EdgeTTS()