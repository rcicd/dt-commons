#!/usr/bin/env python3
#This script is part of the DT Architecture Library for dt-commons

import docker
import os
import time

from zeroconf import ServiceBrowser, Zeroconf
#from dt_archapi_utils.arch_message import ApiMessage, JobLog


'''
    THIS SCRIPT USES THE AVAHI SERVICES TO LISTEN TO THE NETWORK AND UPDATES THE
    AVAILABLE DEVICES THE MultiArchAPIClient COULD USE. SELF.CURRENT_DEVICES AND
    SELF.PREVIOUS ARE OF TYPE LIST.
'''

def wait_for_service(target_service: str, target_hostname: str = None, timeout: int = 10):
    # define callbacks
    workspace = SimpleNamespace(service=target_service, hostname=target_hostname, data=None)

    def cb(service: str, hostname: str, data: dict):
        if target_service == service and target_hostname == hostname:
            workspace.data = data
            workspace.service = service
            workspace.hostname = hostname

    # perform discover
    zeroconf = Zeroconf()
    listener = DiscoverListener(service_in_callback=cb)
    ServiceBrowser(zeroconf, "_duckietown._tcp.local.", listener)
    # wait
    stime = time.time()
    while workspace.data is None:
        time.sleep(0.5)
        if (timeout > 0) and (time.time() - stime > timeout):
            msg = f'No devices matched the search criteria (service={target_service}, hostname={target_hostname}).'
            zeroconf.close()
            raise TimeoutError(msg)
    zeroconf.close()
    
    return workspace.service, workspace.hostname, workspace.data


class FleetScanner:
    def __init__(self, service_in_callback=None, service_out_callback=None):
        self.service_in_callback = service_in_callback
        self.service_out_callback = service_out_callback


    def _process_service(self, zeroconf, type, servicename):
        #example servicename = DT::PRESENCE::._duckietown._tcp.local.hostname
        #format local (network), tcp (communication, vs. udp), duckietown (depending on application)
        print(servicename)
        name = servicename.replace('._duckietown._tcp.local.', '')
        print(name)
        service_parts = name.split('::')

        #Check if format is correct
        if len(service_parts) != 3 or service_parts[0] != 'DT':
            return None, None, dict()
        #Store, name[1] is type of service
        name = '{}::{}'.format(service_parts[0], service_parts[1])
        hostname = service_parts[2]
        txt = dict()

        try:
            serviceinfo = zeroconf.get_service_info(type, servicename)
            txt = json.loads(list(serviceinfo.properties.keys())[0].decode('utf-8')) \
                if len(serviceinfo.properties) \
                else dict()
        except:
            pass
        return name, hostname, txt


    def remove_service(self, zeroconf, type, sname):
        #type is free msg payload, here JSON string
        name, hostname, txt = self._process_service(zeroconf, type, sname)
        dtslogger.debug(f'Zeroconf:SERVICE_OUT (name={name}, hostname={hostname}, data={txt})')
        if not name:
            return
        if self.service_out_callback:
            self.service_out_callback(name, hostname, txt)


    def add_service(self, zeroconf, type, sname):
        #type is free msg payload, here JSON string
        name, hostname, txt = self._process_service(zeroconf, type, sname)
        dtslogger.debug(f'Zeroconf:SERVICE_IN (name={name}, hostname={hostname}, data={txt})')
        if not name:
            return
        if self.service_in_callback:
            self.service_in_callback(name, hostname, txt)


"""
    def __init__(self):
        self.current_devices = {}
        self.previous = {}

        #Initialize imported classes
        self.status = ApiMessage()
        self.manager = Manager()
        self.log = self.manager.dict()
        self.process = None


    def listen_to_network(self):
        self.current_devices = {} #CPU expensive? only add/delete from list, don't start all over again
        self.add_service(add to self.current_devices)
        #self.current_devices = self.previous
        disappear_msg, appear_msg = self.network_update_message()

        return self.current_devices, appear_msg


#MOVE TO DASHBOARD CONTAINER - don't include a message inside the return, Dashboard will generate this
#message based on the fleet file it is reading and the returned list of current & previous devices
    def network_update_message(self):
        if self.previous == self.current_devices:
            disappeared = {}
            appeared = {}
        else:
            #which devices disappeared - used for unavailabilities in existing fleets
            remainder_previous = list(set(self.previous) - set(self.current_devices))
            for hostname in remainder_previous:
                disappeared = {}
                disappeared[hostname] = "currently unavailable"

            #which devices appeared - used for available device overview
            remainder_current = list(set(self.current_devices) - set(self.previous))
            for hostname in remainder_current:
                appeared = {}
                appeared[hostname] = "just entered the network"

        self.store_available_devices()
        return disappeared, appeared


    def store_available_devices(self):
        self.previous = self.current_devices
"""
