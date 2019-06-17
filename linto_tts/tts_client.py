#!/usr/bin/env python3
import os
import argparse
import logging
import sys
import json
from queue import Queue
import paho.mqtt.client as mqtt
import tenacity

if getattr(sys, 'frozen', False):
    DIST_FOLDER = os.path.dirname(sys.executable)
else:
    DIST_FOLDER = os.path.dirname(__file__)

from engine import TTSEngine, Condition

class TTS_Speaker:
    def __init__(self):
        self.config = dict()
        self.mqtt_config = dict()
        self.load_config()

        #Thread communication
        self.text_queue = Queue() #Queue for communication between provider and engine
        self.condition = Condition() #Boolean Object to safely stop thread.
        
        #Engine
        self.ttsengine_thread = TTSEngine(self.text_queue, self.condition, self.config['TTS_LANG'], self)
        self.question = False

        #MQTT broker client
        self.client = self.broker_connect()

    def load_config(self):
        #Load env_default value
        with open(os.path.join(DIST_FOLDER, '.env_default')) as f:
            lines = f.readlines()
            for line in lines:
                key, value = line.strip().split('=')
                self.config[key] = os.path.expandvars(value)
        
        #override with .env values
        env_path = os.path.join(DIST_FOLDER, '.env')
        if os.path.isfile(env_path):
            with open(env_path) as f:
                lines = f.readlines()
                for line in lines:
                    key, value = line.strip().split('=')
                    if key in self.config.keys():
                        self.config[key] = os.path.expandvars(value)

        #override with ENV value
        for key in [k for k in os.environ.keys() if k in self.config.keys()]:
            value = os.environ[key]
            logging.debug("Overriding value for {} with environement value {}".format(key, value))
            self.config[key] = value
        
        #read mqtt msg config
        with open(os.path.join(DIST_FOLDER, 'mqtt_msg.json')) as f:
            self.mqtt_config = json.load(f)

    def run(self):
        self.ttsengine_thread.start()
        try:
            self.client.loop_forever()
            self.condition.state = False
        except KeyboardInterrupt:
            logging.info("Process interrupted by user")
        finally:
            self.condition.state = False
            self.text_queue.put('')

    @tenacity.retry(wait=tenacity.wait_fixed(5),
                stop=tenacity.stop_after_attempt(24),
                retry=tenacity.retry_if_result(lambda s: s is None),
                retry_error_callback=(lambda s: s.result())
                )
    def broker_connect(self):
        logging.info("Attempting connexion to broker at {}:{}".format(self.config['MQTT_LOCAL_HOST'], int(self.config['MQTT_LOCAL_PORT'])))
        try:
            client = mqtt.Client()
            client.on_connect = self._on_broker_connect
            client.connect(self.config['MQTT_LOCAL_HOST'], int(self.config['MQTT_LOCAL_PORT']), 0)

            return client
        except:
            logging.warning("Failed to connect to broker (Retrying after 5s)")
            return None

    def _on_broker_message(self, client, userdata, message):
        try:
            msg = json.loads(str(message.payload.decode("utf-8")))
        except:
            logging.warning("Failed to load message {}".format(str(message.payload.decode("utf-8"))))
            return
        logging.debug("Received message '{}' from topic {}".format(msg, message.topic))
        if message.topic in self.mqtt_config['input']['say_topics'] or message.topic in self.mqtt_config['input']['ask_topics']:
            self.question = message.topic in self.mqtt_config['input']['ask_topics']
            if 'value' in msg.keys():
                self.ttsengine_thread.interupt_speech()
                self.text_queue.put(msg['value'])
                
        elif message.topic in self.mqtt_config['input']['cancel_topics']:
            self.ttsengine_thread.interupt_speech()
        elif message.topic in self.mqtt_config['input']['set_lang_topic']:
            if 'value' in msg.keys():
                self.ttsengine_thread.change_lang(msg['value'])
        
    def start_speech(self, payload):
        self.client.publish(self.mqtt_config['output']['ask']['topic'] if self.question else self.mqtt_config['output']['start']['topic'], payload)
    
    def stop_speech(self, payload):
        self.client.publish(self.mqtt_config['output']['stop']['topic'], payload)
    
    def _on_broker_connect(self, client, userdata, flags, rc):
        logging.info("Connected to broker.")
        self.client.on_message = self._on_broker_message
        for key in self.mqtt_config['input'].keys():
            for topic in self.mqtt_config['input'][key]:
                self.client.subscribe(topic)
                logging.debug("Subscribed to {}".format(topic))
        
def main():
    parser = argparse.ArgumentParser(description='Text To Speech Module.'
                                                 'Read text from MQTT broker and output it using picotts.')
    parser.add_argument('--debug', action='store_true', help='Prompt debug')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="%(levelname)8s %(asctime)s [TTS] %(message)s")

    #Instanciate runner
    runner = TTS_Speaker()
    runner.run()

if __name__ == '__main__':
    main()
