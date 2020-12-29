from enum import IntEnum


class RobotType(IntEnum):
    UNKNOWN = 0
    DUCKIEBOT = 1
    WATCHTOWER = 2
    TRAFFIC_LIGHT = 3
    DUCKIETOWN = 4
    DUCKIEDRONE = 5

    @classmethod
    def from_string(cls, rtype: str) -> 'RobotType':
        _from_string = {
            '__NOTSET__': RobotType.UNKNOWN,
            'duckiebot': RobotType.DUCKIEBOT,
            'watchtower': RobotType.WATCHTOWER,
            'traffic_light': RobotType.TRAFFIC_LIGHT,
            'duckietown': RobotType.DUCKIETOWN,
            'duckiedrone': RobotType.DUCKIEDRONE
        }
        if rtype in _from_string:
            return _from_string[rtype]
        return RobotType.UNKNOWN


class RobotConfiguration(IntEnum):
    UNKNOWN = 0
    # Duckiebot
    DB18 = 10
    DB19 = 11
    DB20 = 12
    DB21 = 13
    # Watchtower
    WT18 = 20
    WT19A = 21
    WT19B = 22
    # Traffic Light
    TL18 = 30
    TL19 = 31
    # Green Station
    GS17 = 40
    # Duckietown
    DT20 = 50
    # Duckiedrone
    DD18 = 60

    @classmethod
    def from_string(cls, name) -> 'RobotConfiguration':
        for robot_cfg in RobotConfiguration:
            if robot_cfg.name == name:
                return robot_cfg
        return RobotConfiguration.UNKNOWN
