from rest_framework import serializers


class TravelerCalendarSerializer(
    serializers.Serializer
):

    blocked_dates = serializers.ListField()

    reserved_dates = serializers.ListField()

    hold_dates = serializers.ListField()