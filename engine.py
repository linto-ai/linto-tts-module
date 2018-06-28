import os
import json
import datetime
from queue import Queue
import configparser
from threading import Thread
import subprocess

class Condition:
    """ 
    Simple condition to be shared between threads
    """
    state = True

class TTSEngine(Thread):
    def __init__(self, text_queue: Queue, condition: Condition, manager):
        Thread.__init__(self)
        self.condition = condition
        self.text_queue = text_queue
        self.manager = manager

    def run(self):
        while self.condition.state:
            text = self.text_queue.get()
            payload = "{\"on\":\"%s\", \"value\":\"%s\"}" % (datetime.datetime.now().isoformat(), text)
            self.manager.broker.publish('tts/speaking/start', payload)
            process_command = [os.path.dirname(os.path.abspath(__file__)) + "/say.sh", '"%s"' % text]
            subprocess.call(process_command)
            payload = "{\"on\":\"%s\", \"value\":\"%s\"}" % (datetime.datetime.now().isoformat(), text)
            self.manager.broker.publish('tts/speaking/stop', payload)
            self.text_queue.queue.clear() # Prevent accumulation of message (may not stay here)

        print("engine stop")

