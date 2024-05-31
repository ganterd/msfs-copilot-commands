from faster_whisper import WhisperModel
import numpy as np
import speech_recognition as sr

class SpeechProcessor:
    hotwords : str

    def __init__(self):
        pass

    def process_audio(self, audio) -> str:
        pass

    def set_hotwords(self, hotwords : str):
        self.hotwords = hotwords

class GoogleSpeechProcessor(SpeechProcessor):
    recognizer : sr.Recognizer

    def __init__(self, recognizer):
        self.recognizer = recognizer

    def process_audio(self, audio) -> str:
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None

class FasterWhisperSpeechProcessor(SpeechProcessor):
    model_size : str
    whisper_model : WhisperModel

    def __init__(self, model : str = "small_en"):
        model_size = "small.en"
        self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def process_audio(self, audio) -> str:
        # Convert the recognizer audio into raw WAV data
        audio_raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
        audio_np = np.frombuffer(audio_raw, dtype=np.int16)
        audio_np = audio_np.astype(np.float32) / 32768.0

        # Use faster-whisper to transcribe the WAV
        if self.hotwords is not None:
            print("Using hotwords")
            segments, _ = self.whisper_model.transcribe(audio_np, hotwords=self.hotwords, language="en")
        else:
            segments, _ = self.whisper_model.transcribe(audio_np, language="en")

        return " ".join([s.text for s in segments])

class SpeechToText:
    recognizer : sr.Recognizer
    microphone : sr.Microphone
    audioProcessor : SpeechProcessor

    def initialize(
            self):
        print("Initializing recognizer...")
        self.recognizer = sr.Recognizer()

        print(sr.Microphone.list_working_microphones())
        self.microphone = sr.Microphone(device_index=0)

        #self.audioProcessor = FasterWhisperSpeechProcessor()
        self.audioProcessor = GoogleSpeechProcessor(self.recognizer)

        # Adjust for minumum ambient noise
        print("Detecting ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Set minimum energy threshold to {}".format(self.recognizer.energy_threshold))

    def set_hotwords(self, hotwords : str):
        self.audioProcessor.set_hotwords(hotwords)

    def listenCallback(self, _, audio):
        try:
            print("Processing")
            text = self.audioProcessor.process_audio(audio)

            self.handle_phrase_callback(text)

        except sr.WaitTimeoutError:
            print("Timed out")

    def startListening(self, handle_phrase_callback):
        self.handle_phrase_callback = handle_phrase_callback

        print("Listening")

        # Listen in background
        stop_listening = self.recognizer.listen_in_background(
            self.microphone,
            lambda _, audio : self.listenCallback(_, audio),
            phrase_time_limit=4)

        while True:
            import time
            time.sleep(0.1)