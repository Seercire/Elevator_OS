import argparse
import os
import socket
import sys
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'helper')))

from elevator import Elevator
from api import runApp
from person import Person
from helper import currentTime, setLoggingLevel, logger, peopleDictionary, peopleWaitingForElevator, peopleInCompletedState, peopleInElevators, startEvent, stopEvent, completeEvent, startTimeDictionary, stragglerCheckTimeStep, peopleQueue, peopleLock, elevatorDictionary


def readableFileCheck(path):
  """Function to check if the provided file path is valid"""
  if not os.path.isfile(path):
    raise argparse.ArgumentTypeError(f"{path} is not a valid file path")
  if os.access(path, os.R_OK):
    return path
  else:
    raise argparse.ArgumentTypeError(f"{path} is not a readable file")


# Function to check if the provided time is an integer greater than 0
def positiveIntCheck(value):
  """Function to check if the provided integer is a valid positive integer"""
  ivalue = int(value)
  if ivalue <= 0:
    raise argparse.ArgumentTypeError(
      f"{value} is an invalid positive int value")
  return ivalue


def parseArguments():
  # Create the parser
  parser = argparse.ArgumentParser(description="CS4352 - Elevator Simulation")

  # Add the arguments
  parser.add_argument("-b",
                      "--buildingFileName",
                      type=readableFileCheck,
                      required=True,
                      help="File path to the building file")
  parser.add_argument("-p",
                      "--peopleFileName",
                      type=readableFileCheck,
                      required=True,
                      help="File path to the people file")
  parser.add_argument("-r",
                      "--reportFileName",
                      required=True,
                      help="File path to the output report file")
  parser.add_argument("-v",
                      "--verbose",
                      action="store_true",
                      help="an optional flag to turn on verbose mode")
  parser.add_argument("-d",
                      "--debug",
                      action="store_true",
                      help="an optional flag to turn on debug verbose mode")
  parser.add_argument("-t",
                      "--time",
                      type=positiveIntCheck,
                      default=18000,
                      help="Max number of time steps.")

  # Parse the arguments
  args = parser.parse_args()

  # Return the arguments
  return args


def main():
  global currentTime, completeEvent

  #Set the start time
  programStartTime = time.time()

  # Parse the arguments
  parsedArgs = parseArguments()
  setLoggingLevel(parsedArgs.verbose, parsedArgs.debug)

  # Read the building and Person files
  readBuildingFile(parsedArgs.buildingFileName)
  readPeopleFile(parsedArgs.peopleFileName)

  # Start the API on a separate thread
  apiThread = threading.Thread(target=runApp)
  apiThread.start()

  # Wait for the signal to begin the simulation
  logger.debug("Waiting for the Simulation Start Event")
  startEvent.wait()
  logger.debug("Recieved the Simulation Start Event")
  simulatorStartTime = time.time()

  # Start the simulation
  logger.debug("Beginning the Simulation")
  while (currentTime < parsedArgs.time and not stopEvent.is_set()):
    # Print the current state of the simulation
    logger.debug(f"Beginning Time Step: {currentTime}")

    # 1) Add people to the API queue
    movePeopleToQueue(currentTime)

    # 2) For each elevator, run the time handler
    for elevator in elevatorDictionary.values():
      elevator.timerTick(currentTime)

    # 3) Check for stragglers
    # checkForStragglers(currentTime)

    # 4) Check if everyone has completed their journey - if yes, print the final results and terminate the simulation.
    if len(peopleDictionary) == len(peopleInCompletedState):
      logger.info("All people have completed their journey")
      break

    # 5) Increment the time step.
    currentTime += 1
    time.sleep(.99)

  #Simulation has completed
  completeEvent.set()
  simulatorEndTime = time.time()

  if not stopEvent.is_set():
    #Sleep 20 seconds so that the API thread can run a little longer so student code verify the elevator is offline.
    time.sleep(20) 

  #Write output report
  printFinalResults(parsedArgs.reportFileName, programStartTime, simulatorStartTime, simulatorEndTime)

  logger.debug("Shutting down the process.")
  os._exit(0)


def readBuildingFile(filename):
  global elevatorDictionary
  """Reads a building file and places their data into the elevatorDictionary."""
  logger.debug("Reading the building file.")
  with open(filename, 'r') as file:
    """File format: <bay> <lowest floor> <highest floor> <current floor> <capacity>"""
    for line in file:
      bay, lowest, highest, current, capacity = line.strip().split('\t')
      logger.debug(f"\tFound new elevator:" + f"\n\t\tbay:{bay}" +
                   f"\n\t\tlowest floor: {lowest}" +
                   f"\n\t\thighest floor: {highest}" +
                   f"\n\t\tcurrent floor: {current}" +
                   f"\n\t\tcapacity: {capacity}")
      
      elevatorDictionary[bay] = Elevator(bay,
                                         int(lowest),
                                         int(highest),
                                         currentFloor=int(current),
                                         capacity=int(capacity))
  logger.debug("Closing the building file.")


def readPeopleFile(filename):
  """Reads a people file and places their data into the peopleDictionary."""

  global peopleDictionary, peopleWaitingForElevator, peopleInElevators, startTimeDictionary

  logger.debug("Reading the people file.")
  with open(filename, 'r') as file:
    """File format: <name> <start floor> <end floor> <start time>"""
    for line in file:
      name, startFloor, endFloor, startTime = line.strip().split('\t')
      peopleDictionary[name] = Person(name, int(startFloor), int(endFloor),
                                      int(startTime))
  logger.debug("Closing the people file.")

  for person in peopleDictionary.values():
    if person.startTime not in startTimeDictionary:
      startTimeDictionary[person.startTime] = [person.id]
    else:
      startTimeDictionary[person.startTime].append(person.id)


def movePeopleToQueue(currTime):
  """Adds people to the peopleQueue if they are waiting for an elevator and their start time is the current time"""
  global peopleQueue, startTimeDictionary

  if currTime in startTimeDictionary:
    for personID in startTimeDictionary[currTime]:
      logger.debug(f"Adding {personID} to peopleQueue")
      peopleQueue.put(personID)


def checkForStragglers(currTime):
  """Checks if there are any people waiting for an elevator when the queue to handle them is empty."""
  global peopleQueue, stragglerCheckTimeStep
  if currTime > stragglerCheckTimeStep:
    stragglerCheckTimeStep = currentTime + 60  #Set it one minute into the future before we do this check again
    if len(peopleQueue.queue) == 0:
      if currTime > max(startTimeDictionary.keys()):
        if len(peopleWaitingForElevator) > 0:
          #People have not been handled.
          for person in peopleWaitingForElevator:
            logger.debug(
              f"Adding {person} back to peopleQueue as they appear to have been skipped."
            )
            peopleQueue.put(person)


def printFinalResults(reportFile, programStartTime, simulatorStartTime, simulatorEndTime):
  """Prints the final results of the simulation."""
  global peopleDictionary, elevatorDictionary
  #Report Variables
  shortestTravelTime       = sys.maxsize
  shortestTravelTimePerson = None
  longestTravelTime        = 0
  longestTravelTimePerson  = None
  occupantCountDictionary  = {}

  #Set up the count dictionary
  for elevator in elevatorDictionary.keys():
    occupantCountDictionary[elevator] = 0
  

  for person in peopleDictionary.values():
    if person.endTime != None:
      travelTime = person.getTravelTime()
      occupantCountDictionary[person.assignedBay] += 1
      if travelTime < shortestTravelTime:
        shortestTravelTime = travelTime
        shortestTravelTimePerson = person.id
      if travelTime > longestTravelTime:
        longestTravelTime = travelTime
        longestTravelTimePerson = person.id

  #Print the final results
  with open(reportFile, 'w') as file:
    file.write("----------  Runtime Data  ----------\n")
    file.write(f"Program Start Time:                   {time.ctime(programStartTime)}\n")
    file.write(f"Simulation Start Time:                {time.ctime(simulatorStartTime)}\n")
    file.write(f"Simulation End Time:                  {time.ctime(simulatorEndTime)}\n")
    file.write(f"Total Time Steps:                     {currentTime}\n")
    file.write(f"Time Waiting for Simulation to Start: {simulatorStartTime - programStartTime}\n")
    file.write(f"Time Spent in Simulation:             {simulatorEndTime - simulatorStartTime}\n")
    file.write(f"Total Time:                           {simulatorEndTime - programStartTime}\n")
    
    file.write("\n----------  Elevator Data  ----------\n")
    for elevator in elevatorDictionary.values():
      file.write(f"Elevator ID: {elevator.bay}\n" +
                 f"\tElevator End Floor:      {elevator.current}\n" +
                 f"\tElevator Occupant Count: {occupantCountDictionary[elevator.bay]}\n")
    
    file.write("\n----------  Person Data  ----------\n")
    file.write(f"Total People: {len(peopleDictionary)}\n")
    if shortestTravelTimePerson != None:
      file.write(f"Person with Shortest Travel Time: {shortestTravelTimePerson}\n" +
                 f"\tElevator Bay: {peopleDictionary[shortestTravelTimePerson].assignedBay}\n" +
                 f"\tStart Floor:  {peopleDictionary[shortestTravelTimePerson].startFloor}\n" +
                 f"\tEnd Floor:    {peopleDictionary[shortestTravelTimePerson].endFloor}\n" +
                 f"\tStart Time:   {peopleDictionary[shortestTravelTimePerson].startTime}\n" +
                 f"\tEnd Time:     {peopleDictionary[shortestTravelTimePerson].endTime}\n" +
                 f"\tTravel Time:  {shortestTravelTime}\n")
    else:
      file.write("Person with Shortest Travel Time: None\n")

    if longestTravelTimePerson != None:
      file.write(f"Person with Longest Travel Time: {longestTravelTimePerson}\n" + 
                 f"\tElevator Bay: {peopleDictionary[longestTravelTimePerson].assignedBay}\n" +
                 f"\tStart Floor:  {peopleDictionary[longestTravelTimePerson].startFloor}\n" +
                 f"\tEnd Floor:    {peopleDictionary[longestTravelTimePerson].endFloor}\n" + 
                 f"\tStart Time:   {peopleDictionary[longestTravelTimePerson].startTime}\n" +
                 f"\tEnd Time:     {peopleDictionary[longestTravelTimePerson].endTime}\n" +
                 f"\tTravel Time:  {longestTravelTime}\n")
    else:
      file.write("Person with Longest Travel Time: None\n")

    file.write("\n----------  Final Statistics  ----------\n")
    file.write(f"Total People:                       {len(peopleDictionary)}\n")
    file.write(f"People Remaining in Queue:          {peopleQueue.qsize()}\n")
    file.write(f"People Still Waiting for Elevator:  {len(peopleWaitingForElevator)}\n")
    file.write(f"People Remaining in Elevators:      {len(peopleInElevators)}\n")
    file.write(f"People Who Completed Their Journey: {len(peopleInCompletedState)}\n\n")
    

if __name__ == '__main__':
  # Get the current hostname
  hostname = socket.gethostname()

  # List of blocked hostnames
  blockedHostnames = [
      "quanah.hpcc.ttu.edu",
      "login-20-25.hpcc.ttu.edu",
      "login-20-26.hpcc.ttu.edu"
  ]

  # Check if the current hostname is in the list of blocked hostnames
  if hostname in blockedHostnames:
      sys.exit("Error: This script cannot be run on this server.  You must run it on a server that is not a login server.")
  
  main()
