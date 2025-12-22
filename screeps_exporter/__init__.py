import yaml

from .api import API
from .memory import Memory


class screeps_exporter:
    def __init__(self, configPath):
        config = self.loadConfig(configPath)

        screepsApi = API(config).api

        Memory(config=config, api=screepsApi)

    def loadConfig(self, path):
        return yaml.full_load(open(path, "r"))
