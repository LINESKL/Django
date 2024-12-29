from django.urls import path, include
from .views import (
    MaritalStatsAPIView,
    GenderDistributionAPIView,
    AgeDistributionAPIView,
    ChildrenStatsAPIView,
    BenefitsStatsAPIView,
    CountryStatisticsAPIView,
    AgeGenderDistributionAPIView,
    TrendsAPIView,
    RegionalComparisonAPIView,
    AnomalyDetectionAPIView,
    WeekdayActivityAPIView,
    SegmentationAPIView,
    UserFunctionsAPIView
)

urlpatterns = [
    path('country/', CountryStatisticsAPIView.as_view(), name='country_statistics'),
    path('region/<str:region_name>/gender/', GenderDistributionAPIView.as_view(), name='gender_distribution'),
    path('region/<str:region_name>/age/', AgeDistributionAPIView.as_view(), name='age_distribution'),
    path('region/<str:region_name>/children/', ChildrenStatsAPIView.as_view(), name='children_stats'),
    path('region/<str:region_name>/benefits/', BenefitsStatsAPIView.as_view(), name='benefits_stats'),
    path('region/<str:region_name>/marital/', MaritalStatsAPIView.as_view(), name='marital_stats'),
    path('region/<str:region_name>/age-gender/', AgeGenderDistributionAPIView.as_view(), name='age_gender_distribution'),
    path('region/<str:region_name>/functions/', UserFunctionsAPIView.as_view(), name='user_actions'),
    path('trends/', TrendsAPIView.as_view(), name='trends'),
    path('regions/', RegionalComparisonAPIView.as_view(), name='regions'),
    path('anomalies/', AnomalyDetectionAPIView.as_view(), name='anomalies'),
    path('weekday-activity/', WeekdayActivityAPIView.as_view(), name='weekday_activity'),
    path('age/', SegmentationAPIView.as_view(), name='age')


]

