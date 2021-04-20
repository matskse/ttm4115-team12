import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
from stmpy import Machine, Driver
from os import system

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/answer'

#test
#test
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


class WalkieTalkie: 
    """"
    state machine for walkie talkie

    """"
    def __init__(self):
        #display user interface
    

    def play_message_f(self):
        #spill av melding når message innkommer
        #gi en error message

    def record_message_f(self):
        #spill inn lyd. 
        #gi en error messafe

    def show_main_menu(self):
        #start meny som kan vises. La inn denne selv i etter tid, kan ha med hvis vi vil. 

    
    def record_receiver(self):
        #bestem hvem man vil sende til. 
        #gi en error message

    def send_message_f(self):
        #send meldingen som er recorded i record message. 
        #send til den som er bestem i record receiver
        #må gi en error message
    

    def join_group(self):
        #bli med i en grupp
        #kan implementeres med en speech to text funksjon¨
    

    def delete_group(self):
        #fjerne seg fra en gruppe
        #kan også implementeres med en speec to text 
    
    
    def test_connection(self):
        #teste tilkoblingen. 



walkieTalkie = WalkieTalkie()

#transitions
#initial transistion
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


#the states

idle = {
    'name': 'idle', 
    'entry': 'show_main_menu'
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
    'delete': 'delete_group',
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
    'message': 'defer'
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

stm = Machine(name='stm', transistions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16, t17, t18, t19, t20, t21],
    states=[idle, play_message, manage_groups, select_group, record_message, send_message, error, system_crash], obj=walkieTalkie)

walkieTalkie.stm = stm
driver = Driver()
driver.add_machine(stm)
driver.start()

driver.send('t2', 'stm', args=['Fatal error, system crashed'])
driver.wait_until_finished()
