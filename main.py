import argparse
import os
import sys
import threading
import time

sys.path.insert(
  0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'helper')))

from elevator import Elevator
from api import runApp
from person import Person
from helper import currentTime, setLoggingLevel, logger, peopleDictionary, peopleWaitingForElevator, peopleInCompletedState, startEvent, stopEvent, completeEvent, startTimeDictionary, stragglerCheckTimeStep, peopleQueue, peopleLock, elevatorDictionary



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
  parser.add_argument(
    "-b",
    "--buildingFileName",
    type=readableFileCheck,
    required=True,
    help="a required file path that leads to a readable building file")
  parser.add_argument(
    "-p",
    "--peopleFileName",
    type=readableFileCheck,
    required=True,
    help="a required file path that leads to a readable people file")
  parser.add_argument("-v",
                      "--verbose",
                      action="store_true",
                      help="an optional flag to turn on verbose mode")
  parser.add_argument("-d",
                      "--debug",
                      action="store_true",
                      help="an optional flag to turn on debug verbose mode")
  parser.add_argument(
    "-t",
    "--time",
    type=positiveIntCheck,
    default=18000,
    help=
    "an optional argument that sets the maximum number of time steps the simulation will run for. Default 18000"
  )

  # Parse the arguments
  args = parser.parse_args()

  # Return the arguments
  return args


def main():
  global currentTime, completeEvent

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

  # Start the simulation
  logger.debug("Beginning the Simulation")
  while (currentTime < parsedArgs.time and not stopEvent.is_set()):
    # Print the current state of the simulation
    logger.debug(f"Beginning Time Step: {currentTime}")

    # 1) Add people to the API queue
    movePeopleToQueue(currentTime)

    # 2) For each elevator, run the time handler
    for elevator in elevatorDictionary.values():
      elevator.timerTick()

    # 3) Check for stragglers
    checkForStragglers(currentTime)

    # 4) Check if everyone has completed their journey - if yes, print the final results and terminate the simulation.
    if len(peopleDictionary) == len(peopleInCompletedState):
      logger.info("All people have completed their journey")
      break

    # 5) Increment the time step.
    currentTime += 1
    time.sleep(1)

  #Simulation has completed
  completeEvent.set()

  #Write output report
  #printFinalResults()

  apiThread.join()
  logger.debug("Shutting down the process.")


def readBuildingFile(filename):
  global elevatorDictionary
  """Reads a building file and places their data into the elevatorDictionary."""
  logger.debug("Reading the building file.")
  with open(filename, 'r') as file:
    """File format: <bay> <lowest floor> <highest floor> <current floor> <capacity>"""
    for line in file:
      bay, lowest, highest, current, capacity = line.strip().split('\t')
      logger.debug(
        f"\tFound new elevator:\n\t\tbay:{bay}\n\t\tlowest/highest/current floors: {lowest}/{highest}/{current}\n\t\tcapacity: {capacity}"
      )
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
    stragglerCheckTimeStep += 60  #Set it one minute into the future before we do this check again
    if len(peopleQueue.queue) == 0:
      if currTime > max(startTimeDictionary.keys()):
        if len(peopleWaitingForElevator) > 0:
          #People have not been handled.
          for person in peopleWaitingForElevator:
            logger.debug(
              f"Adding {person} back to peopleQueue as they appear to have been skipped."
            )
            peopleQueue.put(person)


if __name__ == '__main__':
  main()
