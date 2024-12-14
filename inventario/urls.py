from django.urls import path
from . import views
from.views import *
from django.contrib.auth.views import LoginView



app_name = 'inventario'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('',home, name="home"), 
    path('irLogin',views.irLogin,name="irLogin"),
    path('registro/', views.register_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reportes', views.generar_reportes, name="reportes"),
    path('ingresoegreso', views.registrar_transaccion, name="ingresoegreso"),
    path('registro',registro, name="registro"),
    path('reportes',generar_reportes,name="reportes")
]