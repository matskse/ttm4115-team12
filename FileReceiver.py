import paho.mqtt.client as mqtt

class FileReceiverComponent:

    def on_message(self, client, userdata, msg):
        print("file received")
        f = open('input.wav', 'wb')
        f.write(msg.payload)
        f.close()
        self.driver.send('message', 'stm')
    
    def on_connect(self, client, userdata, flags, rc):
        print('MQTT connected to {}'.format(client))
    
    def __init__(self, driver, MQTT_BROKER, MQTT_PORT):
        
        self.mqtt_client = mqtt.Client()
        
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.loop_start()

        self.driver = driver
    
    def subscribe_to_topic(self, topic):
        self.mqtt_client.subscribe(topic, 0)
    
    def unsubscribe_from_topic(self, topic):
        self.mqtt_client.unsubscribe(topic, 0)
