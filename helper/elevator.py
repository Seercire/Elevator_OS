import threading


class Elevator():
  directionString = ["stationary", "up", "down"]

  def __init__(self,
               bay,
               lowestFloor,
               highestFloor,
               currentFloor=1,
               capacity=10):
    """Initialize the Elevator instance with the lowest and highest possible floors as well as the current floor."""
    self.bay = bay
    self.lowest = lowestFloor
    self.highest = highestFloor
    self.current = currentFloor
    self.capacity = capacity
    self.stops = set()
    self.personList = []
    self.direction = 0
    self._lock = threading.Lock()
    self.nextActionTime = 0

  def __str__(self):
    """Return string for printing current postion"""
    with self._lock:
      if self.direction != 0:
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

  
  def addPerson(self, person):
    """Add a person to the list of people for the Elevator to pick up."""
    if len(self.personList) < self.capacity:
      with self._lock:
        self.personList.append(person)
        return True
    return False

  
  def getElevatorStatus(self):
    """Return a string representation of the Elevator's current status."""
    match self.direction:
      case 0:
        return "{floor}|{direction}|{count}".format(floor=self.current, direction="W", count=len(self.personList))
      case 1:
        return "{floor}|{direction}|{count}".format(floor=self.current, direction="U", count=len(self.personList))
      case -1:
        return "{floor}|{direction}|{count}".format(floor=self.current, direction="D", count=len(self.personList))
      case _:
        """This should never happen"""
        return "ERROR"


  def timerTick(self):
    """Handles the next tick of the timer and calls any necessary actions."""
    with self._lock:
      if self.nextActionTime == 0:
        #Handle the current action.

        """
        If the elevator is stationary, and there are no stops, then the elevator will wait.
        If the elevator is stationary, and there are stops, then the elevator will begin travelling towards the next stop.
        If the elevator is moving, then we determine if it has reached the next stop. If it has, then:
          1) We set the new timer to 5 seconds + 1 second per person entering/exiting.
          2) We remove the stop from the list of stops.
        """
        match self.direction:
          case 0:
            #Determine if we need to begin moving.
            if len(self.stops) == 0:                         #No stops, so we wait.
              pass
            elif self.current in self.stops:                 #We have a stop, so we let people off/on.
                exitCount = self.removePassengers()
                enterCount = addPassengers(self.bay, self.current)
                self.nextActionTime = 5 + exitCount + enterCount
            elif any(i > self.current for i in self.stops):  #We need to begin moving upwards.
                self.direction = 1
                self.nextActionTime = 5
            else:                                            #We need to begin moving downwards.    
                self.direction = -1
                self.nextActionTime = 5

          case 1 | -1:
            #Elevator is moving, determine if we need to stop.
            self.current += self.direction  #Change the current floor.

            #Determine if this is a stop floor, if it is then we stop the elevator.
            if self.current in self.stops:
              self.direction = 0
          

      if self.nextActionTime > 0:
        self.nextActionTime -= 1
          