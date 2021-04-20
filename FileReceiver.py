import paho.mqtt.client as mqtt

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_OUTPUT = 'ttm4115/team_12/file'

class FileReceiverComponent:

    def on_message(self, client, userdata, msg):
        print("file received")
        f = open('newTextFile.txt', 'wb')
        f.write(msg.payload)
        f.close()
    
    def on_connect(self, client, userdata, flags, rc):
        print('MQTT connected to {}'.format(client))
    
    def __init__(self):
        
        self.mqtt_client = mqtt.Client()
        
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.loop_start()

        self.mqtt_client.subscribe(MQTT_TOPIC_OUTPUT, 0)

        print("file receiver initiated")
