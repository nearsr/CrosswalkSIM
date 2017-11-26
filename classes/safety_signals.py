from classes import event as e
from classes import ped as p
from enum import Enum
from classes import input as i

#instead of storing walk light and traffic signal value
#track the states of that state diagram
#bottom is minGreenLight reqGreenLight, minGreenLightTime
#right is reqGreenLightWITHBUTTON, yellowOnExpire
#middle is "buttonReady" triggerImmediatelyOnButtonPress, yellowOnPress

#The pointer to the global event_list
#will be passed in to this variable
#from SIM when it initializes
#event_list = None
#ped_list = None

#need to be able to use these
pedNum = None
t = None
event_list = None
#from classes.event import event_list
ped_list = None
#from classes.ped import ped_list

class crosswalksignal(Enum):
    RED_WALK = 0
    YELLOW_NO_WALK = 1 
    GREEN_MANDATORY_PERIOD = 2
    GREEN_GO_YELLOW_ON_TIMER = 3
    GREEN_GO_YELLOW_ON_PRESS = 4

class safety_signals:
    def __init__(self, signal):
        self.safetySignal = crosswalksignal.GREEN_MANDATORY_PERIOD

    def change_signal(self, signal):
        self.safetySignal = signal
       
    #definitions for functions changing the safety signals
    def button_press(self, request_pushed):
        if self.safetySignal is crosswalksignal.GREEN_GO_YELLOW_ON_PRESS:
            if self.request_pushed:
                self.yellow_begins(self)
            
        elif self.safetySignal is crosswalksignal.GREEN_GO_YELLOW_ON_TIMER:
            self.yellow_begins(self)
        
        elif self.safetySignal is crosswalksignal.YELLOW_NO_WALK:
            pass

        elif self.safetySignal is crosswalksignal.RED_WALK:
            for peds in ped_list:
                m = 1
                if p.ped.can_cross( peds ) and m <= 20:
                    event_list.put( e.event( t + p.ped.exit_time( peds ), e.event_type.PED_EXIT, peds.id ) )
                    m += 1
        #return self

    def ped_at_button( self ):
        if self.safetySignal is crosswalksignal.RED_WALK:
            for peds in ped_list:
                if p.ped.can_cross( peds ):
                    event_list.put( e.event(t + p.ped.exit_time( peds ), e.event_type.PED_EXIT, peds.id ) )
        else:
            wrp = self.walk_request_pushed( pedNum ) #signal in no_walk state
            self.button_press(self, wrp)
        #return self
    
    def is_impatient(self): #ped is self here
        for peds in ped_list:
            for event in event_list:
                if event.event_type is e.event_type.PED_IMPATIENT and event.id is peds.id:
                    pass
                elif (t - peds.arrivalTime) >= 60:
                    event_list.put( e.event( t + 60, e.event_type.PED_IMPATIENT, peds.id ) )

    def ped_impatient(self):
        wrp = self.walk_request_pushed( pedNum )
        self.button_press(self, wrp)
        #return self

    def yellow_begins(self):
        self.safetySignal = crosswalksignal.YELLOW_NO_WALK
        event_list.put( e.event( t + 8, e.event_type.YELLOW_EXPIRES, pedNum) )#yellow timer = 8s
        #return self

    def yellow_expires(self):
        self.red_begins(self)
        #return self

    def red_expires(self):
        self.green_begins(self)
        #return self

    def red_begins(self):
        self.safetySignal = crosswalksignal.RED_WALK
        event_list.put( e.event( t + 18, e.event_type.RED_EXPIRES, pedNum ) )#red timer = 18s: pedestians can walk
        #return self

    def green_begins(self):
        self.safetySignal = crosswalksignal.GREEN_MANDATORY_PERIOD
        event_list.put( e.event( t + 35, e.event_type.GREEN_EXPIRES, pedNum ) )#green timer = 35s
        #return self

    def green_expires(self):
        if self.safetySignal is crosswalksignal.GREEN_MANDATORY_PERIOD:
            self.safetySignal = crosswalksignal.GREEN_GO_YELLOW_ON_PRESS
        elif self.safetySignal is crosswalksignal.GREEN_GO_YELLOW_ON_TIMER:
            pass
        #return self

    def button_prob(self, n):
        if n is 0:
            return (15/16)
        else: # n > 0
            return (1/(n+1))

    def walk_request_pushed(self, n):
        u = i.input.getNext_ButtonTracefile_UniformRand(i) #def from SIM file
        if u < self.button_prob(n):
            return True
        else:
            return False


    

