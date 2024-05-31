import os
from difflib import SequenceMatcher
from typing import List, Dict
from actions.action_config import ActionConfig,ActionEntry,CopilotAction

class ActionsLibrary:
    configs: Dict[str, ActionConfig] = {}
    current_config: ActionConfig = None

    def __init__(self, folder: str):
        self.load_configs(folder)
        self.list_configs()

    def load_configs(self, folder: str):
        self.configs = {}

        files = [f for f in os.listdir(folder)]

        if len(files) == 0:
            print(f"Warning: No config files in {folder}")
            return

        for f_path in files:
            file = open(folder + f_path)
            json = file.read()

            try:
                conf = ActionConfig.from_json(json)
                n = conf.name
                
                self.configs[n] = conf

                print(f"Loaded config: '{n}' ({f_path})")
            except Exception as e:
                print(f"Couldn't load config '{f_path}'")
                print(e)
                raise e

        if len(self.configs) == 0:
            print("Warning: No configs successfully loaded")
            return

        self.set_current_config(list(self.configs.keys())[0])

    def set_current_config(self, name: str):
        if name not in self.configs.keys():
            print(f"Error: No config named {name}")

        self.current_config = self.configs[name]
        print(f"Set current config: {name}")

    def list_configs(self):
        print("Loaded configs:")
        [print("|- " + f.name) for f in self.configs.values()]

class ActionConfigHandler:
    config: ActionConfig
    actionMap : Dict[str,ActionEntry] = {}

    def __init__(self, config: ActionConfig):
        self.config = config

        for a in self.config.actions:
            for p in a.phrases:
                self.actionMap[p] = a

    def get_hotwords(self):
        phrases = [" ".join(p) for p in [a.phrases for a in self.config.actions]]
        hotwords_string = " ".join(set(" ".join(phrases).split(" ")))
        return hotwords_string

    def match_phrase(self, phrase: str, threshold: float = 0.8) -> List[CopilotAction]:
        if phrase is None:
            return None

        matches = { }
        for a in self.actionMap.keys():
            matches[a] = SequenceMatcher(a=a, b=phrase).ratio()

        matches = dict(sorted(matches.items(), key=lambda item: item[1], reverse=True))

        top_action = next(iter(matches))
        top_action_match_ratio = matches[top_action]

        if top_action_match_ratio > threshold:
            return self.actionMap[top_action].actions
        else:
            print("No match found")
        
        return None