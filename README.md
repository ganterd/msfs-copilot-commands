# MSFS Voice Activated Copilot
> :warning: **WORK IN PROGRESS** :warning
>
> This project is only an experiment, and very, very much a work in progress. Please don't judge me for how messy it is, and please don't expect anything to work right at all at the moment. 


This is a project that is intended to take some of the load off a pilot in MSFS. In the real world, airliners have two pilots in the cockpit; a pilot flying (PF), and a pilot monitoring (PM). It is common for PF to instruct PM to read checklists, change flight configurations like flaps, etc. In MSFS this isn't a thing. 

This very very hacky solution uses voice recognition and text-to-speech to listen and respond to key commands and events during your flight.

The plan is ideally to have everything local and offline, including the speech-to-text and text-to-speech, but there will be an option for cloud-based STT and TTS which will be slower, but reduce memory and compute pressure on the machine it's running on.

## Tools
### Speech recognition and processing
- **[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)** - Used to listen for speech, and cloud-based transcription of the speech
- **[Faster Whisper](https://github.com/SYSTRAN/faster-whisper)** - Used to locally transcribe speech

### Text-to-Speech
- **[Edge TTS](https://pypi.org/project/edge-tts/)** - Used as a cloud-based text-to-speech generator
- **[Piper](https://github.com/rhasspy/piper)** - Used as a local text-to-speech generator.
    - **Note:** This version is built locally, because at the time of writing Piper didn't have a python-based solution for Windows, purely because it's phonemizer ([piper-phonemize](https://github.com/rhasspy/piper-phonemize)) didn't have Windows python support released. There's a hacky approach to getting it working in the `ext/` folder. Please don't judge me.

### Audio
- **[pygame](https://www.pygame.org)** - Used to play audio
- **[simpleaudio](https://pypi.org/project/simpleaudio/)** - Used to play audio in a different way
- **[pedalboard](https://github.com/spotify/pedalboard)** - Used to make the voices sound like they're coming from headset microphones

## Development
Running the dev setup script should get everything up and ready to run. `./scripts/dev_setup.ps1`

Running is as simple as `python ./src/main.py`

Building to executable can be done with `./scripts/build_to_exe.ps1`

## To Do
- [ ] Hook into MSFS using [SimConnect](https://pypi.org/project/SimConnect/) python library
    - [ ] Send events to MSFS to control things like flaps, gear, etc
    - [ ] Listen for events to report things like "100 knots", "v1", etc
- [ ] Read from configurable JSON files so that anyone can add configs for specific planes