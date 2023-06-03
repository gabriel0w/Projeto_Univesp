# deepemotion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.deep_emotion, name='deep_emotion'),
    path('upload/', views.upload_file, name='upload'),
    path('confirm/', views.confirm, name='confirm'),
    path('upload_second/', views.upload_second_file, name='upload_second'),
    path('confirm_second/', views.confirm_second, name='confirm_second'),
    path('create_person/', views.create_person, name='create_person'),
    path('data_visualization/', views.data_visualization, name='data_visualization'),
    path('populate_db/', views.populate_data_base, name='populatedatabase'),
]
