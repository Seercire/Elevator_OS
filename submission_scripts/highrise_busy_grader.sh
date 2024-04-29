#!/bin/bash
#SBATCH --job-name=Elevator_Highrise_Busy
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=quanah
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --time=00:50:00
#SBATCH --mem-per-cpu=5370MB  #5.3GB per core


#==============================================================================
#title        : highrise_busy.sh
#description  : This script will perform the following actions:
#		  1) Purge all modules then load GNU 5.4.0 module.
#		  2) Activate the CS4352 Conda environment.
#		  3) Run make on your C / C++ code.
#		  4) Boot up the API application (Python w/ FLASK)
#		  4) Execute your C/C++ Application to interface with the APIs
#author       : errees (R#123456)
#date         : 04/21/2024
#version      : 1.0
#usage        : sbatch highrise_busy.sh
#notes        : This script requires GNU 5.4.0 and Python3 (conda environment)
#bash_version : 4.2.46(2)-release
#==============================================================================

#Set Simulation Name and Time
inputFileDirectory="/lustre/work/errees/courses/cs4352/final_project/Elevator_OS/input_files"
buildingFile="highrise.bldg"
simulationName="highrise_busy"
simulationTime=1542


#Clean the Environment
module purge
module load gnu/5.4.0

#Activate the CS4352 Conda Environment
source /lustre/work/errees/conda/etc/profile.d/conda.sh
conda activate cs4352

#Delete the executable then re-compile the source code.
echo -e "\n\nCS4352 Final Project Test Script - Highrise Busy.\n"
echo -e "Running the following commands:"
echo -e "   make clean &> make.log\n   rm -f scheduler_os ${simulationName}_server.log ${simulationName}_user.log ${simulationName}_report.log\n   make &>> make.log"
make clean &> make.log
rm -f scheduler_os "${simulationName}_server.log" "${simulationName}_user.log" "${simulationName}_report.log"
make &>> make.log

if test -f "scheduler_os"; then
        #The make command finished successfully.
        echo -e "\n\nMake successful! Booting up the Elevator Operating System."

  #Execute the Elevator OS
  python3 /lustre/work/errees/courses/cs4352/final_project/Elevator_OS/main.py -b "${inputFileDirectory}/${buildingFile}" -p "${inputFileDirectory}/${simulationName}.ppl" -r "${simulationName}_report.log" -t $simulationTime &> "${simulationName}_server.log" &
  
  #Sleep for 5 seconds to ensure the FLASK API is up and running.
  sleep 5

  echo -e "Executing scheduler_os.\n\n"
  #Execute assignment_3 application.
  ./scheduler_os "${inputFileDirectory}/${buildingFile}" &> "${simulationName}_user.log"

  #Set the logfile and grading log name to make referencing easier.
  logFile="${simulationName}_report.log"
  gradeLog="grade.log"

  # Calculate Correctness Score
  correctnessCounter=100
  
  # Extract necessary values from the log file
  totalTimeSteps=$(grep "Total Time Steps:" $logFile | awk '{print $NF}')
  totalPeople=$(grep -m 1 "Total People:" $logFile | tail -n 1 | awk '{print $NF}')
  peopleInQueue=$(grep "People Remaining in Queue:" $logFile | awk '{print $NF}')
  peopleWaiting=$(grep "People Still Waiting for Elevator:" $logFile | awk '{print $NF}')
  peopleInElevators=$(grep "People Remaining in Elevators:" $logFile | awk '{print $NF}')

  # Calculate Code Efficiency Score
  if [ $totalTimeSteps -le 1401 ]; then
    efficiencyScore=100
  elif [ $totalTimeSteps -lt 1472 ]; then
    efficiencyScore=50
  else
    efficiencyScore=0
  fi
  echo "Code Efficiency Score: $efficiencyScore%" > $gradeLog

  # Adjust counter for Total People
  if [ $totalPeople -gt 300 ]; then
    excessPeople=$((totalPeople - 300))
    pointsLostTotalPeople=$(echo "$excessPeople * 0.5" | bc)
    correctnessCounter=$(echo "$correctnessCounter - $pointsLostTotalPeople" | bc)
  else
    pointsLostTotalPeople=0
  fi
  
  # Adjust counter for People in Queue
  pointsLostQueue=$(echo "$peopleInQueue * 3" | bc)
  correctnessCounter=$(echo "$correctnessCounter - $pointsLostQueue" | bc)

  # Adjust counter for People Waiting
  pointsLostWaiting=$(echo "$peopleWaiting * 2" | bc)
  correctnessCounter=$(echo "$correctnessCounter - $pointsLostWaiting" | bc)

  # Adjust counter for People in Elevators
  pointsLostElevators=$(echo "$peopleInElevators * 1" | bc)
  correctnessCounter=$(echo "$correctnessCounter - $pointsLostElevators" | bc)

  # Determine Correctness Score based on the counter
  if [ $(echo "$correctnessCounter >= 98" | bc) -eq 1 ]; then
    correctnessScore=100
  elif [ $(echo "$correctnessCounter >= 80" | bc) -eq 1 ]; then
    correctnessScore=80
  elif [ $(echo "$correctnessCounter >= 50" | bc) -eq 1 ]; then
    correctnessScore=50
  else
    correctnessScore=0
  fi

  echo "Correctness Score: $correctnessScore%" >> $gradeLog
  echo "Detail of Correctness Score Calculation:" >> $gradeLog
  echo "  Points lost due to Total People above 300: -$pointsLostTotalPeople points" >> $gradeLog
  echo "  Points lost due to People in Queue: -$pointsLostQueue points" >> $gradeLog
  echo "  Points lost due to People Waiting: -$pointsLostWaiting points" >> $gradeLog
  echo "  Points lost due to People in Elevators: -$pointsLostElevators points" >> $gradeLog
  

else
        #The make command did not generate a binary file - likely due to incorrect makefile or errors in code.
        echo -e "\n\nThe compilation process appears to have failed! Printing out make.log:\n"
        cat "make.log"
        echo -e "\n"
fi