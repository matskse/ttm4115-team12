import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui


MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_12/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_12/answer'


class CommandSenderComponent:

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        pass

    def __init__(self):
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')
        self.recording = False

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.create_gui()

    def create_gui(self):
        self.app = gui()

        def build_command(buttonLabel):
            buttonLabel = buttonLabel.lower()
            command = {"command": ""}
            if buttonLabel == 'record':
                if  not self.recording:
                    command = {"command": "record_message"}
                else:
                    command = {"command": "stop_recording"}
            return command


        def extract_group_name(label):
            group_name = label.lower()
            print(group_name)
            if 'doctors' in group_name:
                group_name = 'doctors'
            elif 'nurses' in group_name:
                group_name = 'nurses'
            elif 'surgeons' in group_name:
                group_name = 'surgeons'
            return group_name

        def publish_command(command):
            payload = json.dumps(command)
            self._logger.info(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)

        self.app.startLabelFrame('Record Message')
        
        def on_button_pressed_record(title):
            command = build_command(title)
            publish_command(command)
            title = title.lower()
            if title == 'record':
                self.recording = not self.recording
        
        
        self.app.addButton('Record', on_button_pressed_record)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Join groups')

        def on_button_pressed_join_groups(title):
            group_name = extract_group_name(title)
            command = {"command": "join_group", "name": group_name}
            publish_command(command)

        self.app.addButton('Join Doctors', on_button_pressed_join_groups)
        self.app.addButton('Join Nurses', on_button_pressed_join_groups)
        self.app.addButton('Join Surgeons', on_button_pressed_join_groups)
        
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Leave groups')

        def on_button_pressed_leave_groups(title):
            group_name = extract_group_name(title)
            command = {"command": "leave_group", "name": group_name}
            publish_command(command)

        self.app.addButton('Leave Doctors', on_button_pressed_leave_groups)
        self.app.addButton('Leave Nurses', on_button_pressed_leave_groups)
        self.app.addButton('Leave Surgeons', on_button_pressed_leave_groups)
        
        self.app.stopLabelFrame()

        self.app.go()


    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = CommandSenderComponent()