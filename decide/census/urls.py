from django.urls import path, include
from . import views
from django.http import HttpResponse



urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('addCustom/', views.create_census, name='create_census'),
    path('addFilters/', views.add_filtered, name='add_filtered'),
]
