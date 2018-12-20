#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
import configparser
import logging
import sys
import json
from queue import Queue
import paho.mqtt.client as mqtt
import tenacity

from linto_tts import DIST_FOLDER
from linto_tts.engine import TTSEngine, Condition

class TTS_Speaker:
    def __init__(self, args):
        self.args = args

        #Thread communication
        self.text_queue = Queue() #Queue for communication between provider and engine
        self.condition = Condition() #Boolean Object to safely stop thread.
        
        #Engine
        self.ttsengine_thread = TTSEngine(self.text_queue, self.condition, args.lang, self)
        self.question = False
        #MQTT broker client
        if args.broker_ip not in ['None', 'none', '']:
            self.broker = self.broker_connect()
        else: 
            self.broker = None

        if self.broker is not None:
            self.broker.on_message = self._on_broker_message
 
    def run(self):
        self.ttsengine_thread.start()
        try:
            self.broker.loop_forever()
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
        logging.info("Attempting connexion to broker at {}:{}".format(self.args.broker_ip, self.args.broker_port))
        try:
            broker = mqtt.Client()
            broker.on_connect = self._on_broker_connect
            broker.connect(self.args.broker_ip, self.args.broker_port, 0)

            return broker
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
        if message.topic in [self.args.broker_topic, self.args.ask_topic]:
            self.question = message.topic == self.args.ask_topic
            if 'value' in msg.keys():
                self.ttsengine_thread.interupt_speech()
                self.text_queue.put(msg['value'])
        elif message.topic == self.args.cancel_topic:
            self.ttsengine_thread.interupt_speech()
        elif message.topic == self.args.lang_topic:
            if 'value' in msg.keys():
                self.ttsengine_thread.change_lang(msg['value'])
        
    def start_speech(self, payload):
        self.broker.publish('tts/speaking/ask' if self.question else 'tts/speaking/start', payload)
    
    def stop_speech(self, payload):
        self.broker.publish('tts/speaking/stop', payload)
    
    def _on_broker_connect(self, client, userdata, flags, rc):
        logging.info("Connected to broker.")
        
        self.broker.subscribe(self.args.broker_topic)
        self.broker.subscribe(self.args.cancel_topic)
        self.broker.subscribe(self.args.lang_topic)
        self.broker.subscribe('lintoclient/ask')
        print(self.args)
        
def main():
    # Logging
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    # Read default config from file
    config = configparser.ConfigParser()
    config_set = 'DEFAULT'
    config.read(os.path.join(DIST_FOLDER, "config.conf"))

    parser = argparse.ArgumentParser(description='Text To Speech Module. Read text from MQTT broker and output it.')
    parser.add_argument('--broker-ip',dest='broker_ip',default=config[config_set]['broker_ip'], help="MQTT Broker IP")
    parser.add_argument('--broker-port', dest='broker_port',default=int(config[config_set]['broker_port']), help='MQTT broker port', type=int)
    parser.add_argument('--broker-topic', dest='broker_topic', default=config[config_set]['broker_topic'], help='Broker on which to publish when the WUW is spotted')
    parser.add_argument('--lang-topic', dest='lang_topic', default=config[config_set]['lang_topic'], help='Broker topic to switch language during runtime')
    parser.add_argument('--cancel-topic', dest='cancel_topic', default=config[config_set]['cancel_topic'], help='Broker topic to switch language during runtime')
    parser.add_argument('--ask-topic', dest='ask_topic', default=config[config_set]['ask_topic'], help='Alternative topic for questions')
    parser.add_argument('-l', dest='lang', default=config[config_set]['lang'], choices=['en-US', 'en-GB', 'fr-FR', 'es-ES', 'de-DE', 'it-IT'], help='Language')
    args = parser.parse_args()
    
    #Instanciate runner
    runner = TTS_Speaker(args)
    runner.run()

if __name__ == '__main__':
    main()
