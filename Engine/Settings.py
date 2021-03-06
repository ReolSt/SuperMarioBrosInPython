import configparser

import os
if os.path.dirname(os.path.abspath(__file__)) == os.getcwd():
    from Singleton import Singleton
else:
    from .Singleton import Singleton

class Settings(metaclass=Singleton):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + "/Settings.ini")

        self.default = config['Default']
        self.sprite = config['Sprite']
        self.audio = config['Audio']
        self.level = config['Level']
        self.ui = config['UI']