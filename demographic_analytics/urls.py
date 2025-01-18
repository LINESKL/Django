from django.urls import path
from .views import FirstLevelAPIView, CountryAPIView

urlpatterns = [
    path('stats/region/<str:region_name>/', FirstLevelAPIView.as_view(), name='first_level_stats'),
    path('allstats/', CountryAPIView.as_view(), name='country_stats'),
]