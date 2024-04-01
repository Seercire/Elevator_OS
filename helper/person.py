class Person():

  def __init__(self, identifier, startFloor, endFloor, timeTick):
    """Initialize the Person instance with their starting floor, which floor they want to end up on, as well as starting their waiting clock."""
    self.id = identifier
    self.start = startFloor
    self.end = endFloor
    self.startTime = timeTick
    self.endTime = None
    self.assignedBay = None

  def setEndTime(self, timeTick):
    self.endTime = timeTick

  def getEndTime(self):
    return self.endTime

  def setAssignedBay(self, bay):
    self.assignedBay = bay

  def getAssignedBay(self):
    return self.assignedBay

  def checkMatch(self, floor, bay):
    """Check if the person is on the current floor and waiting on the current bay."""
    return floor == self.start and bay == self.assignedBay
