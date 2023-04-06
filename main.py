import threading

class Elevator(Resource):
    directionString = ["stationary", "up", "down"]
    def __init__(self, lowest, highest, current):
        """Initialize the Elevator instance with the lowest and highest possible floors as well as the current floor."""
        self.bay        = bay
        self.lowest     = lowest
        self.highest    = highest
        self.current    = current
        self.capacity   = capacity
        self.travelling = false
        self.direction  = 0         # 1 (up), -1 (down)
        self.stops      = []
        self.arrivalTime= None
        self._lock      = threading.Lock()

    def __str__(self):
        """Return string for printing current postion"""
        with self._lock:
            if self.travelling:
                return "Elevator is travelling {direction} and is currently travelling from floor {cfloor} to {nfloor}.".format(direction = self.getString(), cfloor = self.current, nfloor = (self.current + self.direction))
            else:
                return "Elevator is currently waiting on floor {cfloor}".format(cfloor = self.current)

    def addStop(self, floor):
        if self.lowest <= floor <= self.highest:
            with self._lock:
                self.stops.append(floor)
                return True
        return False
            
    
