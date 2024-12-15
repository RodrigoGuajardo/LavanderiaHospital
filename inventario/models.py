from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class ClinicalService(models.Model):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    responsable = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class ExternalLaundry(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class Clothing(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    def __str__(self):
        return self.nombre  # Esto devolverá el nombre de la ropa

    
class ClothingDirt(models.Model):
    nombre = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    tipo_ropa = models.ForeignKey(Clothing, on_delete=models.CASCADE)  # Relación con Clothing

    def __str__(self):
        return self.nombre

class ClothingCleaning(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    lavanderia = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre
    
class ClothingCleanings(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_ropa = models.ForeignKey(Clothing, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)
    lavanderia = models.ForeignKey(ExternalLaundry, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.tipo_ropa.nombre} en {self.lavanderia.nombre}"



class ClothingService(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    servicio = models.CharField(max_length=255)
    
class ClothingServices(models.Model):
    tipo_ropa = models.ForeignKey(Clothing, on_delete=models.CASCADE)
    servicio = models.ForeignKey(ClinicalService, on_delete=models.CASCADE)  # Asegúrate de que esto sea un ForeignKey
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.tipo_ropa.nombre} - {self.servicio.nombre}"

class ClothingType(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


# Modelo para el stock actual de ropa limpia
class ClothingInventory(models.Model):
    service = models.ForeignKey(ClinicalService, on_delete=models.CASCADE)
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.CASCADE)
    cantidad_disponible = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.cantidad_disponible} - {self.clothing_type.nombre} en {self.service.nombre}"


# Modelo para el manejo de ropa sucia
class DirtyClothing(models.Model):
    service = models.ForeignKey(ClinicalService, on_delete=models.CASCADE)
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    laundry = models.ForeignKey(ExternalLaundry, on_delete=models.CASCADE, null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    en_proceso = models.BooleanField(default=False)

    def __str__(self):
        estado = "En proceso" if self.en_proceso else "Pendiente"
        return f"{self.cantidad} - {self.clothing_type.nombre} ({estado}) en {self.service.nombre}"



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", max_length=100)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
