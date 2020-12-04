import os

from .constants import RobotType


def get_robot_type() -> RobotType:
    rtype = os.environ.get('ROBOT_TYPE', '__NOTSET__')
    return RobotType.from_string(rtype)
