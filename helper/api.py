from flask import Flask, request
from helper import elevatorDictionary, startEvent, stopEvent, completeEvent, peopleDictionary, peopleQueue, logger, peopleWaitingForElevator, peopleInElevators, peopleInCompletedState

#GLOBAL VARIABLES
app = Flask(__name__)  #The Flask API


@app.route('/Simulation/<string:command>', methods=['GET', 'PUT'])
def simulation(command):
  if request.method == 'PUT':
    #Check which command was provided.
    if command.lower() == 'start':  #Start the simulation
      if not startEvent.is_set():  # Check if simulation isn't already started
        startEvent.set()
        return "Simulation started", 202
      else:
        return "Simulation is already running.", 200

    elif command.lower(
    ) == 'stop':  #Stop the simulation and terminate the FLASK thread.
      stopEvent.set()
      return "Simulation stopping", 202

    else:
      return "Invalid command", 400

  elif request.method == 'GET':
    #Return the current status of the simulation
    if completeEvent.is_set():
      return "Simulation is complete.", 200
    elif stopEvent.is_set():
      return "Simulation is stopped.", 200
    elif startEvent.is_set():
      return "Simulation is running.", 200
    else:
      return "Simulation is not running.", 200


@app.route('/ElevatorStatus/<string:elevatorID>', methods=['GET'])
def getElevatorStatus(elevatorID):
  if startEvent.is_set():
    if elevatorID in elevatorDictionary:
      return f"{elevatorDictionary[elevatorID]}"
    else:
      return "DNE", 400
  else:
    return "Simulation is not running.", 400


@app.route('/NextInput', methods=['GET'])
def getNextInput():
  """Retrieves the next person in the queue and returns their data, returns 'NONE' if the queue is empty."""
  global peopleQueue

  if startEvent.is_set():
    if len(peopleQueue.queue) > 0:
      personID = peopleQueue.get()
      return f"{peopleDictionary[personID]}", 200
    else:
      return "NONE", 200
  else:
    return "Simulation is not running.", 400


@app.route('/AddPersonToElevator/<string:personID>/<string:elevatorID>',
           methods=['PUT'])
def addPersonToElevator(personID, elevatorID):
  """Adds a person's starting to the elevator's stop list and assigns the elevator to the person"""
  global peopleDictionary, elevatorDictionary, peopleWaitingForElevator

  if startEvent.is_set():
    # At this point, personID and elevatorID are already extracted from the URL
    if (personID in peopleWaitingForElevator or personID in peopleInElevators
        or personID in peopleInCompletedState):
      return f"Person ID {personID} was already assigned previously.", 400

    elif personID in peopleDictionary:
      if elevatorID in elevatorDictionary:
        if (elevatorDictionary[elevatorID].lowest <=
            peopleDictionary[personID].startFloor <=
            elevatorDictionary[elevatorID].highest):
          if (elevatorDictionary[elevatorID].lowest <=
              peopleDictionary[personID].endFloor <=
              elevatorDictionary[elevatorID].highest):

            # Add the person's starting floor to the elevator's stop list
            elevatorDictionary[elevatorID].addStop(
              peopleDictionary[personID].startFloor)
            peopleDictionary[personID].setAssignedBay(elevatorID)
            peopleWaitingForElevator.append(personID)
            logger.debug(f"Person {personID} is now waiting for {elevatorID}.")

            return f"Person ID {personID} added to Elevator ID {elevatorID}", 200  # Returns a plain text response
          else:
            return f"Person ID {personID} cannot be assigned to Elevator ID {elevatorID} because their end floor is not within the elevator's range.", 400
        else:
          return f"Person ID {personID} cannot be assigned to Elevator ID {elevatorID} because their start floor is not within the elevator's range.", 400
      else:
        return f"Elevator ID {elevatorID} does not exist.", 400
    else:
      return f"Person ID {personID} does not exist.", 400
  else:
    return "Simulation is not running.", 400


""" -----------------  OLD STYLE API  ----------------- """


# The PUT APIs below behave like the original ones you encountered in Assignment #3
@app.route('/Simulation_A3', methods=['GET', 'PUT'])
def simulation_A3():
  data = request.data.decode('utf-8').lower()
  if request.method == 'PUT':
    #Check which command was provided.
    if data == 'start':  #Start the simulation
      if not startEvent.is_set():  # Check if simulation isn't already started
        startEvent.set()
        return "Simulation started", 202
      else:
        return "Simulation is already running.", 200

    elif data == 'stop':  #Stop the simulation and terminate the FLASK thread.
      stopEvent.set()
      return "Simulation stopping", 202

    else:
      return "Invalid command", 400

  elif request.method == 'GET':
    #Return the current status of the simulation
    if completeEvent.is_set():
      return "Simulation is complete.", 200
    elif startEvent.is_set():
      return "Simulation is running.", 200
    else:
      return "Simulation is not running.", 200


@app.route('/ElevatorStatus_A3', methods=['GET'])
def getElevatorStatus_A3():
  data = request.data.decode('utf-8')
  if startEvent.is_set():
    if data in elevatorDictionary:
      return f"{elevatorDictionary[data]}"
    else:
      return "DNE", 400
  else:
    return "Simulation is not running.", 400


@app.route('/AddPersonToElevator_A3', methods=['PUT'])
def addPersonToElevator_A3():
  """Adds a person's starting to the elevator's stop list and assigns the elevator to the person"""
  global peopleDictionary, elevatorDictionary, peopleWaitingForElevator

  try:
    data = request.data.decode('utf-8')
    personID, elevatorID = data.split('|')
  except ValueError as e:
    return f"Invalid input: {e}", 400
  """Adds a person's starting to the elevator's stop list and assigns the elevator to the person"""
  global peopleDictionary, elevatorDictionary, peopleWaitingForElevator

  if startEvent.is_set():
    # At this point, personID and elevatorID are already extracted from the URL
    if (personID in peopleWaitingForElevator or personID in peopleInElevators
        or personID in peopleInCompletedState):
      return f"Person ID {personID} was already assigned previously.", 400

    elif personID in peopleDictionary:
      if elevatorID in elevatorDictionary:
        if (elevatorDictionary[elevatorID].lowest <=
            peopleDictionary[personID].startFloor <=
            elevatorDictionary[elevatorID].highest):
          if (elevatorDictionary[elevatorID].lowest <=
              peopleDictionary[personID].endFloor <=
              elevatorDictionary[elevatorID].highest):
            # Add the person's starting floor to the elevator's stop list
            elevatorDictionary[elevatorID].addStop(
              peopleDictionary[personID].startFloor)
            peopleDictionary[personID].setAssignedBay(elevatorID)
            peopleWaitingForElevator.append(personID)
            logger.debug(f"Person {personID} is now waiting for {elevatorID}.")

            return f"Person ID {personID} added to Elevator ID {elevatorID}", 200  # Returns a plain text response
          else:
            return f"Person ID {personID} cannot be assigned to Elevator ID {elevatorID} because their end floor is not within the elevator's range.", 400
        else:
          return f"Person ID {personID} cannot be assigned to Elevator ID {elevatorID} because their start floor is not within the elevator's range.", 400
      else:
        return f"Elevator ID {elevatorID} does not exist.", 400
    else:
      return f"Person ID {personID} does not exist.", 400
  else:
    return "Simulation is not running.", 400

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
  """Simple heartbeat endpoint to check if the service is running"""
  return 'OK', 200
  



def runApp(port):
  app.run(port=port, debug=True, use_reloader=False)
