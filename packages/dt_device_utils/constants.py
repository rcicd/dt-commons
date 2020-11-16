from enum import IntEnum

ETH0_DEVICE_MAC_FILE = "/data/stats/MAC/eth0"
CONFIG_DIR = "/data/config/"


class DeviceHardwareBrand(IntEnum):
    UNKNOWN = 0
    RASPBERRY_PI = 1
    JETSON_NANO = 2


class DeviceHardwareModel(IntEnum):
    UNKNOWN = 0
    # Raspberry Pi Family
    RASPBERRY_PI_2 = 1
    RASPBERRY_PI_3B = 2
    RASPBERRY_PI_3B_PLUS = 3
    RASPBERRY_PI_4B = 4
    # Jetson Nano Family
    JETSON_NANO = 11
    JETSON_NANO_2GB = 12
