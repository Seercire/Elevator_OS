import os
import sys

"""GLOBAL VARIABLES"""
peopleWaitingForElevator  = []  #List of people waiting for the elevator
peopleInElevators         = []  #List of people currently in an elevator
peopleInCompletedState    = []  #List of people who have completed their journey
currentTime               = 0   #Current timestep

sys.path.insert(
  0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'helper')))

from elevator import Elevator
from api import app


def main():
  elevator = Elevator(bay=1,
                      lowestFloor=0,
                      highestFloor=10,
                      currentFloor=1,
                      capacity=10)
  print(elevator)




if __name__ == '__main__':
  main()
