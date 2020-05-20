#!/usr/bin/env python

from flask import Flask, request, abort
import subprocess, time, signal, sys, os, airsim

app = Flask(__name__)

client = airsim.CarClient()
client.confirmConnection()

interfaceprocess = None

# curl --header "Content-Type: application/json" --request POST --data '{"master": "http://localhost:11311", "mission": "trackdrive"}' http://localhost:5000/mission/selectcar
@app.route('/mission/start', methods=['POST'])
def mission_start():
    if request.json is None or request.json['master'] is None or request.json['mission']:
        return abort(400)    

    master = request.json['master']
    mission = request.json['mission']

    procenv = os.environ.copy()
    procenv["ROS_MASTER_URI"] = master

    global interfaceprocess
    interfaceprocess = subprocess.Popen(['roslaunch', 'fsds_ros_bridge', 'fsds_ros_bridge.launch', 'mission:={}'.format(mission)], env=procenv)   

    return {'message': 'Mission started'}

@app.route('/mission/stop', methods=['POST'])
def mission_stop():
    # check if previous process is still running
    if interfaceprocess is not None and interfaceprocess.poll() is None:
        # try to stop it gracefully. SIGINT is the equivilant to doing ctrl-c
        interfaceprocess.send_signal(signal.SIGINT)
        time.sleep(3)
        # still running?
        if interfaceprocess.poll() is None:
            # kill it with fire
            interfaceprocess.terminate()
            # wait for it to finish
            interfaceprocess.wait()

    return {'message': 'Mission stopped'}

@app.route('/mission/reset', methods=['POST'])
def mission_reset():
    client.reset()
    return {'message': 'Car reset'}

if __name__ == '__main__':
    app.run()