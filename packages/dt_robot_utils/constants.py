from enum import IntEnum


class RobotType(IntEnum):
    UNKNOWN = 0
    DUCKIEBOT = 1
    WATCHTOWER = 2
    TRAFFIC_LIGHT = 3
    DUCKIETOWN = 4
    DUCKIEDRONE = 5

    _from_string = {
        '__NOTSET__': UNKNOWN,
        'duckiebot': DUCKIEBOT,
        'watchtower': WATCHTOWER,
        'traffic_light': TRAFFIC_LIGHT,
        'duckietown': DUCKIETOWN,
        'duckiedrone': DUCKIEDRONE
    }

    @classmethod
    def from_string(cls, rtype: str) -> 'RobotType':
        if rtype in cls._from_string:
            return cls._from_string[rtype]
        return RobotType.UNKNOWN
