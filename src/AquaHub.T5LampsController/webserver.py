from flask import Flask, request, jsonify
from flask_cors import CORS
from schedule import Schedule
from DRF0971driver import *

app = Flask(__name__)
CORS(app)
dac = DRF0971Driver()

def start_api_server():

    @app.route('/set_values', methods =['POST'])
    def set_values():
        Schedule.set_demo_mode()
        values = request.json
        ch1 = int(values['Ch1'])
        ch2 = int(values['Ch2'])
        dac.set_dac_out_voltage(ch1, CHANNEL_0)
        dac.set_dac_out_voltage(ch2, CHANNEL_1)
        return jsonify({"message": "Demo mode set"}), 200

    @app.route('/get_values', methods=['GET'])
    def get_values():
        values = Schedule.get_current_values()
        return jsonify({"values": values}), 200

    app.run(host='0.0.0.0', port=5000)   