from stmpy import Machine, Driver
from os import system

import logging
debug_level = logging.DEBUG
logger = logging.getLogger('stmpy')
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)



class Speaker:
    def speak(self, string):
        system('say {}'.format(string))

speaker = Speaker()

#t0 = {'source': 'initial', 'target': 'error'}        
t1 = {'trigger': 'timer2', 'source': 'error', 'target': 'system_crash'}
t2 = {'trigger': 'done', 'source': 'system_crash', 'target': 'idle'}

s1 = {'name': 'system_crash', 'do': 'speak(*)', 'timer2': 'defer'}

stm = Machine(name='stm', transitions=[t1, t2], states=[s1], obj=speaker)
speaker.stm = stm

driver = Driver()
driver.add_machine(stm)
driver.start()

driver.send('timer2', 'stm', args=['Fatal error. System crashed'])


driver.wait_until_finished()