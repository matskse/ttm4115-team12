import paho.mqtt.client as mqtt

class FileSenderComponent:

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_connect(self, client, userdata, flags, rc):
        print('MQTT connected to {}'.format(client))
    
    def __init__(self, driver, MQTT_BROKER, MQTT_PORT):
        self.mqtt_client = mqtt.Client()
        
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.loop_start()

        self.driver = driver

        
    
    def send_file(self, fileName, topic):
        print('Sending file: {} to topic: {}'.format(fileName, topic))
        f = open(fileName, "rb")
        binaryString = f.read()
        f.close()
        byteArray = bytearray(binaryString)
        
        self.mqtt_client.publish(topic, payload=byteArray, qos=0)

        self.driver.send('message_sent', 'stm')
        