# MSFS Voice Activated Copilot
> :warning: **WORK IN PROGRESS** :warning:
>
> This project is only an experiment, and very, very much a work in progress. Please don't judge me for how messy it is, and please don't expect anything to work right at all at the moment. 


This is a project that is intended to take some of the load off a pilot in MSFS. In the real world, airliners have two pilots in the cockpit; a pilot flying (PF), and a pilot monitoring (PM). It is common for PF to instruct PM to read checklists, change flight configurations like flaps, etc. In MSFS this isn't a thing. 

This very very hacky solution uses voice recognition and text-to-speech to listen and respond to key commands and events during your flight.

The plan is ideally to have everything local and offline, including the speech-to-text and text-to-speech, but there will be an option for cloud-based STT and TTS which will be slower, but reduce memory and compute pressure on the machine it's running on.

## Features
- Voice Activated Copilot
- Fire SimConnect Events
- Set SimVars and LVars in MSFS through SimConnect
- Read SimVars and LVars in MSFS to respond to the change in aircraft config

## Config JSON - Actions
The copilot actions are defined as part of JSON files. All actions are contained in a JSON List with the key `actions`.
```json
{
    "name": "Say",
    "aircraft": "",
    "actions":
    [
        ...
    ]
}
```

### Say something
In this example, if the copilot hears the phrase "before start checklist", the copilot will go through the before start checklist so the pilot can confirm each line item.

```json
...
        {
            "phrases": [ "before start checklist" ],
            "actions": [
                { "say": "Before Start Checklist." },
                { "say": "Passenger Signs." },
                { "say": "Fuel Quantity checked."},
                ...
                { "say": "Before start checklist complete" }
            ]
        }
...
```

### Do something - Events
In this example, if the copilot hears "gear up" the copilot will put the landing gear up. This config uses the "do" action, with "event_id". This uses SimConnect Events (not Requests). See the [MSFS SDK Docs](https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Event_IDs.htm) for a list of events.

```json
...
        {
            "phrases": [ "gear up" ],
            "actions": [
                { "do": { "event_id": "GEAR_UP" }},
                { "say": "Gear up." }
            ]
        }
...
```

### Do something - SimVars and LVars
In some cases we need to set SimVars and LVars. For example, lets say we want to copilot to turn the weather radar and predictive windshear on in the Fenix A320. In the below example we can do that using the `do` action with the `var` and `value` fields.
```json
...
                { "say": "Weather radar, on" },
                { "do": { "var": "lvar:S_WR_SYS", "value": "0.0" } },
                { "say": "Predictive windshear, auto" },
                { "do": { "var": "lvar:S_WR_PRED_WS", "value": "1.0" } },
...
```

### Wait for something
In this example, when the copilot hears "flight control check", they wait for the elevators to be deflected up, then deflected down, and confirm their positions.

This is the first example to show using variables. There are certain fields that allow using variables in evaluation strings, such as this one. For more information, see [below](###variables-in-evaluation-strings).

There is also a `timeout` field (default is 15 seconds) to allow for shorter or longer maximum waiting periods. If the `timeout` is reached the rest of the actions are aborted.

```json
...
        {
            "phrases": [ "flight control check" ],
            "actions": [
                { "say": "Flight control check" },
                { "wait": { "until": "{simvar:ELEVATOR_POSITION} > 0.8"} },
                { "say": "Full up" },
                { "wait": { "until": "{simvar:ELEVATOR_POSITION} < -0.8"} },
                { "say": "Full down" }
            ]
        }
...
```

### Variables in Evaluation Strings
Certain fields in the config file allow for the use of SimVars, LVars, or config-defined variabls in their evaluation.

SimVars can be accessed with the `simvar:` prefix, such as `{simvar:ELEVATOR_POSITION}`.

LVars can be accessed with the `lvar:` prefix, such as `{lvar:N_FCU_EFIS1_BARO_HPA}`. In this example it gets the Baro QNH that is set on the captain's side of the Fenix A320.

Config defined variables are accessed with the `var:` prefix. See the second below for an explanation on those.

### Local Config Variables
Config defined variables are defined as an action as part of copilot actions, using the `variable` field. In the below example we query the simvar for total fuel quantity in weight. By default, that is in Pounds. We store that value as a local config variable `fuel_lbs`. We then use the variable to create a new variable `fuel_kg` which is the converted weight to kilos. Both `fuel_lbs` and `fuel_kg` are used in a `say` action.

```json
...
        {
            "phrases": ["tell fuel quantity"],
            "actions": [
                { 
                    "variable":
                    {
                            "name": "fuel_lbs",
                            "value": "int({simvar:FUEL_TOTAL_QUANTITY_WEIGHT})"
                    }
                },
                { 
                    "variable":
                    {
                            "name": "fuel_kg",
                            "value": "int({var:fuel_lbs} * 0.453592)"
                    }
                },
                {
                    "say": "Fuel on board, {var:fuel_lbs} pounds, {var:fuel_kg} kilograms"
                }
            ]
        },
...
```

Occasionally, there are cases where special treatment of numbers is required to make the copilot say something correctly. For example, when saying the barometric pressure in hectopascals, it's customary to say every digit. If the QNH was 1004, it would be strange for the copilot to say "QNH one thousand and four", which is what would happen if you told it to say "QNH 1004". Instead we can make a variable that splits the digits into separate numbers using a variable.

In the below example we use the `is_digit_string` field to say that all digits should be separated so the copilot is told to say "Q N H 1 0 0 4"

```json
...
        {
            "phrases": [ "say pressure" ],
            "actions": [
                {
                    "variable":
                    {
                        "name": "qnh_string",
                        "value": "int({lvar:N_FCU_EFIS1_BARO_HPA})", 
                        "is_digit_string": true 
                    }
                },
                { "say": "Q N H {var:qnh_string}." }
            ]
        }
...
```

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
- [x] Hook into MSFS using [SimConnect](https://pypi.org/project/SimConnect/) python library
    - [x] Send events to MSFS to control things like flaps, gear, etc
    - [x] Listen for events to report things like "100 knots", "v1", etc
- [ ] Read from configurable JSON files so that anyone can add configs for specific planes
    - [ ] Make it a bit less of a mess
    - [ ] Document it
- [ ] Add a launch config file
- [ ] Use appdata to store models
- [ ] Some sort of UI for user control