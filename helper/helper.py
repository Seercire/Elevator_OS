from queue import Queue
import logging
import threading


"""GLOBAL VARIABLES"""
#Command and Control Variables
currentTime              = 0                  #Current timestep
startEvent               = threading.Event()  #The event that starts the simulation
stopEvent                = threading.Event()  #The event that stops the simulation
completeEvent            = threading.Event()  #The event that sees if the simulation has completed
startTimeDictionary      = {}                 #A dictionary of people waiting for an elevator
stragglerCheckTimeStep   = 60                 #Timestep at which we will next check for stragglers
#API data
peopleQueue              = Queue()            #The queue of people waiting for an elevator
#People Data
peopleLock               = threading.Lock()
peopleDictionary         = {}                 #Dictionary of all people in the simulation.
peopleWaitingForElevator = []                 #List of people waiting for the elevator
peopleInElevators        = []                 #List of people currently in an elevator
peopleInCompletedState   = []                 #List of people who have completed their journey
#Elevator Data
elevatorDictionary       = {}                 #Dictionary of all elevators in the simulation.
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setLoggingLevel(verbose, debug):
  # Set the logging level based on the verbose flag
  if debug:
    logger.setLevel(logging.DEBUG)
  elif verbose:
    logger.setLevel(logging.INFO)
  else:
    logger.setLevel(logging.WARNING)
