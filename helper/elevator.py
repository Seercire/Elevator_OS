import threading


class Elevator(Resource):
  directionString = ["stationary", "up", "down"]

  def __init__(self, bay, lowestFloor, highestFloor, currentFloor=0, capacity=10):
    """Initialize the Elevator instance with the lowest and highest possible floors as well as the current floor."""
    self.bay = bay
    self.lowest = lowestFloor
    self.highest = highestFloor
    self.current = currentFloor
    self.capacity = capacity
    self.speed = 0  #Float, accounts for direction and current speed.
    self.stops = []
    self.nextStop = None
    self.personList = []
    self._lock = threading.Lock()


  
  def __str__(self):
    """Return string for printing current postion"""
    with self._lock:
      if self.travelling:
        return "Elevator is travelling {direction} and is currently travelling from floor {cfloor} to {nfloor}.".format(
          direction=self.getString(),
          cfloor=self.current,
          nfloor=(self.current + self.direction))
      else:
        return "Elevator is currently waiting on floor {cfloor}".format(
          cfloor=self.current)



  
  def addStop(self, floor):
    """Add a floor to the list of floors for the Elevator to stop on."""
    if self.lowest <= floor <= self.highest:
      with self._lock:
        self.stops.append(floor)
        return True
    return False


  def 
