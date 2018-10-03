#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="linto_tts",
    version="0.1.0",
    include_package_data=True,
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['linto_tts=linto_tts.linto_tts:main',],
    },
    install_requires=[],
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