from django.urls import path
from . import views
from.views import *
from django.contrib.auth.views import LoginView


app_name = 'inventario'

urlpatterns = [
    path('registrar/', views.registrar_transaccion, name='registrar_transaccion'),
    path('',home, name="home"),
    path('registro',registro, name="registro"),
]