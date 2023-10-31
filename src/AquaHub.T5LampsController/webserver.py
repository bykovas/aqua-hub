from flask import Flask, request, jsonify
from scheduler import Scheduler
from DRF0971driver import *

app = Flask(__name__)

def start_api_server():

    @app.route('/set_values', methods =['POST'])
    def set_values():
        Scheduler.set_demo_mode()
        values = request.json
        ch1 = int(values['Ch1'])
        ch2 = int(values['Ch2'])
        dac.set_dac_out_voltage(ch1 / 10, CHANNEL_0)
        dac.set_dac_out_voltage(ch2 / 10, CHANNEL_1)
        return jsonify({"message": "Demo mode set"}), 200

    @app.route('/get_values', methods=['GET'])
    def get_values():
        values = Scheduler.get_current_values()
        return jsonify({"values": values}), 200

    app.run(port=61354)
    dac = DRF0971Driver()