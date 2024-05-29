from faster_whisper import WhisperModel
import numpy as np
import speech_recognition as sr

from difflib import SequenceMatcher

from tts.copilot import createVoice

copilotTTS = createVoice()

#exit()

model_size = "small.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def action_gear_down():
    copilotTTS.say("Gear down")

def action_gear_up():
    copilotTTS.say("Gear up")

def action_flaps_0():
    copilotTTS.say("Speed checked. Flaps Zero")

def action_flaps_1():
    copilotTTS.say("Speed checked. Flaps 1")

def action_flaps_2():
    copilotTTS.say("Speed checked. Flaps 2")

def action_flaps_3():
    copilotTTS.say("Speed checked. Flaps 3")

def action_flaps_full():
    copilotTTS.say("Speed checked. Flaps full")

def action_before_start_checklist():
    copilotTTS.say("Before start checklist")
    copilotTTS.say("Cockpit Preparation")
    copilotTTS.say("Passenger Signs")
    copilotTTS.say("ADIRS")
    copilotTTS.say("Fuel Quantity")
    copilotTTS.say("Takeoff Data")
    copilotTTS.say("Baro ref")
    copilotTTS.say("Before start checklist complete");

def action_after_start_checklist():
    copilotTTS.say("After start checklist")

actions =  {
    "gear down": action_gear_down,
    "gear up": action_gear_up,
    "flaps 0": action_flaps_0,
    "flaps zero": action_flaps_0,
    "flaps 1": action_flaps_1,
    "flaps one": action_flaps_1,
    "flaps 2": action_flaps_2,
    "flaps two": action_flaps_2,
    "flaps 3": action_flaps_3,
    "flaps three": action_flaps_3,
    "flaps full": action_flaps_full,
    "flaps 4": action_flaps_full,
    "before start checklist": action_before_start_checklist,
    "after start checklist": action_after_start_checklist
}

hotwords = [
    "gear",
    "up",
    "down",
    "flaps",
    "0", "1", "2", "3", "full",
    "after", "before", "start", "checklist"
]

hotwords_string = " ".join(set(" ".join(actions.keys()).split(" ")))
print(hotwords_string)


def matchAndExecute(text : str):
    matches = { }
    for a in actions.keys():
        matches[a] = SequenceMatcher(a=a, b=text).ratio()
    matches = dict(sorted(matches.items(), key=lambda item: item[1], reverse=True))

    top_action = next(iter(matches))
    top_action_match_ratio = matches[top_action]

    if top_action_match_ratio > 0.8:
        actions[top_action]()
    else:
        print("No match found")

def recognize(audio, method : str = "whisper_local"):
    text = ""
    if method == "whisper_local":
        # Convert the recognizer audio into raw WAV data
        audio_raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
        audio_np = np.frombuffer(audio_raw, dtype=np.int16)
        audio_np = audio_np.astype(np.float32) / 32768.0

        # Use faster-whisper to transcribe the WAV
        segments, _ = model.transcribe(
            audio_np,
            hotwords=hotwords_string,
            language="en",)

        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            text = text + segment.text
    elif method == "google":
        text = recognizer.recognize_google(audio)

    return text

print("Initializing recognizer...")
recognizer = sr.Recognizer()

print(sr.Microphone.list_working_microphones())
microphone = sr.Microphone(device_index=0)

# Adjust for minumum ambient noise
print("Detecting ambient noise...")
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)
print("Set minimum energy threshold to {}".format(recognizer.energy_threshold))


def listenCallback(recognizer, audio):
    try:
        print("Processing")
        text = recognize(audio)

        print(f"Heard: {text}")
        matchAndExecute(text)

    except sr.WaitTimeoutError:
        print("Timed out")
    except sr.UnknownValueError:
        print("Couldn't understand audio")

print("Listening")

# Listen in background
stop_listening = recognizer.listen_in_background(microphone, listenCallback, phrase_time_limit=4)

while True:
    import time
    time.sleep(0.1)