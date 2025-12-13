from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("ask/", views.get_ask, name="ask")
]