#!/usr/bin/env python3
import os

import argparse
import json

from linto_tts import DIST_FOLDER

def main():
    parser = argparse.ArgumentParser(description='Text To Speech Config Module. Allow to consult and modify mqtt parameter')
    parser.add_argument('action', help="Either show or set")
    parser.add_argument('--broker-ip',dest='broker_ip', help="MQTT Broker IP")
    parser.add_argument('--broker-port', dest='broker_port', help='MQTT broker port')
    parser.add_argument('--broker-topic', dest='broker_topic', help='Broker on which to publish when the WUW is spotted')
    parser.add_argument('--lang', dest='lang',choices=['en-US', 'en-GB', 'fr-FR', 'es-ES', 'de-DE', 'it-IT'], help='Set the default language.')
    args = parser.parse_args()

    config_file = os.path.join(DIST_FOLDER, "config.conf")
    with open(config_file, 'r') as f:
        lines = f.readlines()
    if args.action == "show":
        for line in [line for line in lines if not line.startswith('[')]:
            print(line.strip())
        return
    elif args.action == "set":

        params = dict()
        for line in [line.strip() for line in lines[1:] if len(line.strip()) >1 ]:
            p, val = line.split('=')
            params[p] = val
        with open(config_file, 'w') as f:
            f.write(lines[0])
            args = vars(args)
            for param in params.keys():
                value = params[param]
                if param in args.keys() and args[param] != None:
                    value = args[param].strip()
                    print("{}<{}".format(param, value))
                f.write("{}={}\n".format(param, value))
            
if __name__ == '__main__':
    main()