from SimConnect import *
from SimConnect.RequestList import RequestHelper

class LVarHelper(RequestHelper):
    list = {}

    def addLvar(self, lvar):
        self.list[lvar] = [
            "Custom lvar",
            lvar.encode('utf-8'),
            b"Number", # LVars are always numbers (float64)
            "Y" # Settable
        ]


class Sim():
    sm : SimConnect
    aq : AircraftRequests
    ae : AircraftEvents
    lv : LVarHelper

    def __init__(self):
        self.sm = SimConnect()
        self.ae = AircraftEvents(self.sm)
        self.aq = AircraftRequests(self.sm)
        self.lv = LVarHelper(self.sm)
        self.aq.list.append(self.lv)

    def fireEvent(self, event_id):
        e = self.ae.find(event_id)
        self.ae.list

        if e is None:
            print(f"Event {event_id} was not found")
            return
        
        e()

    def find_lvar(self, key):
        """ Modified version of AircraftRequests.find() that removes index stripping """
        index = None

        key = "L:" + key
        if not key in self.lv.list:
            self.lv.addLvar(key)

        for clas in self.aq.list:
            if key in clas.list:
                rqest = getattr(clas, key)
                if index is not None:
                    rqest.setIndex(index)
                return rqest
        return None



from SimConnect.Constants import *
from SimConnect.Enum import *

if __name__ == '__main__':
    import time
    
    from actions.action_config import parse_string_for_vars

    sim = Sim()
    f = LVarHelper(sim.sm)
    sim.aq.list.append(f)

    fuel = sim.aq.find("FUEL_TOTAL_QUANTITY")
    print(fuel.value)

    wr_sys = sim.find_lvar('S_MIP_AUTOBRAKE_MAX')
    wr_sys.value += 2

    time.sleep(1)
    wr_sys.value += 2