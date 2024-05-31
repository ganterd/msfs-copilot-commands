from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Dict, Optional
import time
from sim import Sim
from tts.engines.base import TTSEngine
from string import Formatter
import re

variable_store = {}

def parse_string_for_vars(text : str):
    keys = re.findall(r'\{([^}]*)\}', text)

    simvars = [k.removeprefix("simvar:") for k in keys if k.startswith("simvar:")]
    lvars = [k.removeprefix("lvar:") for k in keys if k.startswith("lvar:")]
    _vars = [k.removeprefix("var:") for k in keys if k.startswith("var:")]

    return (simvars, lvars, _vars)

def replace_vars_in_text(text : str, sim : Sim, local_var_store : Dict):
    (simvars, lvars, local_vars) = parse_string_for_vars(text)

    for v in simvars:
        val = sim.aq.find(v).value
        text = text.replace("{simvar:" + v + "}", str(val))
    for v in lvars:
        val = sim.find_lvar(v).value
        text = text.replace("{lvar:" + v + "}", str(val))
    for v in local_vars:
        val = local_var_store.get(v)
        text = text.replace("{var:" + v + "}", str(val))

    return text    

@dataclass_json
@dataclass
class TriggerEventAction:
    event_id: Optional['str'] = None
    var: Optional['str'] = None
    value: Optional['str'] = None

    def perform(self, sim : Sim, local_var_store : Dict):
        if self.event_id is not None:
            sim.fireEvent(self.id)

        if self.var is not None:
            eval_text = replace_vars_in_text(self.value, sim, local_var_store)
            val = eval(eval_text)

            if self.var.startswith("var:"):
                key = self.var.removeprefix("var:")
                local_var_store[key] = val
            else:    
                if self.var.startswith("simvar:"):
                    key = self.var.removeprefix("simvar:")
                    v = sim.aq.find(key)
                    if v is None:
                        print(f"Couldn't find SimVar {key}")
                elif self.var.startswith("lvar:"):
                    key = self.var.removeprefix("lvar:")
                    v = sim.find_lvar(key)
                    if v is None:
                        print(f"Couldn't find LVar {key}")

                v.value = val

@dataclass_json
@dataclass
class VariableAction:
    name: str
    value: str
    
    is_digit_string: bool = False
    is_freq_string: bool = False

    def process(self, sim : Sim, var_store : Dict):
        eval_text = replace_vars_in_text(self.value, sim, var_store)
        v = eval(eval_text)

        if self.is_digit_string:
            v = ' '.join([c for c in str(v)])

        var_store[self.name] = v
        print(var_store)
            


@dataclass_json
@dataclass
class SayAction:
    text: str

@dataclass_json
@dataclass
class WaitCondition:
    until: str
    timeout: Optional['float'] = 10.0

    def perform(self, sim : Sim, local_var_store : Dict) -> bool:
        t = time.time()
        while time.time() - t < self.timeout:

            eval_string = replace_vars_in_text(self.until, sim, local_var_store)

            if eval(eval_string) == True:
                return True
            
            time.sleep(0.1)

        print(f"Timed out waiting for {self.var} to pass '{self.until}")

        return False

@dataclass_json
@dataclass
class ConditionalActions:
    cond: Optional['str'] = None

    if_true: Optional['List[CopilotAction]'] = None
    if_false: Optional['List[CopilotAction]'] = None

    def perform(self, say_callback, sim : Sim, local_var_store : Dict) -> bool:

        eval_string = replace_vars_in_text(self.cond, sim, local_var_store)
        print(f"Conditional: {eval_string}")

        if eval(eval_string) is True:
            if self.if_true is not None:
                [a.perform(say_callback, sim) for a in self.if_true]
        else:
            if self.if_false is not None:
                [a.perform(say_callback, sim) for a in self.if_false ]

@dataclass_json
@dataclass
class CopilotAction:
    say: Optional['str'] = None
    do: Optional['TriggerEventAction'] = None
    wait: Optional['WaitCondition'] = None
    conditional: ConditionalActions = None
    variable: Optional['VariableAction'] = None

    def perform(self, say_callback, sim : Sim):
        if self.say is not None:
            say_callback(replace_vars_in_text(self.say, sim, variable_store))
        if self.do is not None:
            self.do.perform(sim, variable_store)
        if self.wait is not None:
            if self.wait.perform(sim=sim,local_var_store=variable_store) == False:
                return
        if self.conditional is not None:
            self.conditional.perform(say_callback, sim, local_var_store=variable_store)
        if self.variable is not None:
            self.variable.process(sim=sim,var_store=variable_store)

@dataclass_json
@dataclass
class ActionEntry:
    phrases: List[str]
    actions: List[CopilotAction]


@dataclass_json
@dataclass
class ActionConfig:
    name: str
    aircraft: str
    actions: List[ActionEntry]