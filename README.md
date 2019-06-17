# linto-tts-module

The goal of this project is to provide a voice to LinTO Maker through Pico.
It communicates the other elements using MQTT protocol.

## Introduction
linto-tts-module a communication layer meant to provide a voice by reading MQTT messages 
from a dedicated topic and synthezing speech using picotts and sox.

-----

## Getting started

### Dependencies

The following dependencies are required: picotts and sox.

```

sudo apt-get install libttspico-utils sox
```

### Installation
Two option tu use the tts-module:
* Use the binary release package
* Download the repository and use it as it is.

### Binary
It is a binary built using pyinstaller that comes with all python dependecies included.
* x86_64: [Here](https://github.com/linto-ai/linto-tts-module/releases/download/v0.2/linto_tts-0.1-x86_64.tar.gz)
* Armv7l: [Here](https://github.com/linto-ai/linto-tts-module/releases/download/v0.2/linto_tts-0.1-armv7l.tar.gz)

-----

### From source
Download the repository
```bash
git clone https://github.com/linto-ai/linto-tts-module
```
Several python library are required:
```bash
#[Virtual environment if you want it]
pip install pyaudio wave paho-mqtt tenacity
```

### Usage

```
usage: {linto_tts|tts_client.py} [-h] [--debug]

Text To Speech Module. Read text from MQTT broker and output it using picotts.

optional arguments:

  -h, --help  show this help message and exit

  --debug     Prompt debug

```

The executable comes alongside a .env_default file that contains its parameters.
You can override those parameters using a .env file and you can overide those formers by using environment variables.

**Parameters are:**
* TT_LANG: Language to be used by pico. Supported languages are ['en-US', 'en-GB', 'fr-FR', 'es-ES', 'de-DE', 'it-IT'] (default fr-FR)
* MQTT_LOCAL_HOST: MQTT local broker address (default localhost)
* MQTT_LOCAL_PORT: MQTT local broker port (default 1883)

Exemple:
```
echo TTS_LANG=en-US > .env && ./linto_tts --debug
            or
TTS_LANG=en-UK ./command --debug
```

## Built using

* [Tenacity](https://github.com/jd/tenacity) - General-purpose retrying library
* [paho-mqtt](https://pypi.org/project/paho-mqtt/) - MQTT client library.


## License

This project is licensed under the GNU AFFERO License - see the [LICENSE.md](LICENSE.md) file for details.

