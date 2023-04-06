import time

class Person(Resource):
  def __init__(self, identifier, startFloor, endFloor):
    """Initialize the Person instance with their starting floor, which floor they want to end up on, as well as starting their waiting clock."""
    self.id           =  identifier
    self.start        =  startFloor
    self.end          =  endFloor
    self.startTime    =  time.time()
    self.endTime      =  None
    self.assignedBay  =  None

  def setEndTime(self):
    self.endTime = time.time()
