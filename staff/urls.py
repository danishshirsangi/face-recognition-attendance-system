from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_home)
]