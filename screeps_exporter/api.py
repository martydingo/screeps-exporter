import screepsapi


class API:
    def __init__(self, config):
        self.config = config
        self.setupApi()

    def setupApi(self):
        user = self.config["screeps"]["email"]
        token = self.config["screeps"]["token"]

        if token != None:
            self.api = screepsapi.API(u=user, token=token)
            self.api.get()
        else:
            password = self.config["screeps"]["password"]
            self.api = screepsapi.API(u=user, p=password)

        # json.dump( self.api.memory(shard="shard3"), open("memory.json", "w"))
        # memory = json.load(open("memory.json", "r"))
        # Memory(memory=memory["data"])pass
