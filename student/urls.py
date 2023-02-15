from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_home,name='studentregister'),
    path('test/', views.test_page),
    path('vidfeed/', views.vidfeed_dataset,name="vidfeed"),
]