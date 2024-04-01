from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/NextSignal', methods=['GET'])
def next_signal():
    #Pulls the next signal off the queue and returns it.
    #Returns "$" if the simulation is complete.
    #Returns "NS" if there is no signal to return.
    return 'Elevator 1'

@app.route('/ElevatorStatus', methods=['GET'])
def elevator_status():
    return jsonify(elevator_status)

@app.route('/ElevatorStatus_Bay1', methods=['GET'])
def bay1_status():
    return jsonify(bay1_status)

@app.route('/ElevatorCommand', methods=['PUT'])
def elevator_command():
    command = request.json.get('command')

    # In a real application, you would likely define a class to represent the elevator and its behavior
    # This is just a simple example to demonstrate handling a PUT request
    if command == 'go':
        elevator_status['status'] = 'moving'
    elif command == 'stop':
        elevator_status['status'] = 'stopped'

    return jsonify(elevator_status)

if __name__ == '__main__':
    app.run(debug=True)
