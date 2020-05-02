#!/usr/bin/env python3
#This script is part of the DT Architecture Library for dt-commons

import docker
import os
import time
import requests as r

from multiprocessing import Process, Manager
from dt_archapi_utils.arch_message import ApiMessage, JobLog


'''
    THIS SCRIPT USES THE AVAHI SERVICES TO LISTEN TO THE NETWORK AND UPDATES THE
    AVAILABLE DEVICES THE MultiArchAPIClient COULD USE.
'''

class MultiApiWorker:
    def __init__(self, fleet=None, port="8083"):
        self.fleet = fleet
        self.port = port

        #Initialize imported classes
        self.status = ApiMessage()

        #Initialize imported classes - default from single worker
        self.manager = Manager()
        self.log = self.manager.dict()
        self.process = None


    def http_get_request(self, endpoint=None):
        message_list = {}
