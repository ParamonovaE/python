from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import viewsets
from .models import Building
from .serializers import BuildingSerializer
from rest_framework.exceptions import ParseError
from rest_framework_gis import filters as geofilters
from rest_framework.filters import BaseFilterBackend
from django.contrib.gis.db.models.functions import Transform


def index(request):
    return HttpResponse("Страница приложения Building")


def pageNotFound(reguest, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


class AreaFilterQueryset(BaseFilterBackend):
    min_param = 'min'
    max_param = 'max'
    def get_filter_max(self, request, **kwargs):
        max_string = request.query_params.get(self.max_param, None)
        if not max_string:
            return None
        try:
            x = float(max_string)
        except ValueError:
            raise ParseError('Неверный параметр')
        return x

    def get_filter_min(self, request, **kwargs):
        min_string = request.query_params.get(self.min_param, None)
        if not min_string:
            return None
        try:
            x = float(min_string)
        except ValueError:
            raise ParseError('Неверный параметр')
        return x

    def filter_queryset(self, request, queryset, view):
        values = queryset.values()
        min = self.get_filter_min(request)
        max = self.get_filter_max(request)
        if min is None and max is None:
            return queryset
        elif min is None:
            print(max)
            return list(filter(lambda x: x["geom1"].area <= max, values))
        elif max is None:
            print(min)
            return list(filter(lambda x: min <= x["geom1"].area, values))
        else:
            print(min, max)
            return list(filter(lambda x: min <= x["geom1"].area <= max, values))
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    filter_backends = (geofilters.DistanceToPointFilter, AreaFilterQueryset)
    distance_filter_field = 'geom'
    distance_filter_convert_meters = True # чтобы преобразовать входное расстояние в метрах в градусы

    def get_queryset(self, *args, **kwargs):
        min = self.request.query_params.get('min', None)
        max = self.request.query_params.get('max', None)
        if not min and not max:
            ann = Building.objects.all()
        else:
            ann = Building.objects. \
                annotate(geom1=Transform('geom', 27700, clone=False))
        return ann
