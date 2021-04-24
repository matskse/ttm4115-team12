import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
from stmpy import Machine, Driver
from os import system
from FileSender import FileSenderComponent
from FileReceiver import FileReceiverComponent
from appJar import gui
from recorderstm import Recorder
import time
from playerstm import Player

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class WalkieTalkie:
    
    t0 = {
        'source': 'initial', 
        'target': 'idle'
    }

    t1 =  {
        'trigger': 'message',
        'source': 'idle',
        'target': 'play_message'
    }

    t2 = {
        'trigger': 'cancel_btn', 
        'source': 'play_message',
        'target': 'idle',
    }

    t3 = {
        'trigger': 'message_played',
        'source': 'play_message', 
        'target': 'idle',
    }

    t4 = {
        'trigger': 'manage_btn', 
        'source': 'idle',
        'target': 'manage_groups', 
    }

    t5 = {
        'trigger': 'cancel_btn', 
        'source': 'manage_groups',
        'target': 'idle',
    }

    t6 = {
        'trigger': 'select_btn', 
        'source': 'idle',
        'target': 'select_group', 
    }

    t7 = {
        'trigger': 'cancel_btn', 
        'source': 'select_group',
        'target': 'idle', 
    }

    t8 = {
        'trigger': 'record_btn', 
        'source': 'idle',
        'target': 'record_message',
    }

    t9 = {
        'trigger': 'cancel_btn', 
        'source': 'record_message',
        'target': 'idle', 
    }

    t10 = {
        'trigger': 'record_btn', 
        'source': 'select_group',
        'target': 'record_message', 
    }

    t11 = {
        'trigger': 'record_btn', 
        'source': 'record_message',
        'target': 'send_message', 
    }

    t12 = {
        'trigger': 'message_sent', 
        'source': 'send_message',
        'target': 'idle', 
    }

    t13 = {
        'trigger': 'error_message', 
        'source': 'idle',
        'target': 'error',
        'effect': 'start_timer("t2", 120000)', 
    }

    t14 = {
        'trigger': 'error_message', 
        'source': 'select_group',
        'target': 'error',
    }
    t15 = {
        'trigger': 'error_message', 
        'source': 'record_message',
        'target': 'error',
    }
    t16 = {
        'trigger': 'error_message', 
        'source': 'send_message',
        'target': 'error',
    }

    t17 = {
        'trigger': 'error_message', 
        'source': 'manage_groups',
        'target': 'error',
    }

    t18 = {
        'trigger': 'connection_ok', 
        'source': 'error',
        'target': 'idle',
    }

    t19 = {
        'trigger': 't2',
        'source': 'error',
        'target': 'system_crash',
    }

    t20 = {
        'trigger': 't1', 
        'source': 'error',
        'target': 'error'
    }

    t21 = {
        'trigger': 'done',
        'source': 'system_crash', 
        'target': 'idle'
    }

    idle = {
        'name': 'idle', 
        'entry': 'idle_state'
    }

    play_message = {
        'name': 'play_message',
        'entry': 'play_message_f',
        'message': 'defer',
        'error_message': 'defer'
    }

    manage_groups = {
        'name': 'manage_groups',
        'join': 'join_group',
        'delete': 'leave_group',
        'message': 'defer'
    }

    select_group = {
        'name': 'select_group',
        'entry': 'record_receiver',
        'message': 'defer'
    }

    record_message = {
        'name': 'record_message',
        'entry': 'record_message_f',
        'message': 'defer',
    }

    send_message = {
        'name': 'send_message',
        'entry': 'send_message_f',
        'message': 'defer'
    }

    error = {
        'name': 'error',
        'entry': 'test_connection; start_timer("t1", 3000); display_error_message'
    }

    system_crash = {
        'name': 'system_crash',
        'do': 'speak(*)'
    }
    
    def __init__(self):
        
        #MQTT
        self.MQTT_BROKER = 'mqtt.item.ntnu.no'
        self.MQTT_PORT = 1883
        self.topic_output = 'ttm4115/team_12/file'
        self.group_topics_base = 'ttm4115/team_12/groups/'
        self.voice_file_name = 'output.wav'
        self.joined_groups = []
        self.recipient_groups = []
        self.all_groups = {"Doctors":False, "Nurses":False, "Surgeons":False,"Head Surgeon":False, "Janitors":False}
        
        self.stm = Machine(name='stm', transitions=[self.t0, self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8, self.t9, self.t10, self.t11, self.t12, self.t13, self.t14, self.t15, self.t16, self.t17, self.t18, self.t19, self.t20, self.t21], states=[self.idle, self.play_message, self.manage_groups, self.select_group, self.record_message, self.send_message, self.error, self.system_crash], obj=self)
        self.driver = Driver()
        self.driver.add_machine(self.stm)
        self.driver.start()

        #Voice recording
        self.Recorder = Recorder(self.driver)
        self.recording = False

        #Message playing
        self.player = Player(self.driver)

        #File sending
        self.FileSender = FileSenderComponent(self.driver, self.MQTT_BROKER, self.MQTT_PORT)

        #File receiving
        self.FileReceiver = FileReceiverComponent(self.driver, self.MQTT_BROKER, self.MQTT_PORT)

        self.create_gui()

    def create_gui(self):
        self.app = gui()
        self.app.setSize(500, 500)

        self.app.startLabelFrame('Record Message')
        self.app.addButton('Record', self.record_button)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Cancel')
        self.app.addButton('Cancel', self.cancel_button)
        self.app.stopLabelFrame()

        self.app.startFrame("LEFT", row=50, column=0)
        self.app.startLabelFrame('Join Groups')
        self.app.addButton('Join Doctors', self.on_button_pressed_join_groups)
        self.app.addButton('Join Nurses', self.on_button_pressed_join_groups)
        self.app.addButton('Join Surgeons', self.on_button_pressed_join_groups)
        self.app.addLabel("joined_groups_title", "Joined Groups")
        self.app.addLabel("No Joined Groups")
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("RIGHT", row=50, column=1)
        self.app.startLabelFrame('Leave Groups')
        self.app.addButton('Leave Doctors', self.on_button_pressed_leave_groups)
        self.app.addButton('Leave Nurses', self.on_button_pressed_leave_groups)
        self.app.addButton('Leave Surgeons', self.on_button_pressed_leave_groups)
        self.app.stopLabelFrame()
        self.app.stopFrame()


        self.app.startLabelFrame('Choose Recipient Group')
        self.app.addButton('Send to Doctors', self.on_button_pressed_recipient_group)
        self.app.addButton('Send to Nurses', self.on_button_pressed_recipient_group)
        self.app.addButton('Send to Surgeons', self.on_button_pressed_recipient_group)
        self.app.addLabel("recipient_groups_title", "Recipient Groups")
        self.app.addLabel("No Recipient Groups")
        self.app.stopLabelFrame()
        




        self.app.go()
    
    def record_button(self):
        self.recording = not self.recording
        self.set_record_button_text()
        self.driver.send('record_btn', 'stm')
    
    def cancel_button(self):
        if self.recording:
            self.Recorder.stop_recording()
            self.recording = False
            self.set_record_button_text()
        self.player.stop_playing_sound()
        self.driver.send('cancel_btn', 'stm')
    
    def on_button_pressed_join_groups(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        self.join_group(group_name)
    
    def on_button_pressed_leave_groups(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        self.leave_group(group_name)

    
    def on_button_pressed_recipient_group(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        self.choose_recipient_group(group_name)
    
    def set_record_button_text(self):
        if self.recording:
            self.app.setButton('Record', 'Stop and Send')
        else:
            self.app.setButton('Record', 'Record')
        
        

    
    
    def play_message_f(self):
        print("Main state: Play message")
        self.player.play_sound_file(self.voice_file_name)

    def record_message_f(self):
        print("Main state: Record message")
        self.Recorder.start_recording()



    def idle_state(self):
        print("Main state: Idle")

    
    def record_receiver(self):
        #bestem hvem man vil sende til. 
        #gi en error message
        pass

    def send_message_f(self):
        print("Main state: Send message")
        self.Recorder.stop_recording()
        self.recording = False
        for group in self.recipient_groups:
            group_topic = '{0}{1}'.format(self.group_topics_base, group)
            self.FileSender.send_file(self.voice_file_name, group_topic)

    def join_group(self, groupName):
        if not groupName in self.joined_groups:
            print("joining group: {}".format(groupName))
            self.FileReceiver.subscribe_to_topic('{0}{1}'.format(self.group_topics_base, groupName))
            self.joined_groups.append(groupName)
            self.app.setLabel("No Joined Groups", ', '.join(self.joined_groups))
    
    def choose_recipient_group(self, groupName):
        if not groupName in self.recipient_groups:
            self.recipient_groups.append(groupName)
            print("Choosing new recipient group: {}".format(groupName))
            self.app.setLabel("No Recipient Groups", ', '.join(self.recipient_groups))

    def leave_group(self, groupName):
        if groupName in self.joined_groups:
            print("Leaving group: {}".format(groupName))
            self.FileReceiver.unsubscribe_from_topic('{0}{1}'.format(self.group_topics_base, groupName))
            self.joined_groups.remove(groupName)
            self.app.setLabel("No Joined Groups", ', '.join(self.joined_groups))
    
    def test_connection(self):
        #teste tilkoblingen. 
        pass

    


walkieTalkie = WalkieTalkie()
