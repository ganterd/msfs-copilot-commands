from tts.engines.base import TTSEngine

class TTSTextBased(TTSEngine):
    def __init__(self) -> None:
        super().__init__()

    def say(self, text : str):
        print(f"[Copilot] {text}")