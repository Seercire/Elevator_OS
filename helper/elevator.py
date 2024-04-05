import threading
from helper import logger, peopleQueue, peopleDictionary, peopleWaitingForElevator, peopleInElevators, peopleLock, currentTime




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
    """Return a string representation of the Elevator's current status."""
    return f"{self.bay}|{self.current}|{self.directionString()}|{len(self.personList)}|{self.remainingCapacity()}"
    

  def directionString(self):
    """Returns a single character designator for the direction of the elevator."""
    match self.direction:
      case 0:
        return "S"
      case 1:
        return "U"
      case -1:
        return "D"
      case _:
        return "E"

  def remainingCapacity(self):
    """Returns the remaining capacity of the elevator."""
    return self.capacity - len(self.personList)

        
  def addStop(self, floor):
    """Add a floor to the list of floors for the Elevator to stop on."""
    if self.lowest <= floor <= self.highest:
      logger.debug(f"Elevator {self.bay} will now stop on floor {floor}.")
      self.stops.add(floor)
      return True
    return False


  def removePassengers(self, cTime):
    """Remove passengers from the elevator if this is their current floor."""
    global currentTime
    
    with self._lock:
      with peopleLock:
        #Generate a list of id's of people who are exiting on this floor.
        peopleExiting = [id for id in self.personList if peopleDictionary[id].getEndFloor() == self.current]

      #Remove the people from the dictionary.
      for person in peopleExiting:
        logger.info(f"{person} has gotten off of elevator {self.bay}.")
        
        #Remove their ID from the personList
        self.personList.remove(person)

        #Complete the person's journey.
        peopleDictionary[person].completeJourney(cTime)
        

    return len(peopleExiting)

  
  def addPassengers(self):
    """Add passengers to the elevator if they are waiting for this elvator on the current floor."""
    global peopleLock, peopleWaitingForElevator, peopleInElevators
    
    with self._lock:
      with peopleLock:
        peopleEntering = [id for id in peopleWaitingForElevator if peopleDictionary[id].checkMatch(self.current, self.bay)]
    
        for person in peopleEntering:
          #Ensure we have room on the elevator.
          if len(self.personList) < self.capacity:
            logger.info(f"{person} has gotten onto elevator {self.bay}.")
            
            #Add the person to the personList
            self.personList.append(person)

            #Add the person's stop to the elevator's stops.
            self.addStop(peopleDictionary[person].getEndFloor())
    
            #Remove the person from the peopleWaitingForElevator list.
            peopleWaitingForElevator.remove(person)
            
            #Add the person to the peopleInElevators list.
            peopleInElevators.append(person)
          else:
            #We don't have room for this person, they will need to requeue.
            logger.info(f"Elevator at capacity! Adding {person} back to peopleQueue")
            peopleQueue.put(person)
    
    return len(peopleEntering)
      
  
  def timerTick(self, cTime):
    """Handles the next tick of the timer and calls any necessary actions."""
    if self.nextActionTime == 0:
      #Handle the current action.
      match self.direction:
        case 0:
          #Determine if we need to begin moving.
          if len(self.stops) == 0:                         #No stops, so we wait.
            pass
          
          elif self.current in self.stops:                 #We have a stop, so we let people off/on.
              logger.debug(f"Elevator {self.bay} is letting people on/off on floor {self.current}.")
              with self._lock:
                self.stops.discard(self.current)
              exitCount = self.removePassengers()
              enterCount = self.addPassengers()
              logger.debug(f"Elevator {self.bay} had {exitCount} step off and {enterCount} step on.")
              self.nextActionTime = 5 + exitCount + enterCount
          
          elif any(i > self.current for i in self.stops):  #We need to begin moving upwards.
              logger.debug(f"Elevator {self.bay} is leaving floor {self.current} - going up.")
              self.direction = 1
              self.nextActionTime = 5
              if self.current + self.direction in self.stops:    #Handle deceleration
                self.nextActionTime += 2
          
          else:                                            #We need to begin moving downwards.
              logger.debug(f"Elevator {self.bay} is leaving floor {self.current} - going down.")
              self.direction = -1
              self.nextActionTime = 5
              if self.current + self.direction in self.stops:    #Handle deceleration
                self.nextActionTime += 2
  
        case 1 | -1:
          #Elevator is moving, determine if we need to stop.
          self.current += self.direction  #Change the current floor.
  
          #Determine if this is a stop floor, if it is then we stop the elevator.
          if self.current in self.stops:
            self.direction = 0
            logger.debug(f"Elevator {self.bay} is stopping on floor {self.current}.")
          else:
            self.nextActionTime = 3
            logger.debug(f"Elevator {self.bay} is passing by floor {self.current}.")
            if self.current + self.direction in self.stops:  #Handle deceleration
              self.nextActionTime += 2
        case _:
          """This should never happen"""
          return "ERROR"
          
    if self.nextActionTime > 0:
      self.nextActionTime -= 1
          