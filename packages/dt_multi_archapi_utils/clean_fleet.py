#!/usr/bin/env python3
#This script is part of the DT Architecture Library for dt-commons

import yaml
import os
import time

from dt_archapi_utils.arch_message import ApiMessage

'''
    THIS SCRIPT TAKES IN A FLEET .YAML FILE AS SPECIFIED IN THE DESIGN DOCUMENT.
    IT RETURNS A MORE CLEAN AND STRIPPED VERSION OF THE FLEET FILE, WITH ONLY
    THE HOSTNAMES OF THE DEVICES LISTED IN THE FLEET.
'''

class CleanFleet:
    def __init__(self, hostname="hostname"):
        self.hostname = hostname
        self.status = ApiMessage()


    def clean_list(self, fleet=None):
        #Warning
        if fleet is None:
            print("No fleet specified for " + hostname + ", please specify to avoid errors... using default file")
            fleet = "default_device_list"
            #redundant? - might not accept the endpoint anyway
            #return self.status.error(status="error", msg="No fleet was specified, use /fleet/.../<fleet>")

        #For testing & development only
        fleet_path = "/data/assets/dt-architecture-data/lists"
        path_to_list = fleet_path + "/" + fleet + ".yaml"
        try:
            with open(path_to_list, 'r') as f:
                file = yaml.load(f, Loader=yaml.FullLoader)
                fleet_list = file["devices"]
            return fleet_list

        except FileNotFoundError: #error msg
            return self.status.error(status="error", msg="data cannot be JSON decoded")

"""
        #Use fleet file written to disc through Dashboard
        if os.path.isdir("/data/config/fleets"):
            #For testing & development only
            fleet_path = "/data/config/fleets"
            path_to_list = fleet_path + "/" + str(fleet) + ".yaml"
            try:
                with open(path_to_list, 'r') as f:
                    file = yaml.load(f, Loader=yaml.FullLoader)
                    fleet_list = file["devices"]
                return fleet_list

            except FileNotFoundError: #error msg
                return self.status.error(status="error", msg="Fleet file could not be found in " + path_to_list)
        else:
            return self.status.error(status="error", msg="No such directory /data/config/fleets - create or reflash using ente")
"""
