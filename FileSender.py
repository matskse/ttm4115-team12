import paho.mqtt.client as mqtt

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_12/file'


class FileSenderComponent:

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_connect(self, client, userdata, flags, rc):
        print('MQTT connected to {}'.format(client))
    
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.loop_start()
        print('file sender initiated')

        
    
    def send_file(self):
        print('Sending file...')
        f = open("sampleFile.txt", "rb")
        binaryString = f.read()
        f.close()
        byteArray = bytearray(binaryString)
        
        self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=byteArray, qos=2)
        