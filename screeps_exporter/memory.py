from prometheus_client import Gauge, Enum, start_http_server
from time import sleep


class Memory:
    def __init__(self, config, api):
        self.api = api
        self.config = config

        self.createMetrics()

        # if __name__ == "__main__":
        # Start up the server to expose the metrics.
        start_http_server(8000)
        # Generate some requests.
        try:
            while True:
                self.pollMetrics()

        except KeyboardInterrupt:
            exit()

    def pollMemory(self):
        return self.api.memory(shard=self.config["screeps"]["shard"])["data"]

    def createMetrics(self):
        self.metrics = {}

        memory = self.pollMemory()

        self.roomMemory = memory["rooms"]
        self.spawnMemory = memory["spawns"]
        self.jobMemory = memory["jobs"]
        self.creepMemory = memory["creeps"]

        self.createRoomMetrics()

    def createRoomMetrics(self):
        self.createRoomEnergyMetrics()
        self.createRoomSourceMetrics()
        self.createRoomControllerMetrics()

    def createRoomEnergyMetrics(self):
        self.metrics["energy"] = {}

        self.metrics["energy"]["amount"] = Gauge(
            "screeps_room_energy_amount",
            documentation="The amount of energy in a room for use by spawners and extensions",
            labelnames=["room"],
        )

        self.metrics["energy"]["capacity"] = Gauge(
            "screeps_room_energy_capacity",
            documentation="The total capacity of energy in a room for use by spawners and extensions",
            labelnames=["room"],
        )

        for roomName in self.roomMemory:
            try:
                energyData = self.roomMemory[roomName]["energy"]
                self.metrics["energy"]["amount"].labels(room=roomName)
                self.metrics["energy"]["capacity"].labels(room=roomName)

            except KeyError:
                pass

    def createRoomSourceMetrics(self):
        self.metrics["sources"] = {}
        self.metrics["sources"]["amount"] = Gauge(
            "screeps_source_amount",
            documentation="The amount of energy remaining for a given energy source",
            labelnames=["room", "source"],
        )
        self.metrics["sources"]["capacity"] = Gauge(
            "screeps_source_capacity",
            documentation="The total capacity of energy for a given energy source",
            labelnames=["room", "source"],
        )
        self.metrics["sources"]["regeneration"] = Gauge(
            "screeps_source_regeneration",
            documentation="The regeneration timer for a given energy source to replete",
            labelnames=["room", "source"],
        )

        for roomName in self.roomMemory:
            try:
                sourceData = self.roomMemory[roomName]["sources"]
                for sourceId in sourceData:
                    self.metrics["sources"]["amount"].labels(
                        room=roomName, source=sourceId
                    )
                    self.metrics["sources"]["capacity"].labels(
                        room=roomName, source=sourceId
                    )
                    self.metrics["sources"]["regeneration"].labels(
                        room=roomName, source=sourceId
                    )

            except KeyError:
                pass

    def createRoomControllerMetrics(self):
        self.metrics["controllers"] = {}

        self.metrics["controllers"]["upgrade"] = {}
        self.metrics["controllers"]["upgrade"]["progress"] = Gauge(
            "screeps_controllers_upgrade_progress",
            documentation="The amount of energy invested in the room controller to upgrade the room control level",
            labelnames=["room", "controller"],
        )
        self.metrics["controllers"]["upgrade"]["nextLevel"] = Gauge(
            "screeps_controllers_upgrade_next_level",
            documentation="The amount of energy required to upgrade the room control level to the next level",
            labelnames=["room", "controller"],
        )

        self.metrics["controllers"]["safeMode"] = {}
        self.metrics["controllers"]["safeMode"]["active"] = Enum(
            "screeps_controllers_safe_mode_active",
            documentation="Whether safe mode is currently active for a given room",
            labelnames=["room", "controller"],
            states=["active", "inactive"],
        )
        self.metrics["controllers"]["safeMode"]["available"] = Gauge(
            "screeps_controllers_safe_mode_next_available",
            documentation="How many safe modes currently remain for a given room",
            labelnames=["room", "controller"],
        )
        self.metrics["controllers"]["safeMode"]["timeLeft"] = Gauge(
            "screeps_controllers_safe_mode_time_left",
            documentation="The duration of time before safe mode deactivates for a given room",
            labelnames=["room", "controller"],
        )
        self.metrics["controllers"]["downgrade"] = Gauge(
            "screeps_controllers_downgrade",
            documentation="The amount of ticks remaining before the room level decrements",
            labelnames=["room", "controller"],
        )
        self.metrics["controllers"]["level"] = Gauge(
            "screeps_controllers_level",
            documentation="The current room control level",
            labelnames=["room", "controller"],
        )

        for roomName in self.roomMemory:
            try:
                controllerData = self.roomMemory[roomName]["controller"]
                for controllerId in controllerData:
                    self.metrics["controllers"]["upgrade"]["progress"].labels(
                        room=roomName, controller=controllerId
                    )
                    self.metrics["controllers"]["upgrade"]["nextLevel"].labels(
                        room=roomName, controller=controllerId
                    )
                    self.metrics["controllers"]["safeMode"]["active"].labels(
                        room=roomName, controller=controllerId
                    )
                    self.metrics["controllers"]["safeMode"]["available"].labels(
                        room=roomName, controller=controllerId
                    )
                    self.metrics["controllers"]["safeMode"]["timeLeft"].labels(
                        room=roomName, controller=controllerId
                    )
                    self.metrics["controllers"]["downgrade"].labels(
                        room=roomName, controller=controllerId
                    )
                    self.metrics["controllers"]["level"].labels(
                        room=roomName, controller=controllerId
                    )

            except KeyError:
                pass

    def pollMetrics(self):
        memory = self.pollMemory()

        self.roomMemory = memory["rooms"]
        self.spawnMemory = memory["spawns"]
        self.jobMemory = memory["jobs"]
        self.creepMemory = memory["creeps"]

        self.pollRoomMetrics()

        sleep(self.config["exporter"]["interval"])

    def pollRoomMetrics(self):
        self.pollRoomEnergyMetrics()
        self.pollRoomSourceMetrics()
        self.pollRoomControllerMetrics()

    def pollRoomEnergyMetrics(self):
        for roomName in self.roomMemory:
            try:
                energyData = self.roomMemory[roomName]["energy"]
                self.metrics["energy"]["amount"].labels(room=roomName).set(
                    energyData["amount"]
                )

                self.metrics["energy"]["capacity"].labels(room=roomName).set(
                    energyData["capacity"]
                )

            except KeyError:
                pass

    def pollRoomSourceMetrics(self):
        for roomName in self.roomMemory:
            try:
                sourceData = self.roomMemory[roomName]["sources"]

                for sourceId in sourceData:
                    self.metrics["sources"]["amount"].labels(
                        room=roomName, source=sourceId
                    ).set(sourceData[sourceId]["energy"]["amount"])
                    self.metrics["sources"]["capacity"].labels(
                        room=roomName, source=sourceId
                    ).set(sourceData[sourceId]["energy"]["capacity"])
                    self.metrics["sources"]["regeneration"].labels(
                        room=roomName, source=sourceId
                    ).set(sourceData[sourceId]["regeneration"])

            except KeyError:
                pass

    def pollRoomControllerMetrics(self):
        for roomName in self.roomMemory:
            try:
                controllerData = self.roomMemory[roomName]["controller"]
                for controllerId in controllerData:
                    self.metrics["controllers"]["upgrade"]["progress"].labels(
                        room=roomName, controller=controllerId
                    ).set(controllerData[controllerId]["upgrade"]["progress"])

                    self.metrics["controllers"]["upgrade"]["nextLevel"].labels(
                        room=roomName, controller=controllerId
                    ).set(controllerData[controllerId]["upgrade"]["nextLevel"])

                    if controllerData[controllerId]["safeMode"]["active"] == True:
                        safeModeState = "active"
                    else:
                        safeModeState = "inactive"

                    self.metrics["controllers"]["safeMode"]["active"].labels(
                        room=roomName, controller=controllerId
                    ).state(safeModeState)

                    self.metrics["controllers"]["safeMode"]["available"].labels(
                        room=roomName, controller=controllerId
                    ).set(controllerData[controllerId]["safeMode"]["available"])

                    try:
                        self.metrics["controllers"]["safeMode"]["timeLeft"].labels(
                            room=roomName, controller=controllerId
                        ).set(controllerData[controllerId]["safeMode"]["timeLeft"])
                    except KeyError as error:
                        print(error)
                        print(controllerData[controllerId]["safeMode"].keys())
                        self.metrics["controllers"]["safeMode"]["timeLeft"].labels(
                            room=roomName, controller=controllerId
                        ).set(0)

                    self.metrics["controllers"]["downgrade"].labels(
                        room=roomName, controller=controllerId
                    ).set(controllerData[controllerId]["downgrade"])

                    self.metrics["controllers"]["level"].labels(
                        room=roomName, controller=controllerId
                    ).set(controllerData[controllerId]["level"])

            except KeyError as error:
                print(error)
