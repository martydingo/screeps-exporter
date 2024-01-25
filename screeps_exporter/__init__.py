import screepsapi
import yaml
import argparse
from prometheus_client import start_http_server, Gauge, Info
from time import sleep

class screeps_exporter:
    def __init__(self, config_file) -> None:
        print("Starting screeps_exporter")
        self.room_monitoring_dict = {}
        self.monitoring_targets = {}
        self.metrics = {}
        self.__load_config__(config_file)

        self.prefix = f"screeps"

        self.__initialise_api_connection__()
        self.__get_room_monitoring_memory__()
        self.__define_keys__()
        self.__build_metrics__()

        print("Exporting metrics on port 8122")
        start_http_server(port=8122)
        while True:
            self.__export_metrics__()


    def __load_config__(self, config_file):
        with open(config_file, "r") as config_file:
            self.config = yaml.load(config_file, Loader=yaml.FullLoader)

    def __initialise_api_connection__(self):
        self.auth_config = self.config["auth"]
        fqdn = f"{self.auth_config["hostname"]}:{self.auth_config["port"]}"
        if(self.auth_config["token"]):
            self.screepsApi = screepsapi.API(
                token=self.auth_config["token"],
                host=fqdn,
                secure=self.auth_config["secure"],
            )
        else:
            self.screepsApi = screepsapi.API(
                u=self.auth_config["username"],
                p=self.auth_config["password"],
                host=fqdn,
                secure=self.auth_config["secure"],
            )

    def __get_room_monitoring_memory__(self):
        roomMemory = self.screepsApi.memory(path="rooms", shard=self.auth_config["shard"])
        for roomName, roomMonitoringData in roomMemory['data'].items():
            self.room_monitoring_dict.update({roomName: roomMonitoringData['monitoring']})


    def __recurse_monitoring_dict_for_keys__(self, dictionary):
        keyArray = []
        for key, value in dictionary.items():
            if(isinstance(value, dict)):
                keyArray.append(key)
                if(len(value) > 0):
                    self.__recurse_monitoring_dict_for_keys__(value)
            else:
                keyArray.append(key)
        return keyArray


    def __define_keys__(self):
        for roomName, roomMonitoringData in self.room_monitoring_dict.items():
            for roomMonitorKey, roomMonitorValue in roomMonitoringData.items():
                prefix = f"{roomMonitorKey}"
                keyArray = self.__recurse_monitoring_dict_for_keys__(roomMonitorValue)
                for key in keyArray:
                    topLevelKey = f"{prefix}_{key}"
                    topLevelChildren = self.__recurse_monitoring_dict_for_keys__(roomMonitorValue[key])
                    if(len(topLevelChildren) > 0):
                        if(type(roomMonitorValue[key][topLevelChildren[0]]) == dict):
                            childrenKeys = self.__recurse_monitoring_dict_for_keys__(roomMonitorValue[key][topLevelChildren[0]])
                            for innerKey in childrenKeys:
                                self.monitoring_targets.update({f"{roomName}_{topLevelKey}_{innerKey}": topLevelChildren})
                        
                    

    def __build_metrics__(self):
        monitoringDataKeys = self.monitoring_targets.keys()
        for outerKey in monitoringDataKeys:
            splitMonitoringDataKeys = outerKey.split("_")
            roomName = splitMonitoringDataKeys[0]
            metricKey = f"{self.prefix}_{splitMonitoringDataKeys[1]}_{splitMonitoringDataKeys[2]}_{splitMonitoringDataKeys[3]}"
            try:
               self.metrics[metricKey]
            except KeyError:
                if(metricKey == f"{self.prefix}_structures_storage_contents" or metricKey == f"{self.prefix}_resources_ruins_contents"):
                    self.metrics.update({metricKey: Gauge(metricKey, f"Gauge for{metricKey}", ["room_name", "id", "resource", "instance"])})
                elif(metricKey == f"{self.prefix}_resources_droppedResources_resourceType"):
                    self.metrics.update({metricKey: Info(metricKey, f"Gauge for{metricKey}", ["room_name", "id", "instance"])})
                elif(metricKey == f"{self.prefix}_resources_droppedResources_pos"):
                        pass
                else:
                    self.metrics.update({metricKey: Gauge(metricKey, f"Gauge for{metricKey}", ["room_name", "id", "instance"])})
            

    def __export_metrics__(self):
        self.__get_room_monitoring_memory__()
        
        self.__build_metrics__()
        monitoringDataKeys = self.monitoring_targets.keys()
        for outerKey in monitoringDataKeys:
            splitMonitoringDataKeys = outerKey.split("_")
            roomName = splitMonitoringDataKeys[0]
            metricKey = f"{self.prefix}_{splitMonitoringDataKeys[1]}_{splitMonitoringDataKeys[2]}_{splitMonitoringDataKeys[3]}"
            
            monitorDictionary = self.room_monitoring_dict[splitMonitoringDataKeys[0]][splitMonitoringDataKeys[1]][splitMonitoringDataKeys[2]]
            
            for childKey in self.monitoring_targets[outerKey]:
                try:
                    value = monitorDictionary[childKey][splitMonitoringDataKeys[3]]
                    if(value == None):
                        value = 0
                    if(metricKey == f"{self.prefix}_structures_storage_contents" or metricKey == f"{self.prefix}_resources_ruins_contents"):
                        for resourceKey, resourceValue in value.items():
                            self.metrics[metricKey].labels(room_name=roomName, id=childKey, resource=resourceKey, instance=self.config['exporter']['name']).set(resourceValue)
                    elif(metricKey == f"{self.prefix}_resources_droppedResources_resourceType"):
                            self.metrics[metricKey].labels(room_name=roomName, id=childKey, instance=self.config['exporter']['name']).info({"resource": value})
                    elif(metricKey == f"{self.prefix}_resources_droppedResources_pos"):
                            pass
                    else:
                        # if(isinstance(value, int)):
                        self.metrics[metricKey].labels(room_name=roomName, id=childKey, instance=self.config['exporter']['name']).set(value)
                except KeyError:
                    self.monitoring_targets[outerKey].remove(childKey)
                    self.metrics[metricKey].remove(roomName, childKey, self.config['exporter']['name'])
        sleep(self.config['exporter']['interval'])
        

