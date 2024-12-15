from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.db.models import F


def ingresar_ropa(request):
    if request.method == 'POST':
        form = ClothingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ingreso de ropa registrado exitosamente.")
            return redirect('inventario:ingresar_ropa')  # Redirige a la página principal o donde desees
    else:
        form = ClothingForm()
    
    return render(request, 'inventario/ingresar_ropa.html', {'form': form})


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
        clothing_id = request.POST.get('clothing')  # Cambia a 'clothing' para obtener el ID de Clothing
        cantidad = int(request.POST.get('cantidad'))
        
        # Obtener el objeto Clothing correspondiente
        clothing = Clothing.objects.get(id=clothing_id)

        if transaction_type == "ingreso_limpia":
            # Ropa limpia
            # Aquí puedes manejar el ingreso de ropa limpia si es necesario
            clothing.cantidad += cantidad
            clothing.save()
            

            messages.success(request, "Ingreso de ropa limpia registrado.")
        elif transaction_type == "egreso":
            # Ropa egresada
            if clothing.cantidad >= cantidad:
                # Buscar si ya existe un registro en ClothingDirt para este tipo de ropa
                clothing_dirt, created = ClothingDirt.objects.get_or_create(
                    nombre=clothing.nombre,  # Usar el nombre de la ropa
                    defaults={'cantidad': 0}  # Inicializar cantidad en 0 si se crea un nuevo registro
                )
                
                # Sumar la cantidad al registro existente
                clothing_dirt.cantidad += cantidad
                clothing_dirt.save()

                # Actualizar la cantidad en Clothing
                clothing.cantidad -= cantidad
                clothing.save()

                messages.success(request, "Egreso de ropa registrado y cantidad sumada a ropa sucia.")
            else:
                messages.error(request, "No hay suficiente ropa en el inventario para realizar el egreso.")
        else:
            messages.error(request, "Transacción no válida.")
        
        return redirect('inventario:ingresoegreso')

    context = {
        'clothing_items': Clothing.objects.all()  # Cambia a clothing_items para obtener los nombres de ropa
    }
    return render(request, 'inventario/ingresoegreso.html', context)


def asignar_ropa(request):
    if request.method == 'POST':
        form = ClothingServiceForm(request.POST)
        if form.is_valid():
            tipo_ropa = form.cleaned_data['tipo_ropa']
            cantidad = form.cleaned_data['cantidad']
            servicio = form.cleaned_data['servicio']
            transaction_type = form.cleaned_data['transaction_type']

            if transaction_type == 'ingreso':
                # Lógica para ingreso
                if tipo_ropa.cantidad >= cantidad:  # Verificar que haya suficiente ropa
                    tipo_ropa.cantidad -= cantidad  # Restar de Clothing
                    tipo_ropa.save()

                    # Actualizar ClothingService
                    clothing_services, created = ClothingServices.objects.get_or_create(
                        tipo_ropa=tipo_ropa,
                        servicio=servicio,
                        defaults={'cantidad': 0}
                    )
                    clothing_services.cantidad += cantidad
                    clothing_services.save()

                    messages.success(request, "Ingreso de ropa registrado exitosamente.")
                else:
                    messages.error(request, "No hay suficiente ropa en el inventario para realizar el ingreso.")
                    
            elif transaction_type == 'egreso':
                # Lógica para egreso
                clothing_services = ClothingServices.objects.filter(tipo_ropa=tipo_ropa, servicio=servicio).first()
                if clothing_services and clothing_services.cantidad >= cantidad:
                    clothing_services.cantidad -= cantidad  # Restar de ClothingServices
                    clothing_services.save()

                    # Guardar en ClothingDirt
                    clothing_dirt, created = ClothingDirt.objects.get_or_create(
                        nombre=tipo_ropa.nombre,
                        defaults={'cantidad': 0}
                    )
                    clothing_dirt.cantidad += cantidad  # Sumar a ClothingDirt
                    clothing_dirt.save()

                    messages.success(request, "Egreso de ropa registrado y cantidad sumada a ropa sucia.")
                else:
                    messages.error(request, "No hay suficiente ropa en el servicio para realizar el egreso.")
                    
            return redirect('inventario:asignar_ropa')  # Redirigir a la misma página o a otra
    else:
        form = ClothingServiceForm()

    context = {
        'form': form,
    }
    return render(request, 'inventario/asignar_ropa.html', context)

def gestionar_ropa_sucia(request):
    if request.method == 'POST':
        form = ClothingCleaningForm(request.POST)
        if form.is_valid():
            transaction_type = form.cleaned_data['transaction_type']
            cantidad = form.cleaned_data['cantidad']
            ropa_sucia = form.cleaned_data['nombre']  # Este debe ser un objeto ClothingDirt
            lavanderia = form.cleaned_data['lavanderia']  # Correcto

            if transaction_type == 'ingreso':
                # Lógica para ingreso
                if ropa_sucia.cantidad >= cantidad:  # Verificar que haya suficiente ropa sucia
                    ropa_sucia.cantidad -= cantidad  # Restar de ClothingDirt
                    ropa_sucia.save()

                    # Crear o actualizar ClothingCleanings
                    cleaning, created = ClothingCleanings.objects.get_or_create(
                        tipo_ropa=ropa_sucia.tipo_ropa,  # Asegúrate de que esto sea un objeto Clothing
                        lavanderia=lavanderia,  # Guardar la lavandería seleccionada
                        defaults={'cantidad': 0}
                    )
                    cleaning.cantidad += cantidad  # Sumar a ClothingCleanings
                    cleaning.save()

                    messages.success(request, "Ingreso de ropa sucia registrado exitosamente.")
                else:
                    messages.error(request, "No hay suficiente ropa sucia para realizar el ingreso.")
                    
            elif transaction_type == 'egreso':
                # Lógica para egreso
                cleaning = ClothingCleanings.objects.filter(tipo_ropa=ropa_sucia.tipo_ropa, lavanderia=lavanderia).first()
                if cleaning and cleaning.cantidad >= cantidad:
                    cleaning.cantidad -= cantidad  # Restar de ClothingCleanings
                    cleaning.save()

                    # Actualizar Clothing
                    clothing, created = Clothing.objects.get_or_create(
                        nombre=ropa_sucia.tipo_ropa.nombre,  # Usar el nombre de Clothing
                        defaults={'cantidad': 0}
                    )
                    clothing.cantidad += cantidad  # Sumar a Clothing
                    clothing.save()

                    messages.success(request, "Egreso de ropa limpia registrado exitosamente.")
                else:
                    messages.error(request, "No hay suficiente ropa limpia para realizar el egreso.")
                    
            return redirect('inventario:gestion-ropa-sucia')  # Redirigir a la misma página o a otra
    else:
        form = ClothingCleaningForm()

    context = {
        'form': form,
    }
    return render(request, 'inventario/gestionar_ropa_sucia.html', context)






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
