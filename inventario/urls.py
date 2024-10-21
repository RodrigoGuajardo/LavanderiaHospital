from django.urls import path,include,reverse
from . import views
from.views import *
from django.contrib.auth.views import LoginView



app_name = 'inventario'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('',home, name="home"), 
    path('login',login_view, name="login"),
    path('ingresoegreso', views.registrar_transaccion, name="ingresoegreso"),
    path('registro',registro, name="registro"),
    path('reportes',generar_reportes,name="reportes")
]