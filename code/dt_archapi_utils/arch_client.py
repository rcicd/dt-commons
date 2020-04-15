#!/usr/bin/env python3
#This is the DT Architecture Library for dt-commons

#THIS LIB INCLUDES FUNCTIONS THAT ALLOW TO COMMUNICATE WITH AN ARCHITECTURE API
#RUNNING ON A SINGLE ROBOT, BUT DO NOT SPECIFY THE REQUIRED API FOR THAT. I.E.
#THE REQUIRED SERVER IS NOT RUNNING WITHIN THE LIBRARY.

#Define msg types for various endpoints of a single architecture api

import yaml
import docker
import os
import git
import glob

from git import Repo
from .arch_message import ArchMessage

class ArchAPIClient:
    def __init__(self, hostname="hostname"):
        #Initialize robot hostname
        self.hostname = hostname
        #Initialize folders and directories
        self.robot_type = "unknown"
        self.active_config = None
        self.config_path = None
        self.module_path = None
        self.current_configuration = "none"

        self.dt_version = "ente"
        self.status = ArchMessage()
        #self.worker = ConfigWorker()

        #Retract robot_type
        if os.path.isfile("/data/config/robot_type"):
            self.robot_type = open("/data/config/robot_type").readline()
        elif os.path.isfile("/data/stats/init_sd_card/parameters/robot_type"):
            self.robot_type = open("/data/stats/init_sd_card/parameters/robot_type").readline()
        else: #error upon initialization
            self.status("error", "Could not find robot type in expected paths", None)

        #Include ente version of dt-architecture-data repo
        if not os.path.isdir("/data/assets/dt-architecture-data"):
            os.makedirs("/data/assets", exist_ok=True)
            git.Git("/data/assets").clone("git://github.com/duckietown/dt-architecture-data.git", branch=self.dt_version)

        self.config_path = "/data/assets/dt-architecture-data/configurations/"+self.robot_type
        self.module_path = "/data/assets/dt-architecture-data/modules/"

        #Initialize configuration & module endpoints
        self.configuration = []  #empty array, with all endpoints in it
        self.module = []  #empty list, with all endpoints in it


#PASSIVE MESSAGING: monitoring (info, list, status) requests
    def default_response(self):
        return self.status #.msg if message only

    def configuration_status(self):
        self.configuration.status = json.dumps(self.status)
        return self.configuration.status

    def configuration_list(self):
        self.configuration.list = {} #re-initialize every time called for (empty when error)
        if self.config_path is not None:
            config_paths = glob.glob(self.config_path + "/*.yaml")
            self.configuration.list["configurations"] = [os.path.splitext(os.path.basename(f))[0] for f in config_paths]
        else: #error msg
            return self.status("error", "could not find configurations (dt-docker-data)", None)
        return self.configuration.list


    def configuration_info(self, config):
        self.configuration.info = {} #re-initialize every time called for (empty when error)
        try:
            with open(self.config_path + "/" + config + ".yaml", 'r') as file:
                data = yaml.load(file)
                if "modules" in data:
                    mods = data["modules"]
                    for m in mods:
                        if "type" in mods[m]:
                            mod_type = mods[m]["type"]
                            mod_config = self.module_info(mod_type)
                            if "configuration" in mod_config:
                                data["modules"][m]["configuration"] = mod_config["configuration"]
                self.configuration.info = data
        except FileNotFoundError: #error msg
            return self.status("error", "Configuration file not found", self.config_path + "/" + config + ".yaml")
        return self.configuration.info


    def module_list(self):
        self.module.list = {} #re-initialize every time called for (empty when error)
        yaml_paths = glob.glob(self.module_path + "/*.yaml")
        for files in yaml_paths:
            try:
                with open(files, 'r') as fd:
                    print ("loading module: " + files)
                    config = yaml.load(fd)
                    filename, ext = os.path.splitext(os.path.basename(files))
                    self.module.list["modules"] = [] #put here, so error msg can be sent
                    self.module.list["modules"].append(filename)
            except FileNotFoundError: #error msg
                return self.status("error", "Module file not found", self.module_path + "/" + module_name + ".yaml")
        return self.module.list


    def module_info(self, module):
        self.module.info = {} #re-initialize every time called for (empty when error)
        try:
            with open(self.module_path + "/" + module + ".yaml", 'r') as fd:
                self.module.info = yaml.load(fd)
                config = self.module.info["configuration"]

                #Update ports for pydocker from docker-compose
                if "ports" in config:
                    ports = config["ports"]
                    newports = {}
                    for p in ports:
                        external,internal = p.split(":", 1)
                        newports[internal]=int(external)
                    config["ports"] = newports
                #Update volumes for pydocker from docker-compose
                if "volumes" in config:
                    vols = config["volumes"]
                    newvols = {}
                    for v in vols:
                        host, container = v.split(":", 1)
                        newvols[host] = {'bind': container, 'mode':'rw'} #what happens here?
                    config["volumes"] = newvols
                #Update restart_policy
                if "restart" in config:
                    config.pop("restart")
                    restart_policy = {"Name":"always"}
                #Update container_name
                if "container_name" in config:
                    config["name"] = config.pop("container_name")
                #Update image
                if "image" in config:
                    config["image"] = config["image"].replace('${ARCH-arm32v7}','arm32v7' )

        except FileNotFoundError: #error msg, self.module.info is still empty
            return self.status("error", "Module not found", self.module_path + module + ".yaml")

        return self.module.info


#ACTIVE MESSAGING: activation (pull, stop, ...) requests













''' #IGNORE#
    def module(self):
        self.docker_client.containers = 'something' #from docker SDK for python

        #LIST OF ENDPOINTS
        #functions to read out from configuration endpoints
        self.modules
        self.modules_info = "Do we want to have this much detail?"

        self.module_set = "Not only client, but also boss"

    def get_configuration_list(self, robot):
        #LIST OF ENDPOINTS
        #functions to read out configuration endpoints
        self.status =
        self.configurations =
        self.configurations_info = "Do we want to have this much detail?"

        self.configuration_set = "Not only client, but also boss"

    def get_configuration_status(self, robot):
        self.ok

    def get(self):
        self.ok
'''
