import paho.mqtt.client as mqtt

class FileReceiverComponent:

    def on_message(self, client, userdata, msg):
        print("file received")
        file_name = 'input{}.wav'.format(self.message_index)
        self.message_index += 1
        f = open(file_name, 'wb')
        f.write(msg.payload)
        f.close()
        self.driver.send('message', 'stm')
    
    def on_connect(self, client, userdata, flags, rc):
        print('File receiver connected')
        self.connected = True
    
    def on_disconnect(self, client, userdata, rc):
        print('File receiver disconnected')
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

        self.message_index = 0
    
    def subscribe_to_topic(self, topic):
        self.mqtt_client.subscribe(topic, 0)
        print("subscribed, sends subscribed to stm")
        self.driver.send('subscribed', 'stm')
    
    def unsubscribe_from_topic(self, topic):
        self.mqtt_client.unsubscribe(topic, 0)
        print("unsubscribed, sends unsubscribed to stm")
        self.driver.send('unsubscribed', 'stm')
    

    def disconnect(self):
        self.mqtt_client.disconnect()
            
