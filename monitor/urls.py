from django.urls import path

from monitor import views

urlpatterns = [
    path("", views.index, name="index"),
]
