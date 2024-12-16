from django.urls import path
from . import views
from.views import *
from .views import register_view  # Asegúrate de que esta línea esté presente
from django.contrib.auth.views import LoginView



app_name = 'inventario'

urlpatterns = [
    path('gestionar_ropa_sucia/', gestionar_ropa_sucia, name='gestionar_ropa_sucia'),
    path('home/', views.home, name='home'),
    path('',home, name="home"), 
    path('irLogin',views.irLogin,name="irLogin"),
    path('registro/', views.register_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reportes', views.generar_reportes, name="reportes"),
    path('ingresoegreso', views.registrar_transaccion, name="ingresoegreso"),
    path('registro',views.register_view, name="registro"),
    path('reportes',generar_reportes,name="reportes"),
    path('ingresar_ropa/', views.ingresar_ropa, name='ingresar_ropa'),
    path('asignar_ropa/', asignar_ropa, name='asignar_ropa'),
    
]