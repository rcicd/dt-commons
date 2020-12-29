import os

from .constants import RobotType, RobotConfiguration


def get_robot_type() -> RobotType:
    rtype = os.environ.get('ROBOT_TYPE', '__NOTSET__')
    return RobotType.from_string(rtype)


def get_robot_configuration() -> RobotConfiguration:
    rcfg = os.environ.get('ROBOT_CONFIGURATION', 'UNKNOWN')
    return RobotConfiguration.from_string(rcfg)
