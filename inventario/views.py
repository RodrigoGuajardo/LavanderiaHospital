from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages

def home(request):
    return render(request, 'inventario/index.html')
def irLogin(request):
    return render(request,'inventario/login.html')
def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión.")
    return redirect('inventario:login')

def registrar_transaccion(request):
    if request.method == 'POST':
        service_id = request.POST.get('service')
        laundry_id = request.POST.get('laundry')
        clothing_type_id = request.POST.get('clothing_type')
        transaction_type = request.POST.get('transaction_type')
        clothing_status = request.POST.get('clothing_status')
        cantidad = request.POST.get('cantidad')
        inventory = ClothingInventory(
            service_id=service_id,
            laundry_id=laundry_id,
            clothing_type_id=clothing_type_id,
            transaction_type=transaction_type,
            clothing_status=clothing_status,
            cantidad=cantidad
        )
        inventory.save()
        messages.success(request, 'Registro de inventario exitoso.')
        return render(request, 'inventario/ingresoegreso.html')
    services = ClinicalService.objects.all()
    laundries = ExternalLaundry.objects.all()
    clothing_types = ClothingType.objects.all()
    context = {
        'services': services,
        'laundries': laundries,
        'clothing_types': clothing_types
    }
    return render(request, 'inventario/ingresoegreso.html', context)


def generar_reportes(request):
    reportajes = ClothingInventory.objects.all()

    context = {
        'reportajes': reportajes
    }
    return render(request, 'inventario/reportes.html', context)

def registro(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inventario:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'inventario/registro.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'inventario/register.html', {'form': form})

# Vista de Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Inicio de sesión exitoso.")
                return redirect('inventario:home')  # Redirige a la página principal o a donde desees
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
    return render(request, 'inventario/login.html', {'form': form})
