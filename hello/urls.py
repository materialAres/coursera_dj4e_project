from django.urls import path

from . import views


app_name = 'hello'

urlpatterns = [
    path('', views.session_view),
    ]
