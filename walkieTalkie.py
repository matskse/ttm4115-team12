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
        'effect': 'stop_playing()'
    }

    t3 = {
        'trigger': 'message_played',
        'source': 'play_message', 
        'target': 'idle',
    }

    t4 = {
        'trigger': 'join_btn', 
        'source': 'idle',
        'target': 'join_group',
        'effect': 'join_group_f(*)' 
    }

    t5 = {
        'trigger': 'error_message', 
        'source': 'join_group',
        'target': 'error',
    }

    t6 = {
        'trigger': 'subscribed', 
        'source': 'join_group',
        'target': 'idle',
    }

    t7 = {
        'trigger': 'leave_btn', 
        'source': 'idle',
        'target': 'leave_group',
        'effect': 'leave_group_f(*)'
    }

    t8 = {
        'trigger': 'error_message', 
        'source': 'leave_group',
        'target': 'error',
    }

    t9 = {
        'trigger': 'unsubscribed', 
        'source': 'leave_group',
        'target': 'idle',
    }

    t10 = {
        'trigger': 'recipient_btn', 
        'source': 'idle',
        'target': 'select_group', 
        'effect': 'choose_recipient_group(*)'
    }

    t11 = {
        'trigger': 'leave_recipient_btn', 
        'source': 'idle',
        'target': 'select_group', 
        'effect': 'remove_recipient_group(*)'
    }


    t12 = {
        'trigger': 't1', 
        'source': 'select_group',
        'target': 'idle',
    }
    

    t13 = {
        'trigger': 'cancel_btn', 
        'source': 'select_group',
        'target': 'idle', 
    }

    t14 = {
        'trigger': 'record_btn', 
        'source': 'idle',
        'target': 'record_message',
    }

    t15 = {
        'trigger': 'cancel_btn', 
        'source': 'record_message',
        'target': 'idle', 
    }

    t16 = {
        'trigger': 'record_btn', 
        'source': 'select_group',
        'target': 'record_message', 
    }

    t17 = {
        'trigger': 'recording_saved', 
        'source': 'record_message',
        'target': 'send_message', 
    }

    t18 = {
        'trigger': 'message_sent', 
        'source': 'send_message',
        'target': 'idle', 
    }

    t19 = {
        'trigger': 'error_message', 
        'source': 'idle',
        'target': 'error', 
    }

    t20 = {
        'trigger': 'error_message', 
        'source': 'select_group',
        'target': 'error',
    }
    t21 = {
        'trigger': 'error_message',
        'source': 'record_message',
        'target': 'error',
    }
    t22 = {
        'trigger': 'error_message', 
        'source': 'send_message',
        'target': 'error',
    }

    t23 = {
        'trigger': 'error_message', 
        'source': 'manage_groups',
        'target': 'error',
    }

    t24 = {
        'trigger': 'connection_ok', 
        'source': 'error',
        'target': 'idle',
    }

    #states

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

    join_group = {'name': 'join_group', 'message': 'defer'}

    leave_group = {'name': 'leave_group', 'message': 'defer'}


    select_group = {
        'name': 'select_group',
        'entry': 'start_timer("t1", 1000)',
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
        'entry': 'test_connection;'
    }

    
    
    def __init__(self):
        
        #MQTT
        self.MQTT_BROKER = 'mqtt.item.ntnu.no'
        self.MQTT_PORT = 1883
        self.topic_output = 'ttm4115/team_12/file'
        self.group_topics_base = 'ttm4115/team_12/groups/'
        self.voice_file_name = 'output.wav'
        self.message_file_name_base = 'input.wav'
        self.joined_groups = []
        self.recipient_groups = []
        self.all_groups = {"Doctors":False, "Nurses":False, "Surgeons":False,"Head Surgeon":False, "Janitors":False}
        
        self.recording = False

        #State machine
        self.stm = Machine(name='stm', transitions=[self.t0, self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8, self.t9, self.t10, self.t11, self.t12, self.t13, self.t14, self.t15, self.t16, self.t17, self.t18, self.t19, self.t20, self.t21, self.t21, self.t22, self.t23, self.t24], states=[self.idle, self.play_message, self.join_group, self.leave_group, self.select_group, self.record_message, self.send_message, self.error], obj=self)
        self.driver = Driver()
        self.driver.add_machine(self.stm)
        self.driver.start()

        #Voice recording
        self.Recorder = Recorder(self.driver)

        #Message playing
        self.player = Player(self.driver)

        #File sending
        self.FileSender = FileSenderComponent(self.driver, self.MQTT_BROKER, self.MQTT_PORT)

        #File receiving
        self.FileReceiver = FileReceiverComponent(self.driver, self.MQTT_BROKER, self.MQTT_PORT)

        #Errors
        self.error_message = 'ERROR: Connection lost'

        self.message_index = 0

        self.create_gui()

    def create_gui(self):
        self.app = gui()
        self.app.setSize(600, 620)
        self.app.setBg('white', override=False, tint=False)

        self.app.startFrame("record", row=0, column=0)
        self.app.startLabelFrame('Record Message')
        self.app.addButton('Record', self.record_button)
        self.app.addButton('Save and Send recording', self.stop_recording)
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("cancel", row=0, column=1)
        self.app.startLabelFrame('Cancel')
        self.app.addButton('Cancel', self.cancel_button)
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("join_groups", row=20, column=0)
        self.app.startLabelFrame('Join Groups')
        self.app.addButton('Join Doctors', self.on_button_pressed_join_groups)
        self.app.addButton('Join Nurses', self.on_button_pressed_join_groups)
        self.app.addButton('Join Surgeons', self.on_button_pressed_join_groups)
        self.app.addButton('Join Important Information', self.on_button_pressed_join_groups)
        self.app.addLabel("joined_groups_title", "Joined Groups")
        self.app.addLabel("No Joined Groups")
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("choose_recipient", row=40, column=0)
        self.app.startLabelFrame('Choose Recipient Group')
        self.app.addButton('Send to Doctors', self.on_button_pressed_recipient_group)
        self.app.addButton('Send to Nurses', self.on_button_pressed_recipient_group)
        self.app.addButton('Send to Surgeons', self.on_button_pressed_recipient_group)
        self.app.addButton('send to Important', self.on_button_pressed_recipient_group)
        self.app.addLabel("recipient_groups_title", "Recipient Groups")
        self.app.addLabel("No Recipient Groups")
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("leave_group", row=20, column=1)
        self.app.startLabelFrame('Leave Groups')
        self.app.addButton('Leave Doctors', self.on_button_pressed_leave_groups)
        self.app.addButton('Leave Nurses', self.on_button_pressed_leave_groups)
        self.app.addButton('Leave Surgeons', self.on_button_pressed_leave_groups)
        self.app.addButton(' Leave Important information', self.on_button_pressed_leave_groups)
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("remove_recipient", row=40, column=1)
        self.app.startLabelFrame('Remove Recipient Groups')
        self.app.addButton('Remove Doctors', self.on_button_pressed_remove_groups)
        self.app.addButton('Remove Nurses', self.on_button_pressed_remove_groups)
        self.app.addButton('Remove Surgeons', self.on_button_pressed_remove_groups)
        self.app.addButton('Remove Important Information', self.on_button_pressed_remove_groups)
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.startFrame("error_display", row=60, column=1)
        self.app.startLabelFrame('Error Display')
        self.app.addLabel("error_label", "No errors")
        self.app.addButton('Simulate connection lost', self.simulate_connection_lost)
        self.app.stopLabelFrame()
        self.app.stopFrame()

        self.app.go()
    
    def record_button(self):
        if len(self.recipient_groups) == 0:
            print("No recipient groups to send to")
            return
        self.recording = True
        self.driver.send('record_btn', 'stm')
    
    def cancel_button(self):
        #self.player.stop_playing_sound()
        self.driver.send('cancel_btn', 'stm')
    
    def stop_playing(self):
        self.player.stop_playing_sound()
    
    def on_button_pressed_join_groups(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        elif 'important' in group_name:
            group_name = 'important'
        #self.join_group(group_name)
        if group_name not in self.joined_groups:
            self.driver.send('join_btn', 'stm', args=[group_name])
        else : 
            pass

    def on_button_pressed_leave_groups(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        elif 'important' in group_name:
            group_name = 'important'
        #self.leave_group(group_name)
        if group_name in self.joined_groups:
            self.driver.send('leave_btn', 'stm', args=[group_name])
        else: 
            pass
    
    def on_button_pressed_recipient_group(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        elif 'important' in group_name:
            group_name = 'important'
        #self.choose_recipient_group(group_name)
        self.driver.send('recipient_btn', 'stm', args=[group_name])
    
    def on_button_pressed_remove_groups(self, buttonTitle):
        group_name = buttonTitle.lower()
        if 'doctors' in group_name:
            group_name = 'doctors'
        elif 'nurses' in group_name:
            group_name = 'nurses'
        elif 'surgeons' in group_name:
            group_name = 'surgeons'
        elif 'important' in group_name:
            group_name = 'important'
        #self.remove_recipient_group(group_name)
        self.driver.send('leave_recipient_btn', 'stm', args=[group_name])
    
    def set_record_button_text(self):
        if self.recording:
            self.app.setButton('Record', 'Stop and Send')
        else:
            self.app.setButton('Record', 'Record')
    
    def simulate_connection_lost(self):
        print('Simulating connection lost')
        self.FileSender.disconnect()
        
        

    
    
    def play_message_f(self):
        print("Main state: Play message")
        next_file_name = 'input{}.wav'.format(self.message_index)
        self.player.play_sound_file(next_file_name)
        self.message_index += 1

    def record_message_f(self):
        print("Main state: Record message")
        self.Recorder.start_recording()



    def idle_state(self):
        print("Main state: Idle")
        if self.recording:
            self.Recorder.stop_recording()
            self.recording = False
            self.set_record_button_text()

    

    def send_message_f(self):
        print("Main state: Send message")
        for group in self.recipient_groups:
            group_topic = '{0}{1}'.format(self.group_topics_base, group)
            self.FileSender.send_file(self.voice_file_name, group_topic)
    
    def stop_recording(self):
        self.Recorder.stop_recording()
        self.recording = False
        self.set_record_button_text()

    def join_group_f(self, groupName):
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
    
    def remove_recipient_group(self, groupName):
        if groupName in self.recipient_groups:
            print("Removing group: {}".format(groupName))
            self.recipient_groups.remove(groupName)
            self.app.setLabel("No Recipient Groups", ', '.join(self.recipient_groups))

    def leave_group_f(self, groupName):
        if groupName in self.joined_groups:
            print("Leaving group: {}".format(groupName))
            self.FileReceiver.unsubscribe_from_topic('{0}{1}'.format(self.group_topics_base, groupName))
            self.joined_groups.remove(groupName)
            self.app.setLabel("No Joined Groups", ', '.join(self.joined_groups))
    
    def test_connection(self):
        print('Testing connection')
        if self.FileReceiver.connected and self.FileSender.connected:
            self.driver.send('connection_ok', 'stm')
            self.app.setLabel("error_label", 'No errors')
            self.app.setLabelBg("error_label", 'white')
            print('Connection ok')
        else:
            self.app.setLabel("error_label", self.error_message)
            self.app.setLabelBg("error_label", 'red')
            print('Connection lost, resetting components and reconnecting')
            self.FileReceiver = FileReceiverComponent(self.driver, self.MQTT_BROKER, self.MQTT_PORT)
            self.FileSender = FileSenderComponent(self.driver, self.MQTT_BROKER, self.MQTT_PORT)

    


walkieTalkie = WalkieTalkie()
