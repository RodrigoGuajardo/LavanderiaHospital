from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.db.models import F



def generar_reportes(request):
    # Recuperar filtros del formulario
    tipo_ropa = request.GET.get('tipo_ropa', '')
    tipo_transaccion = request.GET.get('tipo_transaccion', '')
    servicio_clinico = request.GET.get('servicio_clinico', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar transacciones
    resultados = ClothingInventory.objects.all()

    if tipo_ropa:
        resultados = resultados.filter(clothing_type__nombre__icontains=tipo_ropa)
    if tipo_transaccion:
        resultados = resultados.filter(transaction_type=tipo_transaccion)
    if servicio_clinico:
        resultados = resultados.filter(service__nombre__icontains=servicio_clinico)
    if fecha_inicio and fecha_fin:
        resultados = resultados.filter(fecha_transaccion__range=[fecha_inicio, fecha_fin])

    return render(request, 'reportes.html', {'resultados': resultados})

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
        transaction_type = request.POST.get('transaction_type')
        clothing_type_id = request.POST.get('clothing_type')
        service_id = request.POST.get('service')
        cantidad = int(request.POST.get('cantidad'))
        
        if transaction_type == "ingreso_limpia":
            # Ropa limpia
            inventory, created = ClothingInventory.objects.get_or_create(
                service_id=service_id,
                clothing_type_id=clothing_type_id,
                defaults={'cantidad_disponible': 0}
            )
            inventory.cantidad_disponible += cantidad
            inventory.save()
            messages.success(request, "Ingreso de ropa limpia registrado.")
        elif transaction_type == "ingreso_sucia":
            # Ropa sucia
            laundry_id = request.POST.get('laundry')
            DirtyClothing.objects.create(
                service_id=service_id,
                clothing_type_id=clothing_type_id,
                cantidad=cantidad,
                laundry_id=laundry_id,
                en_proceso=False
            )
            messages.success(request, "Ingreso de ropa sucia registrado.")
        else:
            messages.error(request, "Transacción no válida.")
        return redirect('inventario:ingresoegreso')

    context = {
        'services': ClinicalService.objects.all(),
        'laundries': ExternalLaundry.objects.all(),
        'clothing_types': ClothingType.objects.all()
    }
    return render(request, 'inventario/ingresoegreso.html', context)

def get_context():
    return {
        'services': ClinicalService.objects.all(),
        'laundries': ExternalLaundry.objects.all(),
        'clothing_types': ClothingType.objects.all()
    }


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
