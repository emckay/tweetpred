from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'data_files', views.DataFileViewSet)
router.register(r'estimates', views.EstimateViewSet)
router.register(r'predictions', views.PredictionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
