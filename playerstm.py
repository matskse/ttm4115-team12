from stmpy import Machine, Driver
import simpleaudio as sa
        
class Player:

    t0 = {'source': 'initial', 'target': 'ready'}
    t1 = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}
    t2 = {'trigger': 'done', 'source': 'playing', 'target': 'ready'}

    s_playing = {'name': 'playing', 'do': 'play()', 'start': 'defer'}

    def __init__(self, driver):
        self.stm_player = Machine(name='stm_player', transitions=[self.t0, self.t1, self.t2], states=[self.s_playing], obj=self)
        self.driver = driver
        self.driver.add_machine(self.stm_player)
        self.fileName = 'input.wav'
        self.play_obj = None

    def play(self):
        self.wave_obj = sa.WaveObject.from_wave_file(self.fileName)
        self.play_obj = self.wave_obj.play()
        self.play_obj.wait_done()
        self.play_obj.stop()
        print("finished playing sound")
        self.driver.send('message_played', 'stm')

    def play_sound_file(self, fileName):
        self.fileName = fileName
        self.driver.send('start', 'stm_player')
    
    def stop_playing_sound(self):
        if self.play_obj is not None:
            self.play_obj.stop()

