#!/usr/bin/env python3

import yaml
import docker
import os
import git
import glob
import requests
import json

#Import from another folder within dt-commons (no base image)
from ..dt_archapi_utils/arch_client import ArchAPIClient
from ..dt_archapi_utils/arch_message import ApiMessage

from .device_list import DeviceList
from .multi_request import MultiRequests

'''
    DESCRIPTION:
'''

class MultiArchAPIClient:
    def __init__(self, fleet=None, client=None, port="8083"): #fleet as yaml file without .yaml
        self.client = client
        self.port = port
        self.status = ApiMessage()
        self.error = ApiMessage()

        #Set up fleet list
        self.fleet = deviceList(fleet)
        if self.fleet.as_array is []:
            self.status("error", "Fleet file was not found", self.fleet.path_to_list)
        else:
            self.fleet = self.fleet.as_array

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

        #Give town an ArchAPIClient
        self.town_name = os.environ['VEHICLE_NAME']
        self.town_api = ArchAPIClient(self.town_name, self.robot_type, self.client)


    #TOWN CONFIGURATION: #extended with device info from config file
    #Passive Messaging
    def default_response(self):
        return self.town_api.default_response

    def configuration_info(self, config):
        #Include config info on fleet (per device)
        self.c_info_1 = self.town_api.configuration_info(config)
        self.configuration_info = "appended self.c_info_1 with fleet info"
        return self.configuration_info

    #Active messaging
    def configuration_set_config(self, config):
        #Launch town modules
        self.c_set_config = self.town_api.configuration_set_config(config)

        #Launch configuration requests for devices in fleet
        for "devices" in config:
            do something
            self.send_request #send request

        self.configuration_set_config = "appended launching town modules with sending out a GET HTTP request for device configurations"
        return self.c_set_config



    #FLEET CONFIGURATION
    def send_request(self, fleet):
        FLEET

    def get_url_list(self, endpoint):
        self.url = ".local" + self.port + "/"
        self.url_list = []
        for i in [0, len(self.fleet)-1]:
            self.url_list(i) = str(self.fleet(i)) + self.url


    def request_list(self, endpoint, gp='GET'):
        #Send HTTP requests to every device in fleet list
        if gp == 'POST':
            #POST type request to submit data to server
            do something
        else:
            #GET type request to request data from server
            self.url_list = self.get_url_list(endpoint)
            self.requests = []
            self.messages = []

            for i in [0, len(self.fleet)-1]:
                self.requests(i) = requests.get(url = self.url_list(i))
                self.messages(i) = self.requests(i).json()






"""
    def pull_image(self, url):
        return self.town_api.pull_image(url)

    def monitor_id(self, id):
        return self.town_api.monitor_id(id)

    def clear_job_log(self):
        return self.town_api.clear_job_log
"""


'''
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
