import os
import json
import datetime
from queue import Queue
import configparser
from threading import Thread
import pyaudio
import wave
import subprocess

class Condition:
    """ 
    Simple condition to be shared between threads
    """
    state = True

class TTSEngine(Thread):
    chunk = 1024
    def __init__(self, text_queue: Queue, condition: Condition, manager):
        Thread.__init__(self)
        self.condition = condition
        self.text_queue = text_queue
        self.manager = manager
        self.playing = False
        self.audio = pyaudio.PyAudio()

    def interupt_speech(self):
        self.playing = False
            
    def say_text(self, text: str):
        """ Create a wav file using a pico2wave subprocess then play the result using pyaudio


        Keyword arguments:
        text -- sentence to be spoken
        """
        #Create sound file
        command = ["pico2wave", "-l", "fr-FR", "-w", "/tmp/test.wav", text]
        subprocess.call(command)

        #Play it
        f = wave.open("/tmp/test.wav")
        stream = self.audio.open(format = self.audio.get_format_from_width(f.getsampwidth()),  
                channels = f.getnchannels(),  
                rate = f.getframerate(),  
                output = True)

        data = f.readframes(self.chunk)
        self.playing = True
        payload = "{\"on\":\"%s\", \"value\":\"%s\"}" % (datetime.datetime.now().isoformat(), text)
        self.manager.broker.publish('tts/speaking/start', payload)
        while data and self.playing:
            stream.write(data)
            data = f.readframes(self.chunk)

        payload = "{\"on\":\"%s\", \"value\":\"%s\"}" % (datetime.datetime.now().isoformat(), text)
        self.manager.broker.publish('tts/speaking/stop', payload)

        self.playing = False
        stream.stop_stream()
        stream.close()

    def run(self):
        while self.condition.state:
            text = self.text_queue.get()
            if not self.condition.state:
                break
            if self.playing:
                self.interupt_speech()
            self.say_text(text)
            
        print("TTS engine stopped")

