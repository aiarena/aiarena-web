from django.contrib import admin
from django.urls import path
from aiarena.api import views


urlpatterns = [
    path('hello/', views.hello_world),
]
