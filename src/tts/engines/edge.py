from tts.engines.base import TTSEngine
import edge_tts
import asyncio
import tempfile
import random
from pygame import mixer
import time
import os
from pedalboard.io import AudioFile
from pedalboard import *

class EdgeTTS(TTSEngine):
    def __init__(self) -> None:
        super().__init__()
        mixer.init()
        voices = asyncio.run(edge_tts.list_voices())
        en_voices = []
        for v in voices:
            print(f"{v['ShortName']}")
            if v['ShortName'].startswith("en"):
                en_voices.append(v)



        v = en_voices[random.randint(0, len(en_voices) - 1)]
        self.voice = v['ShortName']
        print(v)

        self.simulate_microphone = True
        self.board = Pedalboard([
            LadderFilter(mode=LadderFilter.Mode.BPF24, cutoff_hz=3000, drive=7.0),
            Limiter()
        ])

        self.say(f"Co-pilot started, I am {v['Name']}")


    def say(self, text : str):
        print(f"[Copilot] {text}")
        f = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        f.close()
        f = f.name
        print(f"tmp: {f}")
        
        asyncio.run(self.sayAsync(text, f))

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
                #os.unlink(f_out)

        mixer.music.load(f_out)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)

        mixer.music.unload()

        os.unlink(f)
        if f_out is not None:
            print("Unlinking modified");
            os.unlink(f_out)

    async def sayAsync(self, text : str, output : str):
        comm = edge_tts.Communicate(text, self.voice, rate="+40%")
        await comm.save(output)