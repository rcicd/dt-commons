#!/usr/bin/env python3
#this file reads every (default) or desired robot (request)

import yaml
import docker
import os
import git
import glob

#Import from another folder within dt-commons (no base image)
from ..dt_archapi_utils/arch_client import ArchAPIClient
from ..dt_archapi_utils/arch_message import ApiMessage

from .device_list import deviceList

class multiArchAPIClient:
    def __init__(self, fleet=None, client=None): #fleet as yaml file without .yaml
        self.client = client
        self.status = ApiMessage()
        self.error = ApiMessage()

        #Set up fleet list
        self.list = deviceList(fleet)
        if self.list.as_array is []:
            self.status("error", "Fleet file was not found", self.list.path_to_list)
        else:
            self.list = self.list.as_array

        #Define robot_type
        self.robot_type = "none"
        if os.path.isfile("/data/config/robot_type"):
            self.robot_type = open("/data/config/robot_type").readline()
        elif os.path.isfile("/data/stats/init_sd_card/parameters/robot_type"):
            self.robot_type = open("/data/stats/init_sd_card/parameters/robot_type").readline()
        else: #error upon initialization = status
            self.status("error", "Could not find robot type in expected paths", None)

        #Initialize folders and directories
        self.current_configuration = "none"
        self.dt_version = "ente"


'''
        #Give town an ArchAPIClient
        self.api = ArchAPIClient()
        self.town_name = os.environ['VEHICLE_NAME']
        self.town = self.api(self.town_name, None)

        #Give every device in fleet an ArchAPIClient
        for i in [0, len(self.fleet)-1]:
            self.multi_api = []
            self.multi_api(i) = self.api(self.fleet(i), self.client)
'''



#ENDPOINTS FOR TOWNAPI:
    #HTTP REQUEST: townXX.local:8083/architecture/<something>/<else>
    #PASS REQUEST: split into all necessary arch configs
    #This library does not take care about individual messages between town and
    #user. As this is the task of the Architecture API running on the town.

    #Make list of desired HTTP cmds to send out
    def request_list(self): #also possible to specify fleet here?
        return self.listmaker

    def read_data(self):
        self.api.config_path


















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



        '''
        if fleet is None:
            self.fleet = self.list.list #"//read from default .yaml file//" #array type!
        else:
            self.fleet = fleet #custom fleet as list/array
        '''
