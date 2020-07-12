from enum import Enum, IntFlag


class FormatStrings(Enum):
    BYTE = 'c'

    INT8 = 'b'
    UINT8 = 'B'

    INT16 = 'h'
    UINT16 = 'H'

    INT32 = 'i'
    UINT32 = 'I'

    INT64 = 'q'
    UINT64 = 'Q'

    FLOAT = 'f'
    BOOL = '?'


class MessageTypes(Enum):
    SERVER_DETAILS = b'\x00'
    DOD_LIST = b'\x01'


    PLAYER_UPDATE = b'\x10'
    PLAYER_ADD = b'\x11'
    PLAYER_REMOVE = b'\x12'

    VEHICLE_UPDATE = b'\x20'
    VEHICLE_ADD = b'\x21'
    VEHICLE_DESTROYED = b'\x22'

    FOB_ADD = b'\x30'
    FOB_REMOVE = b'\x31'

    FLAG_UPDATE = b'\x40'
    FLAG_LIST = b'\x41'

    KILL = b'\x50'
    CHAT = b'\x51'

    TICKETS_TEAM1 = b'\x52'
    TICKETS_TEAM2 = b'\x53'

    RALLY_ADD = b'\x60'
    RALLY_REMOVE = b'\x61'

    CACHE_ADD = b'\x70'
    CACHE_REMOVE = b'\x71'
    CACHE_REVEAL = b'\x72'
    INTEL_CHANGE = b'\x73'

    REVIVE = b'\xA0'
    KITALLOCATED = b'\xA1'
    SQUADNAME = b'\xA2'
    SLORDERS = b'\xA3'

    ROUNDEND = b'\xf0'
    TICKS = b'\xf1'


class PlayerUpdateFlags(IntFlag):
    team = 1
    squad = 2
    vehicle = 4
    health = 8
    score = 16
    teamwork_score = 32
    kills = 64
    teamkills = 128
    deaths = 256
    ping = 512
    is_alive = 2048
    is_joining = 4096
    position = 8192
    rotation = 16384
    kit_name = 32768


class VehicleUpdateFlags(IntFlag):
    team = 1
    position = 2
    rotation = 4
    health = 8
