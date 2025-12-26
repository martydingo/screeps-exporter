import yaml, threading

from .api import API
from .memory import Memory
from .syslog import Syslog


class screeps_exporter:
    def __init__(self, configPath):
        config = self.loadConfig(configPath)
        screepsApi = API(config).api

        threads = []

        mem_t = threading.Thread(
            target=self._run_memory,
            args=(config, screepsApi),
            name="memory",
            daemon=True,
        )
        mem_t.start()
        threads.append(mem_t)

        if config["syslog"]["enabled"] == True:
            syslog = Syslog(
                user=config["screeps"]["email"],
                password=config["screeps"]["password"],
                config=config,
            )
            sys_t = threading.Thread(
                target=syslog.start,
                name="syslog",
                daemon=True,
            )
            sys_t.start()
            threads.append(sys_t)

        for thread in threads:
            thread.join()

    def loadConfig(self, path):
        return yaml.full_load(open(path, "r"))

    def _run_memory(self, config, api):
        # If Memory blocks in __init__, this is fine:
        Memory(config=config, api=api)

    async def asyncEntrypoint(self):
        pass
