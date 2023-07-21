from django.contrib.gis.db import models
from rest_framework import serializers


def validation(value):
    if not value.is_valid():
        raise serializers.ValidationError(value.is_valid_reason)


class Building(models.Model):
    geom = models.GeometryField(srid=4326, validators=[validation])
    address = models.CharField(max_length=255)

    def __str__(self):
        return str(type(self.geom)) + str(self.geom)
