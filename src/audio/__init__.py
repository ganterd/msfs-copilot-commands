import numpy
import pyaudio
from pedalboard import *

class AudioHandler:
    simulate_microphone : bool = True
    board : Pedalboard
    resample : Pedalboard
    stream : pyaudio.Stream
    p : pyaudio
    sample_rate : int

    def __init__(self, sample_rate : int = 22050, sample_width : int = 2):
        self.sample_rate = sample_rate
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(sample_width),
            channels=1,
            rate=sample_rate,
            output=True)
        
        self.simulate_microphone = True
        self.board = Pedalboard([
            LadderFilter(mode=LadderFilter.Mode.BPF24, cutoff_hz=2000, drive=7.0),
            Limiter()
        ])

        self.resample = Pedalboard([
            Resample(sample_rate)
        ])

    def play(self, audio : numpy.ndarray, sample_rate : int):
        if sample_rate != self.sample_rate:
            audio = self.resample(audio, sample_rate)

        if self.simulate_microphone:
            audio = self.board(audio, sample_rate)

        processed = (audio * 32768.0).astype(numpy.int16)
        
        self.stream.write(processed.tobytes())
