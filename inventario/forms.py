from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import *

class ClothingForm(forms.ModelForm):
    class Meta:
        model = Clothing
        fields = ['nombre', 'cantidad']  # Asegúrate de que estos campos existan en tu modelo

class ClothingServiceForm(forms.ModelForm):
    TRANSACTION_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
    ]

    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, label="Tipo de Transacción")

    class Meta:
        model = ClothingServices
        fields = ['cantidad', 'servicio', 'tipo_ropa', 'transaction_type']

    servicio = forms.ModelChoiceField(queryset=ClinicalService.objects.all(), label="Servicio Clínico")
    tipo_ropa = forms.ModelChoiceField(queryset=Clothing.objects.all(), label="Tipo de Ropa")

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get("cantidad")
        tipo_ropa = cleaned_data.get("tipo_ropa")
        transaction_type = cleaned_data.get("transaction_type")

        # Verificar que la cantidad no exceda la cantidad disponible en Clothing para egreso
        if transaction_type == 'egreso' and tipo_ropa is not None:
            if cantidad > tipo_ropa.cantidad:
                self.add_error('cantidad', f"La cantidad no puede exceder {tipo_ropa.cantidad}.")

        return cleaned_data


class ClothingCleaningForm(forms.ModelForm):
    TRANSACTION_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
    ]

    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, label="Tipo de Transacción")

    class Meta:
        model = ClothingCleanings  # Cambiado a ClothingCleanings
        fields = ['nombre', 'cantidad', 'transaction_type', 'lavanderia']

    nombre = forms.ModelChoiceField(queryset=ClothingDirt.objects.all(), label="Ropa Sucia")
    lavanderia = forms.ModelChoiceField(queryset=ExternalLaundry.objects.all(), label="Lavandería")



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

