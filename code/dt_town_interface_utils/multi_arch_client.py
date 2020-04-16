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
    def __init__(self, fleet=None, client=None):
        #fleet = list/array of devices that are to be controlled
        #client = docker.DockerClient for communication via server

        #Initialize fleet & docker.DockerClient()
        self.client = client
        if fleet is None:
            self.fleet = "//read from default .yaml file//"
        else:
            self.fleet = fleet #custom fleet as list/array

        #Give every DB an ArchAPIClient
        self.api = ArchAPIClient()
        for i in [0, (len(self.fleet) -1)]:
            self.multi_api = []
            self.multi_api(i) = self.api(self.fleet(i), self.client)

        #Initialize folders and directories
        self.robot_type = "unknown"
        self.active_config = None
        self.current_configuration = "none"
        self.dt_version = "ente"


#SWARM FUNCTION: move to dt-town-interface
    def docker_swarm(self):
        self.client.swarm()


#ENDPOINTS FOR TOWNAPI:
    #HTTP REQUEST: townXX.local:8083/architecture/<something>/<else>
    #PASS REQUEST: split into all necessary arch configs

#AUXILIARY FUNCTIONS:
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
