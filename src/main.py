
import sys

def main() -> int:
    from stt import SpeechToText
    from tts import TextToSpeech
    from audio import AudioHandler
    from sim import Sim
    import time

    from actions.actions import ActionsLibrary,ActionConfigHandler

    actionsLibray = ActionsLibrary("resources/actions/")
    current_action_config =  ActionConfigHandler(actionsLibray.current_config)

    audio = AudioHandler()

    copilotTTS = TextToSpeech.createVoice(local=False)

    sim = Sim()

    def handle_phrase_callback(text : str):
        actions = current_action_config.match_phrase(text)

        if actions is None:
            return
        
        for a in actions:
            a.perform(
                lambda text : copilotTTS.say(text, audio),
                sim
            )

    speech_to_text = SpeechToText()
    speech_to_text.initialize()
    speech_to_text.set_hotwords(current_action_config.get_hotwords())
    speech_to_text.startListening(handle_phrase_callback)

if __name__ == '__main__':
    sys.exit(main())