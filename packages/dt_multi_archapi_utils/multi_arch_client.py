#!/usr/bin/env python3
#This script is part of the DT Architecture Library for dt-commons

import yaml
import docker
import os
import git
import glob
import requests
import json

from .device_list import DeviceList
from .multi_arch_worker import MultiApiWorker
from .clean_fleet import CleanFleet

#Import from another folder within dt-commons (no base image)
from dt_archapi_utils.arch_client import ArchAPIClient
from dt_archapi_utils.arch_message import ApiMessage

'''
    THIS LIB INCLUDES FUNCTIONS THAT ALLOW TO COMMUNICATE WITH AN EXTENDED
    ARCHITECTURE API RUNNING ON A SINGLE (PRIVILEGED) ROBOT AND ALLOW TO CONTROL
    A SO CALLED FLEET THROUGH THIS ROBOT BY PASSING A SINGLE HTTP COMMAND. NOTE
    THAT THIS LIB DOES NOT SPECIFY THE REQUIRED API FOR THAT. I.E. THE
    REQUIRED SERVER IS NOT RUNNING WITHIN THE LIBRARY
'''

class MultiArchAPIClient:
    def __init__(self, client=None, port="8083"): #fleet as yaml file without .yaml
        self.client = client
        self.port = port

        #Initialize folders and classes
        self.current_configuration = "none"
        self.dt_version = "ente"
        self.status = ApiMessage()
        self.cl_fleet = CleanFleet()

        #Define robot_type
        self.robot_type = "none"
        if os.path.isfile("/data/config/robot_type"):
            self.robot_type = open("/data/config/robot_type").readline()
        elif os.path.isfile("/data/stats/init_sd_card/parameters/robot_type"):
            self.robot_type = open("/data/stats/init_sd_card/parameters/robot_type").readline()
        else: #error upon initialization
            self.status("error", "Could not find robot type in expected paths", None)

        #Give main robot an ArchAPIClient
        self.main_name = os.environ['VEHICLE_NAME']
        self.main_api = ArchAPIClient(hostname=self.main_name, robot_type=self.robot_type, client=self.client)
        self.config_path = self.main_api.config_path
        self.module_path = self.main_api.module_path


    #RESPONSE MESSAGES: extended with device info from fleet file
    #Passive Messaging
    def default_response(self, fleet):
        #Initialize worker with fleet and port
        fleet = self.cl_fleet.clean_list(fleet)
        self.work = MultiApiWorker(fleet=fleet, port=self.port)

        #Initialize with main response
        def_response_list = self.main_api.default_response

        #if def_response_list["status"] is 'ok':
        def_response_list["data"] = None
        #Proceed with messages from fleet
        for name in fleet:
            def_response_list["data"][name] = self.work.http_get_request(device=name, endpoint='/')
        return def_response_list

        #else: #return only error from controlling device
        #    return def_response_list


    def configuration_info(self, config, fleet):
        #Initialize worker with fleet and port
        fleet = self.cl_fleet.clean_list(fleet)
        self.work = MultiApiWorker(fleet=fleet, port=self.port)

        #Initialize with main response & check on error
        config_info = self.main_api.configuration_info(config)
        #if config_info["status"] != "error":
        #Proceed with messages from fleet devices in configuration file
        try:
            with open(self.config_path + "/" + config + ".yaml", 'r') as file:
                device_info = yaml.load(file, Loader=yaml.FullLoader)
                print(device_info)
                print("devices" in device_info)
                if "devices" in device_info:
                    devs = device_info["devices"]

                    if "duckiebot" in device_info["devices"]:
                        if "configuration" in devs["duckiebot"]:
                            db_configuration = devs["duckiebot"]["configuration"]
                            for db_conf in db_configuration:
                                #Danger - Retrieve static dt-architecture-data info using ArchAPIClient functions,
                                #without client specified! We do not want an option to change the robot_type within
                                #the already defined ArchAPIClient. This would not follow the ArchAPI approach.
                                new_robot_type_as_duckiebot = ArchAPIClient(robot_type="duckiebot")
                                db_configuration[str(db_conf)] = new_robot_type_as_duckiebot.configuration_info(db_conf)

                    if "watchtower" in device_info["devices"]:
                        if "configuration" in devs["watchtower"]:
                            wt_configuration = devs["watchtower"]["configuration"]
                            for wt_conf in wt_configuration:
                                new_robot_type_as_watchtower = ArchAPIClient(robot_type="watchtower")
                                wt_configuration[str(wt_conf)] = new_robot_type_as_watchtower.configuration_info(wt_conf)

                    if "greenstation" in device_info["devices"]:
                        if "configuration" in devs["greenstation"]:
                            gs_configuration = devs["greenstation"]["configuration"]
                            for gs_conf in gs_configuration:
                                new_robot_type_as_greenstation = ArchAPIClient(robot_type="greenstation")
                                gs_configuration[str(gs_conf)] = new_robot_type_as_greenstation.configuration_info(gs_conf)

                    if "duckiedrone" in device_info["devices"]:
                        if "configuration" in devs["greenstation"]:
                            dd_configuration = devs["greenstation"]["configuration"]
                            for dd_conf in dd_configuration:
                                new_robot_type_as_duckiedrone = ArchAPIClient(robot_type="duckiedrone")
                                dd_configuration[str(dd_conf)] = new_robot_type_as_duckiedrone.configuration_info(dd_conf)

                    #Append retracted info to config_info
                    config_info["devices"] = device_info["devices"]

                return config_info

        except FileNotFoundError: #error msg
            return self.status.error(status="error", msg="Configuration file not found in " + self.config_path + "/" + config + ".yaml")

        #else: #error msg
        #    return config_info


"""
    def configuration_list(self, fleet=None):
        #Initialize worker with fleet and port
        fleet = self.cl_fleet.clean_list(fleet)
        self.work = MultiApiWorker(fleet=fleet, port=self.port)

        #SCAN FLEET = LISTEN TO AVAHI SERVICES
        config_list = {} #re-initialize every time called for (empty when error)
        current_fleet = self.scan.for_devices
        config_list[str(self.main_name)] = self.main_api.configuration_list
        if self.config_path is not None:
            config_paths = glob.glob(self.config_path + "/*.yaml")
            config_list["configurations"] = [os.path.splitext(os.path.basename(f))[0] for f in config_paths]
        else: #error msg
            self.status["status"] = "error"
            self.status["message"].append("could not find configurations (dt-docker-data)")
            return self.status
        return config_list
"""




"""
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





'''
    def pull_image(self, url):
        return self.town_api.pull_image(url)

    def monitor_id(self, id):
        return self.town_api.monitor_id(id)

    def clear_job_log(self):
        return self.town_api.clear_job_log
'''


'''
        #Give every device in fleet an ArchAPIClient
        for i in [0, len(self.fleet)-1]:
            self.multi_api = []
            self.multi_api(i) = self.api(self.fleet(i), self.client)
'''


"""
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
"""
