import os
import json
import datetime
import logging
from queue import Queue
import configparser
from threading import Thread
import pyaudio
import wave
import subprocess

logger = logging.getLogger()

class Condition:
    """ 
    Simple condition to be shared between threads
    """
    state = True

class TTSEngine(Thread):
    chunk = 2048
    def __init__(self, text_queue: Queue, condition: Condition, lang, manager):
        Thread.__init__(self)
        self.condition = condition
        self.text_queue = text_queue
        self.manager = manager
        self.playing = False
        self.audio = pyaudio.PyAudio()
        self.lang = lang

    def interupt_speech(self):
        self.playing = False
    
    def change_lang(self, lang: str):
        if lang in ['en-US', 'en-GB', 'fr-FR', 'es-ES', 'de-DE', 'it-IT']:
            self.lang = lang
        else:
            logger.warning("Wrong language argument: {}".format(lang))
            
    def say_text(self, text: str):
        """ Create a wav file using a pico2wave subprocess then play the result using pyaudio

        Keyword arguments:
        text -- sentence to be spoken
        """
        #Create sound file
        logger.debug(text)
        command = ["pico2wave", "-l", self.lang, "-w", "/tmp/speech.wav", text]
        subprocess.call(command)
        command = ["sox", "/tmp/speech.wav", "-r", "44100", "-t", "wav", "/tmp/speech_sample.wav"]
        subprocess.call(command)
        #Play it
        f = wave.open("/tmp/speech_sample.wav")
        while True:
            try:
                stream = self.audio.open(format = self.audio.get_format_from_width(f.getsampwidth()),  
                        channels = f.getnchannels(),  
                        rate = f.getframerate(),  
                        output = True)
            except OSError as e:
                logger.error("Failed to open stream, retrying")
                self.audio = pyaudio.PyAudio()
            else:
                break
        data = f.readframes(self.chunk)
        self.playing = True
        payload = "{\"on\":\"%s\", \"value\":\"%s\"}" % (datetime.datetime.now().isoformat(), text)
        self.manager.start_speech(payload)
        while data and self.playing:
            stream.write(data)
            data = f.readframes(self.chunk)

        payload = "{\"on\":\"%s\", \"value\":\"%s\"}" % (datetime.datetime.now().isoformat(), text)
        self.manager.stop_speech(payload)

        self.playing = False
        stream.stop_stream()
        stream.close()

    def run(self):
        logging.debug("TTS engine started")
        while self.condition.state:
            text = self.text_queue.get()
            logging.debug("Processing input: {}".format(text))
            if not self.condition.state:
                break
            if self.playing:
                self.interupt_speech()
            self.say_text(text)
            
        logging.debug("TTS engine stopped")

