# linto-tts-module

The goal of this project is to provide a voice to LinTO through Pico.
It communicates with the system via an MQTT local bus.

### Before starting

The following libraries (and APIs) are necessary for the proper functioning of the program:

* Pico :
```
sudo apt-get install libttspico-utils
```

### Use

Configuration data are available in the config.conf file.
To start the program, just run the Python script using
```
/usr/bin/python3 tts_speaker.py
```

```
./tts_speaker.py
```
