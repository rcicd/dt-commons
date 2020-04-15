#!/usr/bin/env python3
#this file reads every (default) or desired robot (request)

import yaml
import docker
import os
import git
import glob

#Import from another folder within dt-commons (no base image)
from ..dt_archapi_utils/arch_client import ArchAPIClient

class multiArchAPIClient:
    def __init__(self, robot):
        super(StateEstimator, self).__init__(robot=node_name)
        
        self.robot = robot #upon calling this class from lib, specify input robot
        self.robot_type = "unknown"
        self.active_config = None
        self.config_path = None
        self.module_path = "/data/assets/dt-architecture-data/modules/"
        self.current_configuration = "none"
        self.dt_version = "ente"
        self.worker = ConfigWorker()
        self.status = ConfigMessage()

    def get_robot_list(self):
        #list ALL robots from .yaml filename by default
        #if no http request can be sent, show error message, or don't care
        #make .yaml file for Autolab only (for now)
        if 'incoming' is 'empty':
            return self.robot = np.array(["from_yaml_file"])
        else:
            return self.robot = np.array(["the incoming robots"])

    def get_robot_type_list(self):
        for i in [0, self.robot_type_count]:
            if self.robot_type == 'duckiebot':
                return 'list of all possible configurations'
            elif self.robot_type == 'watchtower':
                return 'list of all possible configurations'
            elif self.robot_type == 'duckiedrone':
                return 'list of all possible configurations'

    def get_robot_count(self):
        self.robot_count = len(self.robot)

    def archAPIClient(self):
        self.docker_client.configs = 'something'

        #specify the required input for the ArchAPIClient class
        self.robot = ArchAPIClient(self.robot) #"duckiebot23"

        #call desired msgs
        self.status = robot.configuration.status()
        self.list = robot.configuration.list()
        self.info = "default message, hardcoded, get from somewhere (dt-arch-data??)"
