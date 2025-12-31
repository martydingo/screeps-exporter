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
        self.globalMemory = memory["global"]

        self.createGlobalMetrics()
        self.createRoomMetrics()

    def createRoomMetrics(self):
        self.createRoomEnergyMetrics()
        self.createRoomSourceMetrics()
        self.createRoomControllerMetrics()
        self.createRoomDroppedResourceMetrics()
        self.createRoomStructureMetrics()
        self.createSpawnMetrics()
        self.createJobMetrics()

    def createGlobalMetrics(self):
        self.metrics["global"] = {}
        self.createGlobalGclMetrics()

    def createGlobalGclMetrics(self):
        self.metrics["global"]["gcl"] = {}
        self.metrics["global"]["gcl"]["level"] = Gauge(
            "screeps_global_gcl_level",
            documentation="The current global control level of the player",
        )
        self.metrics["global"]["gcl"]["progress"] = Gauge(
            "screeps_global_gcl_progress",
            documentation="The current amount of progress to the next global control level",
        )
        self.metrics["global"]["gcl"]["nextLevel"] = Gauge(
            "screeps_global_gcl_next_level",
            documentation="The total progress required to progress to the next global control level",
        )
        # self.metrics[""]

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

            except KeyError as error:
                print(f"create_screeps_room_energy: {error}")

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

            except KeyError as error:
                print(f"create_screeps_sources: {error}")

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

            except KeyError as error:
                print(f"create_screeps_controllers: {error}")

    def createRoomDroppedResourceMetrics(self):
        self.metrics["droppedResources"] = Gauge(
            "screeps_dropped_resources",
            documentation="Tracks the amount and the resource type of dropped resources within a given room",
            labelnames=["room", "resource_id", "resource_type"],
        )

        for roomName in self.roomMemory:
            try:
                droppedResourceData = self.roomMemory[roomName]["resources"]
                for droppedResourceId in droppedResourceData:
                    self.metrics["droppedResources"].labels(
                        room=roomName,
                        resource_id=droppedResourceId,
                        resource_type=self.roomMemory[roomName]["resources"][
                            droppedResourceId
                        ]["resource"],
                    )
            except KeyError as error:
                print(f"create_screeps_dropped_resources: {error}")

    def createRoomStructureMetrics(self):
        self.metrics["structures"] = {}

        self.createRoomStorageMetrics()
        self.createRoomLabMetrics()
        self.createRoomTerminalMetrics()
        self.createRoomExtensionMetrics()
        self.createRoomLinkMetrics()

    def createRoomStorageMetrics(self):
        self.metrics["structures"]["storage"] = {}
        self.metrics["structures"]["storage"]["amount"] = Gauge(
            "screeps_structures_storage_amount",
            documentation="Tracks the amount of resources stored within storage for a given room",
            labelnames=["room", "storage", "resource"],
        )
        self.metrics["structures"]["storage"]["capacity"] = Gauge(
            "screeps_structures_storage_capacity",
            documentation="Tracks the total capacity of resources that can be stored within storage for a given room",
            labelnames=["room", "storage", "resource"],
        )

        for roomName in self.roomMemory:
            try:
                storageData = self.roomMemory[roomName]["structures"]["storage"]
                for storageId in storageData:
                    for resource in storageData[storageId]["resources"]:
                        self.metrics["structures"]["storage"]["amount"].labels(
                            room=roomName, storage=storageId, resource=resource
                        )
                        self.metrics["structures"]["storage"]["capacity"].labels(
                            room=roomName, storage=storageId, resource=resource
                        )
            except KeyError as error:
                print(f"create_screeps_storage: {error}")

    def createRoomLabMetrics(self):
        self.metrics["structures"]["labs"] = {}
        self.metrics["structures"]["labs"]["amount"] = Gauge(
            "screeps_structures_labs_amount",
            documentation="Tracks the amount of resources stored within lab for a given room",
            labelnames=["room", "lab", "resource"],
        )
        self.metrics["structures"]["labs"]["capacity"] = Gauge(
            "screeps_structures_labs_capacity",
            documentation="Tracks the total capacity of resources that can be stored within lab for a given room",
            labelnames=["room", "lab", "resource"],
        )

        for roomName in self.roomMemory:
            try:
                labData = self.roomMemory[roomName]["structures"]["labs"]
                for labId in labData:
                    for resource in labData[labId]["resources"]:
                        self.metrics["structures"]["labs"]["amount"].labels(
                            room=roomName, lab=labId, resource=resource
                        )
                        self.metrics["structures"]["labs"]["capacity"].labels(
                            room=roomName, lab=labId, resource=resource
                        )
            except KeyError as error:
                print(f"create_screeps_lab: {error}")

    def createRoomTerminalMetrics(self):
        self.metrics["structures"]["terminal"] = {}
        self.metrics["structures"]["terminal"]["amount"] = Gauge(
            "screeps_structures_terminal_amount",
            documentation="Tracks the amount of resources stored within terminal for a given room",
            labelnames=["room", "terminal", "resource"],
        )
        self.metrics["structures"]["terminal"]["capacity"] = Gauge(
            "screeps_structures_terminal_capacity",
            documentation="Tracks the total capacity of resources that can be stored within terminal for a given room",
            labelnames=["room", "terminal", "resource"],
        )

        for roomName in self.roomMemory:
            try:
                terminalData = self.roomMemory[roomName]["structures"]["terminal"]
                for terminalId in terminalData:
                    for resource in terminalData[terminalId]["resources"]:
                        self.metrics["structures"]["terminal"]["amount"].labels(
                            room=roomName, terminal=terminalId, resource=resource
                        )
                        self.metrics["structures"]["terminal"]["capacity"].labels(
                            room=roomName, terminal=terminalId, resource=resource
                        )
            except KeyError as error:
                print(f"create_screeps_terminal: {error}")

    def createRoomExtensionMetrics(self):
        self.metrics["structures"]["extensions"] = Gauge(
            "screeps_structures_extensions",
            documentation="Tracks the amount of energy stored within extensions",
            labelnames=["room", "extension"],
        )

        for roomName in self.roomMemory:
            try:
                extensionData = self.roomMemory[roomName]["structures"]["extensions"]
                for extensionId in extensionData:
                    self.metrics["structures"]["extensions"].labels(
                        room=roomName, extension=extensionId
                    )
            except KeyError as error:
                print(f"create_screeps_structures_extensions: {error}")

    def createRoomLinkMetrics(self):
        self.metrics["structures"]["links"] = {}
        self.metrics["structures"]["links"]["amount"] = Gauge(
            "screeps_structures_links_amount",
            documentation="Tracks the amount of energy stored within links",
            labelnames=["room", "link", "linkType"],
        )
        self.metrics["structures"]["links"]["capacity"] = Gauge(
            "screeps_structures_links_capacity",
            documentation="Tracks the total capacity of energy that can bestored within links",
            labelnames=["room", "link", "linkType"],
        )

        for roomName in self.roomMemory:
            try:
                linkData = self.roomMemory[roomName]["structures"]["links"]
                for linkId in linkData:
                    self.metrics["structures"]["links"]["amount"].labels(
                        room=roomName,
                        link=linkId,
                        linkType=linkData[linkId]["linkType"],
                    )
                    self.metrics["structures"]["links"]["capacity"].labels(
                        room=roomName,
                        link=linkId,
                        linkType=linkData[linkId]["linkType"],
                    )

            except KeyError as error:
                print(f"create_screeps_structures_links: {error}")

    def createRoomContainersMetrics(self):
        self.metrics["structures"]["containers"] = {}
        self.metrics["structures"]["containers"]["hits"] = {}
        self.metrics["structures"]["containers"]["hits"]["hits"] = Gauge(
            "screeps_structures_hits_hits",
            documentation="Tracks the amount of hitpoints of a given container has",
            labelnames=["room", "container"],
        )
        self.metrics["structures"]["containers"]["hits"]["hitsMax"] = Gauge(
            "screeps_structures_hits_hitsMax",
            documentation="Tracks the total amount of hitpoints of a given container has",
            labelnames=["room", "container"],
        )

        self.metrics["structures"]["containers"]["resources"] = {}
        self.metrics["structures"]["containers"]["resources"]["amount"] = Gauge(
            "screeps_structures_containers_amount",
            documentation="Tracks the amount of resources stored within containers for a given room",
            labelnames=["room", "container", "resource"],
        )
        self.metrics["structures"]["containers"]["resources"]["capacity"] = Gauge(
            "screeps_structures_containers_capacity",
            documentation="Tracks the total capacity of resources that can be stored within containers for a given room",
            labelnames=["room", "container", "resource"],
        )

        for roomName in self.roomMemory:
            try:
                containersData = self.roomMemory[roomName]["structures"]["containers"]
                for containerId in containersData:
                    self.metrics["structures"]["containers"]["hits"]["hits"].labels(
                        room=roomName, container=containerId
                    )
                    self.metrics["structures"]["containers"]["hits"]["hitsMax"].labels(
                        room=roomName, container=containerId
                    )
                    for resource in containersData[containerId]["resources"]:
                        self.metrics["structures"]["containers"]["resources"][
                            "amount"
                        ].labels(
                            room=roomName, container=containerId, resource=resource
                        )
                        self.metrics["structures"]["containers"]["resources"][
                            "capacity"
                        ].labels(
                            room=roomName, container=containerId, resource=resource
                        )
            except KeyError as error:
                print(f"create_screeps_containers: {error}")

    def createSpawnMetrics(self):
        self.metrics["spawns"] = {}
        self.metrics["spawns"]["energy"] = {}
        self.metrics["spawns"]["energy"]["amount"] = Gauge(
            "screeps_spawns_energy",
            documentation="Tracks the amount of energy stored within spawners",
            labelnames=["spawn"],
        )
        self.metrics["spawns"]["energy"]["capacity"] = Gauge(
            "screeps_spawns_capacity",
            documentation="Tracks the total capacity of energy that can be stored within spawners",
            labelnames=["spawn"],
        )
        self.metrics["spawns"]["spawning"] = Enum(
            "screeps_spawns_spawning",
            documentation="Whether a given spawner is spawning a creep",
            labelnames=["spawn"],
            states=["spawning", "idle"],
        )

        try:
            spawnData = self.spawnMemory
            for spawnName in spawnData:
                self.metrics["spawns"]["energy"]["amount"].labels(spawn=spawnName)
                self.metrics["spawns"]["energy"]["capacity"].labels(spawn=spawnName)
                self.metrics["spawns"]["spawning"].labels(spawn=spawnName)
        except KeyError as error:
            print(f"create_screeps_spawns: {error}")

    def createJobMetrics(self):
        self.metrics["jobs"] = {}
        self.metrics["jobs"]["count"] = {}
        self.metrics["jobs"]["count"]["type"] = Gauge(
            "screeps_jobs_count_type",
            documentation="Tracks the number of jobs within the jobs queue",
            labelnames=["job_type"],
        )

        try:
            jobTypes = list(
                map(lambda jobName: self.jobMemory[jobName]["type"], self.jobMemory)
            )

            self.metrics["jobs"]["count"]["status"] = Gauge(
                "screeps_jobs_count_name",
                documentation="Tracks the number of jobs within the jobs queue",
                labelnames=["status"],
            )

            jobStatusNames = list(
                map(lambda jobName: self.jobMemory[jobName]["status"], self.jobMemory)
            )

            for jobType in jobTypes:
                self.metrics["jobs"]["count"]["type"].labels(job_type=jobType)

            for jobStatusName in jobStatusNames:
                self.metrics["jobs"]["count"]["status"].labels(status=jobStatusName)
        except KeyError as error:
            print(f"create_screeps_jobs: {error}")

    def pollMetrics(self):
        try:
            memory = self.pollMemory()

            self.roomMemory = memory["rooms"]
            self.spawnMemory = memory["spawns"]
            self.jobMemory = memory["jobs"]
            self.creepMemory = memory["creeps"]
            self.globalMemory = memory["global"]

            self.pollGlobalGclMetrics()
            self.pollRoomMetrics()
        except Exception as error:
            print(f"pollMetrics: {error}")

        sleep(self.config["exporter"]["interval"])

    def pollGlobalGclMetrics(self):
        self.metrics["global"]["gcl"]["level"].set(self.globalMemory["gcl"]["level"])
        self.metrics["global"]["gcl"]["progress"].set(
            self.globalMemory["gcl"]["progress"]
        )
        self.metrics["global"]["gcl"]["nextLevel"].set(
            self.globalMemory["gcl"]["nextLevel"]
        )

    def pollRoomMetrics(self):
        self.pollRoomEnergyMetrics()
        self.pollRoomSourceMetrics()
        self.pollRoomControllerMetrics()
        self.pollRoomDroppedResourceMetrics()
        self.pollRoomStorageMetrics()
        self.pollRoomLabMetrics()
        self.pollRoomTerminalMetrics()
        self.pollRoomExtensionMetrics()
        self.pollRoomLinkMetrics()
        self.pollSpawnMetrics()
        self.pollJobMetrics()

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

            except KeyError as error:
                print(f"poll_screeps_room_energy: {error}")

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

            except KeyError as error:
                print(f"poll_screeps_sources: {error}")

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
                    except KeyError:
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
                print(f"poll_screeps_controllers: {error}")

    def pollRoomDroppedResourceMetrics(self):
        droppedResourceLabels = set()
        for roomName in self.roomMemory:
            try:
                droppedResourceData = self.roomMemory[roomName]["resources"]
                for droppedResourceId in droppedResourceData:
                    labels = (
                        roomName,
                        droppedResourceId,
                        self.roomMemory[roomName]["resources"][droppedResourceId][
                            "resource"
                        ],
                    )

                    droppedResourceLabels.add(labels)

                    self.metrics["droppedResources"].labels(
                        room=labels[0],
                        resource_id=labels[1],
                        resource_type=labels[2],
                    ).set(
                        self.roomMemory[roomName]["resources"][droppedResourceId][
                            "amount"
                        ]
                    )

            except KeyError as error:
                print(f"poll_screeps_dropped_resources: {error}")

            metric = self.metrics["droppedResources"]
            for labels in list(metric._metrics.keys()):
                if labels not in droppedResourceLabels:
                    metric.remove(*labels)

    def pollRoomStorageMetrics(self):
        for roomName in self.roomMemory:
            try:
                storageData = self.roomMemory[roomName]["structures"]["storage"]
                for storageId in storageData:
                    for resource in storageData[storageId]["resources"]:
                        self.metrics["structures"]["storage"]["amount"].labels(
                            room=roomName, storage=storageId, resource=resource
                        ).set(
                            self.roomMemory[roomName]["structures"]["storage"][
                                storageId
                            ]["resources"][resource]["amount"]
                        )
                        self.metrics["structures"]["storage"]["capacity"].labels(
                            room=roomName, storage=storageId, resource=resource
                        ).set(
                            self.roomMemory[roomName]["structures"]["storage"][
                                storageId
                            ]["resources"][resource]["capacity"]
                        )
            except KeyError as error:
                print(f"poll_screeps_storage: {error}")

    def pollRoomLabMetrics(self):
        for roomName in self.roomMemory:
            try:
                labData = self.roomMemory[roomName]["structures"]["labs"]
                for labId in labData:
                    for resource in labData[labId]["resources"]:
                        self.metrics["structures"]["labs"]["amount"].labels(
                            room=roomName, lab=labId, resource=resource
                        ).set(labData[labId]["resources"][resource]["amount"])
                        self.metrics["structures"]["labs"]["capacity"].labels(
                            room=roomName, lab=labId, resource=resource
                        )
            except KeyError as error:
                print(f"create_screeps_lab: {error}")

    def pollRoomTerminalMetrics(self):
        for roomName in self.roomMemory:
            try:
                terminalData = self.roomMemory[roomName]["structures"]["terminal"]
                for terminalId in terminalData:
                    for resource in terminalData[terminalId]["resources"]:
                        self.metrics["structures"]["terminal"]["amount"].labels(
                            room=roomName, terminal=terminalId, resource=resource
                        ).set(terminalData[terminalId]["resources"][resource]["amount"])
                        self.metrics["structures"]["terminal"]["capacity"].labels(
                            room=roomName, terminal=terminalId, resource=resource
                        ).set(
                            terminalData[terminalId]["resources"][resource]["capacity"]
                        )
            except KeyError as error:
                print(f"create_screeps_terminal: {error}")

    def pollRoomExtensionMetrics(self):
        for roomName in self.roomMemory:
            try:
                extensionData = self.roomMemory[roomName]["structures"]["extensions"]
                for extensionId in extensionData:
                    self.metrics["structures"]["extensions"].labels(
                        room=roomName, extension=extensionId
                    ).set(
                        self.roomMemory[roomName]["structures"]["extensions"][
                            extensionId
                        ]["energy"]["amount"]
                    )
            except KeyError as error:
                print(f"poll_screeps_extensions: {error}")

    def pollRoomLinkMetrics(self):
        for roomName in self.roomMemory:
            try:
                linkData = self.roomMemory[roomName]["structures"]["links"]
                for linkId in linkData:
                    self.metrics["structures"]["links"]["amount"].labels(
                        room=roomName,
                        link=linkId,
                        linkType=linkData[linkId]["linkType"],
                    ).set(
                        self.roomMemory[roomName]["structures"]["links"][linkId][
                            "energy"
                        ]["amount"]
                    )
                    self.metrics["structures"]["links"]["capacity"].labels(
                        room=roomName,
                        link=linkId,
                        linkType=linkData[linkId]["linkType"],
                    ).set(
                        self.roomMemory[roomName]["structures"]["links"][linkId][
                            "energy"
                        ]["capacity"]
                    )

            except KeyError as error:
                print(f"create_screeps_structures_links: {error}")

    def pollRoomContainersMetrics(self):
        for roomName in self.roomMemory:
            try:
                containersData = self.roomMemory[roomName]["structures"]["containers"]
                for containerId in containersData:
                    self.metrics["structures"]["containers"]["hits"]["hits"].labels(
                        room=roomName, container=containerId
                    ).set(containersData[containerId]["hits"]["hits"])
                    self.metrics["structures"]["containers"]["hits"]["hitsMax"].labels(
                        room=roomName, container=containerId
                    ).set(containersData[containerId]["hits"]["hitsMax"])
                    for resource in containersData[containerId]["resources"]:
                        self.metrics["structures"]["containers"]["resources"][
                            "amount"
                        ].labels(
                            room=roomName, container=containerId, resource=resource
                        ).set(
                            containersData[containerId]["resources"][resource]["amount"]
                        )
                        self.metrics["structures"]["containers"]["resources"][
                            "capacity"
                        ].labels(
                            room=roomName, container=containerId, resource=resource
                        ).set(
                            containersData[containerId]["resources"][resource][
                                "capacity"
                            ]
                        )
            except KeyError as error:
                print(f"create_screeps_containers: {error}")

    def pollSpawnMetrics(self):
        try:
            spawnData = self.spawnMemory
            for spawnName in spawnData:
                self.metrics["spawns"]["energy"]["amount"].labels(spawn=spawnName).set(
                    self.spawnMemory[spawnName]["energy"]["amount"]
                )

                self.metrics["spawns"]["energy"]["capacity"].labels(
                    spawn=spawnName
                ).set(self.spawnMemory[spawnName]["energy"]["capacity"])

                if self.spawnMemory[spawnName]["spawning"] == True:
                    spawnerState = "spawning"
                else:
                    spawnerState = "idle"
                self.metrics["spawns"]["spawning"].labels(spawn=spawnName).state(
                    spawnerState
                )

        except KeyError as error:
            print(f"poll_screeps_spawns: {error}")

    def pollJobMetrics(self):
        try:
            typeCounts = {}
            jobTypes = list(
                map(lambda jobName: self.jobMemory[jobName]["type"], self.jobMemory)
            )

            for jobType in jobTypes:
                typeCounts[jobType] = 0

            statusCounts = {}
            jobStatusNames = list(
                map(lambda jobName: self.jobMemory[jobName]["status"], self.jobMemory)
            )

            for statusName in jobStatusNames:
                statusCounts[statusName] = 0

            for jobName, jobData in self.jobMemory.items():
                typeCounts[jobData["type"]] = typeCounts[jobData["type"]] + 1
                statusCounts[jobData["status"]] = statusCounts[jobData["status"]] + 1

            for typeName, typeCount in typeCounts.items():
                self.metrics["jobs"]["count"]["type"].labels(job_type=typeName).set(
                    typeCount
                )

            for statusName, statusCount in statusCounts.items():
                self.metrics["jobs"]["count"]["status"].labels(status=statusName).set(
                    statusCount
                )
        except KeyError as error:
            print(f"poll_screeps_jobs: {error}")
