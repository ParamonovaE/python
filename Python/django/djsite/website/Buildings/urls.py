from rest_framework import routers
from .views import BuildingViewSet
from django.urls import path,include
router = routers.DefaultRouter()
router.register(r'buildings', BuildingViewSet)

urlpatterns = [
    path('api/', include(router.urls))
]
