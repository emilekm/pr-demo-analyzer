from demo_analyzer import constants, serializers
from demo_analyzer.constants import FormatStrings, MessageTypes


class MapSerializer(serializers.Serializer):
    name = serializers.StringField()
    gamemode = serializers.StringField()
    layer = serializers.UInt8Field()


class ServerDetails(serializers.Serializer):
    version = serializers.Int32Field()
    demo_time_per_tick = serializers.FloatField()
    ip_port = serializers.StringField()
    server_name = serializers.StringField()
    max_players = serializers.UInt8Field()
    round_length = serializers.UInt16Field()
    briefing_time = serializers.UInt16Field()
    map = MapSerializer()
    blufor_team = serializers.StringField()
    opfor_team = serializers.StringField()
    start_time = serializers.TimestampField(fmt=FormatStrings.UINT32)
    tickets1 = serializers.UInt16Field()
    tickets2 = serializers.UInt16Field()


class PlayerAdd(serializers.Serializer):
    id = serializers.UInt8Field()
    ign = serializers.StringField()
    hash = serializers.StringField()
    ip = serializers.StringField()

    class Meta:
        many = True


class PlayerVehicle(serializers.Serializer):
    id = serializers.Int16Field()
    seat_name = serializers.StringField()
    seat_number = serializers.Int8Field()

    def check_id(self, ret):
        if ret['id'] < 0:
            raise serializers.SkipField()

    def validate_seat_name(self, raw_value, ret):
        self.check_id(ret)

    def validate_seat_number(self, raw_value, ret):
        self.check_id(ret)



class Position(serializers.Serializer):
    x = serializers.Int16Field()
    y = serializers.Int16Field()
    z = serializers.Int16Field()


class PlayerUpdate(serializers.Serializer):
    flags = serializers.FlagsField(
        fmt=FormatStrings.UINT16,
        flags=constants.PlayerUpdateFlags,
    )
    id = serializers.UInt8Field()
    team = serializers.Int8Field()
    squad = serializers.UInt8Field()
    vehicle = PlayerVehicle()
    health = serializers.Int8Field()
    score = serializers.Int16Field()
    teamwork_score = serializers.Int16Field()
    kills = serializers.Int16Field()
    deaths = serializers.Int16Field()
    ping = serializers.Int16Field()
    is_alive = serializers.BoolField()
    is_joining = serializers.BoolField()
    position = Position()
    rotation = serializers.Int16Field()
    kit_name = serializers.StringField()

    class Meta:
        many = True


class PlayerRemove(serializers.Serializer):
    id = serializers.UInt8Field()


class VehicleAdd(serializers.Serializer):
    id = serializers.Int16Field()
    name = serializers.StringField()
    max_health = serializers.UInt16Field()

    class Meta:
        many = True


class VehicleUpdate(serializers.Serializer):
    flags = serializers.FlagsField(
        constants.VehicleUpdateFlags,
        fmt=FormatStrings.UINT8,
    )
    id = serializers.Int16Field()
    team = serializers.Int8Field()
    position = Position()
    rotation = serializers.Int16Field()
    health = serializers.Int8Field()

    class Meta:
        many = True


class VehicleDestroyed(serializers.Serializer):
    id = serializers.Int16Field()
    is_killer_known = serializers.BoolField()
    killer = serializers.UInt8Field()


class FobAdd(serializers.Serializer):
    id = serializers.Int32Field()
    team = serializers.Int8Field()
    position = Position()

    class Meta:
        many = True


class FobRemove(serializers.Serializer):
    id = serializers.Int32Field()

    class Meta:
        many = True


class Kill(serializers.Serializer):
    attacker = serializers.UInt8Field()
    victim = serializers.UInt8Field()
    weapon = serializers.StringField()


class Revive(serializers.Serializer):
    medic = serializers.UInt8Field()
    patient = serializers.UInt8Field()


class TeamTickets(serializers.Serializer):
    tickets = serializers.UInt16Field()


class Ticks(serializers.Serializer):
    ticks = serializers.UInt8Field()
