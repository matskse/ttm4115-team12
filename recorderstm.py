from stmpy import Machine, Driver
from os import system
import os
import time
import pyaudio
import wave

class Recorder:

    t0 = {'source': 'initial', 'target': 'ready'}
    t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
    t2 = {'trigger': 'done', 'source': 'recording', 'target': 'processing'}
    t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}

    s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()"}
    s_processing = {'name': 'processing', 'do': 'process()'}

    def __init__(self, driver):
        self.recording = False
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.filename = "output.wav"
        self.p = pyaudio.PyAudio()
        self.stm_recorder = Machine(name='stm_recorder', transitions=[self.t0, self.t1, self.t2, self.t3], states=[self.s_recording, self.s_processing], obj=self)
        self.driver = driver
        self.driver.add_machine(self.stm_recorder)
        
    def record(self):
        print("Starting to record")
        self.stream = self.p.open(format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True)
        self.frames = []
        self.recording = True
        while self.recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
    def stop(self):
        print("Recording stopped")
        self.recording = False
    
    def process(self):
        print("Saving sound file")
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.driver.send('recording_saved', 'stm')
    
    def start_recording(self):
        self.driver.send('start', 'stm_recorder')
    
    def stop_recording(self):
        self.driver.send('done', 'stm_recorder')