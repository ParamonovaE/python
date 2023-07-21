from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers
from .models import Building


class BuildingSerializer(geo_serializers.GeoFeatureModelSerializer):
    class Meta:
        geo_field = 'geom'
        model = Building
        fields = ['id', 'geom', 'address']

