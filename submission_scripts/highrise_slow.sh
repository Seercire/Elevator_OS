#!/bin/bash
#SBATCH --job-name=Elevator_Highrise_Slow
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=quanah
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --time=00:20:00
#SBATCH --mem-per-cpu=5370MB  #5.3GB per core


#==============================================================================
#title        : highrise_slow.sh
#description  : This script will perform the following actions:
#		  1) Purge all modules then load GNU 5.4.0 module.
#		  2) Activate the CS4352 Conda environment.
#		  3) Run make on your C / C++ code.
#		  4) Boot up the API application (Python w/ FLASK)
#		  4) Execute your C/C++ Application to interface with the APIs
#author       : errees (R#123456)
#date         : 04/21/2024
#version      : 1.0
#usage        : sbatch highrise_slow.sh
#notes        : This script requires GNU 5.4.0 and Python3 (conda environment)
#bash_version : 4.2.46(2)-release
#==============================================================================

#Set Simulation Name and Time
inputFileDirectory="/lustre/work/errees/courses/cs4352/final_project/Elevator_OS/input_files"
buildingFile="highrise.bldg"
simulationName="highrise_slow"
simulationTime=626


#Clean the Environment
module purge
module load gnu/5.4.0

#Activate the CS4352 Conda Environment
source /lustre/work/errees/conda/etc/profile.d/conda.sh
conda activate cs4352

#Delete the executable then re-compile the source code.
echo -e "\n\nCS4352 Final Project Test Script - Highrise Slow.\n"
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


else
        #The make command did not generate a binary file - likely due to incorrect makefile or errors in code.
        echo -e "\n\nThe compilation process appears to have failed! Printing out make.log:\n"
        cat "make.log"
        echo -e "\n"
fi

