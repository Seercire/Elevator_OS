#!/bin/bash
#SBATCH --job-name=Elevator_Hotel_Busy
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=nocona
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --time=00:20:00
#SBATCH --mem-per-cpu=1GB


#==============================================================================
#title        : hotel_busy.sh
#description  : This script will perform the following actions:
#		  1) Purge all modules then load GNU 5.4.0 module.
#		  2) Activate the CS5379 Conda environment.
#		  3) Run make on your C / C++ code.
#		  4) Boot up the API application (Python w/ FLASK)
#		  4) Execute your C/C++ Application to interface with the APIs
#author       : errees (R#123456)
#date         : 04/21/2024
#version      : 1.0
#usage        : sbatch hotel_busy.sh
#notes        : This script requires GNU 5.4.0 and Python3 (conda environment)
#bash_version : 4.2.46(2)-release
#==============================================================================

#Code to find an available network port.
find_free_port() {
  while true; do
    PORT=$((5000 + RANDOM % 1000))
    ss -ltn | grep -q ":$PORT " || break
  done
  echo $PORT
}

#Required variables
API_UP=0

#Determine an available port so student tests hopefully do not bump into eachother.
PORT=$(find_free_port)
echo "Selected port: $PORT"


#Clean the Environment
module purge
module load gcc

#Activate the CS5379 Conda Environment
source /lustre/work/errees/conda/etc/profile.d/conda.sh
conda activate cs5379


#Set Simulation Name and Time
inputFileDirectory="/lustre/work/errees/courses/cs5379/final_project/Elevator_OS/input_files"
buildingFile="hotel.bldg"
simulationName="hotel_busy"
simulationTime=275


#Delete the executable then re-compile the source code.
echo -e "\n\nFinal Project Test Script - Hotel Busy.\n"
echo -e "Running the following commands:"
echo -e "   make clean &> make.log\n   rm -f scheduler_os ${simulationName}_server.log ${simulationName}_user.log ${simulationName}_report.log\n   make &>> make.log"
make clean &> make.log
rm -f scheduler_os "${simulationName}_server.log" "${simulationName}_user.log" "${simulationName}_report.log"
make &>> make.log

if test -f "scheduler_os"; then
        #The make command finished successfully.
        echo -e "\n\nMake successful! Booting up the Elevator Operating System."

  #Execute the Elevator OS
  python3 /lustre/work/errees/courses/cs5379/final_project/Elevator_OS/main.py --port "$PORT" -b "${inputFileDirectory}/${buildingFile}" -p "${inputFileDirectory}/${simulationName}.ppl" -r "${simulationName}_report.log" -t $simulationTime &> "${simulationName}_server.log" &
  API_PID=$!


	#Poll the /health endpoint to determine if the API has booted up.
	for i in {1..20}; do
		if curl -s "http://localhost:$PORT/healthcheck" | grep -q "OK"; then
			echo "Flask API is up!"
			API_UP=1
			break
		fi
		sleep 1
	done


	# Check if API came up successfully or if we need to terminate
	if [ $API_UP -ne 1 ]; then
		echo "Flask API failed to start"
		kill "$API_PID" 2>/dev/null
		exit 1
	fi

  echo -e "Executing scheduler_os.\n\n"
  #Execute assignment_3 application.
  ./scheduler_os "${inputFileDirectory}/${buildingFile}" "$PORT" &> "${simulationName}_user.log"


else
        #The make command did not generate a binary file - likely due to incorrect makefile or errors in code.
        echo -e "\n\nThe compilation process appears to have failed! Printing out make.log:\n"
        cat "make.log"
        echo -e "\n"
fi

