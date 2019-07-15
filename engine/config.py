# config.py
"""
######################################################
#CONFIG MUST BE PROVIDED BY THE FRONT-END APPLICATION#
######################################################

Configuration and application file system locations:

This should all be in the CLI application - not the library.
We need an interface in the library which expects these variables.

Linux
-----

configuration:              ~/.config/bcompiler-engine/config.ini
cache/serialized data:      ~/.bcompiler-engine-data
document drop directory:    AS PER CONFIG.INI
                            AS PER CONFIG.INI

Mac
---

configuration:              ~/Library/Application Support/bcompiler-engine/config.ini
cache/serialized data:      ~/.bcompiler-engine-data
document drop directory:    AS PER CONFIG.INI
                            AS PER CONFIG.INI

Windows
-------

configuration:              ~/Library/Application Support/bcompiler-engine/config.ini
cache/serialized data:      ~/.bcompiler-engine-data
document drop directory:    AS PER CONFIG.INI
                            AS PER CONFIG.INI

"""

import os
import sys
from configparser import ConfigParser
from pathlib import Path

import appdirs

from .exceptions import MissingConfigurationException

# this gets replaced once the application registers its config class
USER_CONFIG = None


class Config:
    """This is created in the application and passed to the library.

    To be subclassed by the application.
    """

    USER_NAME = os.getlogin()
    USER_HOME = Path.home()

    config_parser = ConfigParser()

    BCOMPILER_LIBRARY_DATA_DIR = Path(
        appdirs.user_data_dir("bcompiler-data", USER_NAME))
    BCOMPILER_LIBRARY_CONFIG_DIR = Path(appdirs.user_config_dir("bcompiler"))
    BCOMPILER_LIBRARY_CONFIG_FILE = Path(BCOMPILER_LIBRARY_CONFIG_DIR /
                                         "config.ini")

    @classmethod
    def initialise(cls):
        if not Path(cls.BCOMPILER_LIBRARY_DATA_DIR).exists():
            Path.mkdir(cls.BCOMPILER_LIBRARY_DATA_DIR)
        if not Path(cls.BCOMPILER_LIBRARY_CONFIG_DIR).exists():
            Path.mkdir(cls.BCOMPILER_LIBRARY_CONFIG_DIR)
        if not Path(cls.BCOMPILER_LIBRARY_CONFIG_FILE).exists():
            with open(cls.BCOMPILER_LIBRARY_CONFIG_FILE, "w") as f:
                f.write("[BASE]\n")
                f.write("version=0.1.0\n")


def register_config(config_class):
    if not issubclass(config_class, Config):
        raise MissingConfigurationException(
            "Your config class must inherit from engine.config.Config")
    setattr(sys.modules[__name__], "USER_CONFIG", config_class)
