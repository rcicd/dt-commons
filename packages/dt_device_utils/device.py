import os
import socket
import logging

import requests

from .constants import \
    ETH0_DEVICE_MAC_FILE, \
    DeviceHardwareBrand


# create logger
logging.basicConfig()
logger = logging.getLogger(os.environ.get('DT_MODULE_TYPE', 'module') + '.device')
logger.setLevel(logging.INFO)
if 'DEBUG' in os.environ and os.environ['DEBUG'].lower() in ['true', 'yes', '1']:
    logger.setLevel(logging.DEBUG)


def get_device_id() -> str:
    if not os.path.isfile(ETH0_DEVICE_MAC_FILE):
        msg = f"File '{ETH0_DEVICE_MAC_FILE}' not found. Cannot compute unique device ID."
        logger.error(msg)
        raise ValueError(msg)
    # read MAC from file
    with open(ETH0_DEVICE_MAC_FILE, 'rt') as fin:
        mac = fin.read().strip()
    # turn MAC into a unique ID
    device_id = mac.replace(':', '').strip()
    # make sure we have a valid MAC address
    if len(device_id) != 12:
        msg = f"Invalid MAC address '{mac}'. Cannot compute unique device ID."
        logger.error(msg)
        raise ValueError(msg)
    # ---
    return device_id


def get_device_hostname() -> str:
    return socket.gethostname()


def get_device_hardware_brand() -> DeviceHardwareBrand:
    hw = os.environ.get('ROBOT_HARDWARE', 'UNKNOWN')
    if hw == 'raspberry_pi':
        return DeviceHardwareBrand.RASPBERRY_PI
    elif hw == 'jetson_nano':
        return DeviceHardwareBrand.JETSON_NANO
    # ---
    return DeviceHardwareBrand.UNKNOWN


def _device_trigger(trigger: str, quiet: bool = True) -> bool:
    hostname = get_device_hostname()
    url = f"http://{hostname}.local/health/trigger/{trigger}"
    # ---
    try:
        data = requests.get(url).json()
        assert data['status'] == 'needs-confirmation'
        assert 'token' in data
        token = data['token']
        url += f"?token={token}"
        data = requests.get(url).json()
        assert data['status'] == 'ok'
    except BaseException as e:
        if quiet:
            logger.error(str(e))
            return False
        else:
            raise e
    # ---
    return True


def shutdown_device(quiet: bool = True) -> bool:
    return _device_trigger('shutdown', quiet=quiet)


def reboot_device(quiet: bool = True) -> bool:
    return _device_trigger('reboot', quiet=quiet)
