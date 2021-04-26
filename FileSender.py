import paho.mqtt.client as mqtt

class FileSenderComponent:

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_connect(self, client, userdata, flags, rc):
        print('File sender connected')
        self.connected = True
    
    def on_disconnect(self, client, userdata, rc):
        print('File sender disconnected')
        self.connected = False
        self.driver.send('error_message', 'stm')
    
    def __init__(self, driver, MQTT_BROKER, MQTT_PORT):
        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.mqtt_client = mqtt.Client()
        
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        self.mqtt_client.loop_start()

        self.driver = driver
        self.connected = False

        
    
    def send_file(self, fileName, topic):
        print('Sending file: {} to topic: {}'.format(fileName, topic))
        f = open(fileName, "rb")
        binaryString = f.read()
        f.close()
        byteArray = bytearray(binaryString)
        
        self.mqtt_client.publish(topic, payload=byteArray, qos=0)

        self.driver.send('message_sent', 'stm')
    
    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        