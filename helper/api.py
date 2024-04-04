from flask import Flask, request
from helper import elevatorDictionary

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
      shutdown_function = request.environ.get('werkzeug.server.shutdown')
      if shutdown_function is None:
        raise RuntimeError('Not running with the Werkzeug Server')
      shutdown_function()
      return "Simulation stopped", 202

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


@app.route('/ElevatorStatus/<string:elevator_id>', methods=['GET'])
def getElevatorStatus(elevatorID):
  if startEvent.is_set():
    if elevatorID in elevatorDictionary:
      return f"{elevatorDictionary[elevatorID]}"
    else:
      return "DNE"
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
  global peopleDictionary, elevatorDictionary

  if startEvent.is_set():
    # At this point, personID and elevatorID are already extracted from the URL
    if personID in peopleDictionary:
      if elevatorID in elevatorDictionary:
        # Add the person's starting floor to the elevator's stop list
        elevatorDictionary[elevatorID].addStop(
          peopleDictionary[personID].startFloor)
        peopleDictionary[personID].setAssignedBay(elevatorID)

    return f"Person ID {personID} added to Elevator ID {elevatorID}", 200  # Returns a plain text response
  else:
    return "Simulation is not running.", 400


def runApp():
  app.run(port=5432, debug=True, use_reloader=False)
