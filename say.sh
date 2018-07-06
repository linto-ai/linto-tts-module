#!/bin/bash
pico2wave -l fr-FR -w /tmp/say.wav "$1"
aplay -q /tmp/say.wav
rm /tmp/say.wav
