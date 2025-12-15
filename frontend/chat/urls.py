from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dash/", views.dash, name="dash"),
    path("event/", views.event, name="event"),
    path("note/", views.note, name="note"),
    path("login/", views.login, name="login")
]