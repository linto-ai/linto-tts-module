#!/usr/bin/env python3
from setuptools import setup, find_packages
import json

man = json.load(open('manifest.json'))
setup(
    name="linto_tts",
    version=man['version'],
    include_package_data=True,
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['linto_tts=linto_tts.tts_client:main',
                            'linto_tts_conf=linto_tts.tts_config:main'],
    },
    install_requires=[
        "tenacity>=5.0.2",
        "paho-mqtt>=1.4.0",
        "Wave>=0.0.2"
    ],
    package_data={},
    author="Rudy Baraglia",
    author_email="baraglia.rudy@gmail.com",
    description="linto_tts is an engine to produce voice from a text using pico2wave. It listen for a mqtt message contening text to be spoken.",
    license="AGPL V3",
    keywords="tts linto mqtt",
    url="",
    project_urls={
        "github" : ""
    },
    long_description="Refer to README"
)
