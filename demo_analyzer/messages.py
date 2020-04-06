from demo_analyzer import serializers


class Type(serializers.Serializer):
    type = serializers.ByteField()


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
    start_time = serializers.TimestampField(fmt='I')
    tickets1 = serializers.UInt16Field()
    tickets2 = serializers.UInt16Field()


class PlayerAdd(serializers.Serializer):
    id = serializers.UInt8Field()
    ign = serializers.StringField()
    hash = serializers.StringField()
    ip = serializers.StringField()


class PlayerRemove(serializers.Serializer):
    id = serializers.UInt8Field()


class Ticks(serializers.Serializer):
    ticks = serializers.UInt8Field()


class Kill(serializers.Serializer):
    attacker = serializers.UInt8Field()
    victim = serializers.UInt8Field()
    weapon = serializers.StringField()


class Revive(serializers.Serializer):
    medic = serializers.UInt8Field()
    patient = serializers.UInt8Field()


class TeamTickets(serializers.Serializer):
    tickets = serializers.UInt16Field()