class Floor(Resource):
  def __init__(self, identifier):
    """Initialize the Elevator instance with the lowest and highest possible floors as well as the current floor."""
    self.floorNumber  =  identifier
    self.upPerson     =  list()
    self.downPerson   =  list()
