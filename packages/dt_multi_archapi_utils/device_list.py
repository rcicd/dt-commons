#!/usr/bin/env python3
#returns the default array of devices

import yaml
import docker
import os
import git
import glob


class DeviceList:
    def __init__(self, fleet=None):
        #Define incoming fleet
        self.fleet = fleet
        self.dt_version = "ente"

        #Include ente version of dt-architecture-data repo
        if not os.path.isdir("/data/assets/dt-architecture-data"):
            os.makedirs("/data/assets", exist_ok=True)
            git.Git("/data/assets").clone("git://github.com/duckietown/dt-architecture-data.git", branch=self.dt_version)

        self.list_path = "/data/assets/dt-architecture-data/lists"


    def as_array(self):
        if self.fleet is None:
            #set up array from default yaml file
            self.fleet = "default_device_list"
            self.defaultList = self.list_maker(self.fleet)
            return self.defaultList
        else:
            #set up array from custom yaml file
            self.customList = self.list_maker(self.fleet)
            return self.customList


    def list_maker(self, fleet_file):
        #Bring input .yaml file to array
        self.list = []
        self.path_to_list = self.list_path + "/" + fleet_file + ".yaml"
        try:
            with open(self.path_to_list, 'r') as f:
                file = yaml.load(f)
                devices = file["devices"]

                duckiebots = []
                if "duckiebot" in devices:
                    duckiebots = devices["duckiebot"]
                watchtowers = []
                if "watchtower" in devices:
                    watchtowers = devices["watchtower"]
                greenstations = []
                if "greenstation" in devices:
                    greenstations = devices["greenstation"]
                duckiedrones = []
                if "duckiedrone" in devices:
                    duckiedrones = devices["duckiedrone"]

                listed = duckiebots.extend(watchtowers).extend(greenstations).extend(duckiedrones)
                self.list = listed
                return self.list

        except FileNotFoundError:
            #Return empty list - error msg
            return self.list
