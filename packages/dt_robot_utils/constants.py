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
