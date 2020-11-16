import os
import socket
import logging
from typing import Optional

from .constants import \
    ETH0_DEVICE_MAC_FILE, \
    CONFIG_DIR, \
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
    return DeviceHardwareBrand.UNKNOWN


def get_device_tag_id() -> Optional[int]:
    """
    Reads the ID of the (April) Tag attached to the robot from disk and returns it as an int.

    :return: Robot's tag ID if it is set, None if the ID is not set.
    :rtype: Optional[int]
    """
    tag_id_filename = os.path.join(CONFIG_DIR, 'robot_tag_id')
    tag_id = None
    # try to read the tag from file and parse it as int
    if os.path.isfile(tag_id_filename):
        try:
            with open(tag_id_filename, 'rt') as fin:
                tag_id = int(fin.read().strip().lower())
        except BaseException as e:
            logger.error(f"Could not read the tag ID from file `{tag_id_filename}`. "
                         f"The error reads: {str(e)}")
    # negative values turn into None
    if tag_id is None or tag_id < 0:
        return None
    # return tag ID
    return tag_id
