from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.db.models import F
from django.db.models import Sum

def generar_reportes(request):
    # Obtener la cantidad de ropa limpia
    total_ropa_limpia = Clothing.objects.aggregate(total=Sum('cantidad'))['total'] or 0

    # Obtener la cantidad de ropa sucia
    total_ropa_sucia = ClothingDirt.objects.aggregate(total=Sum('cantidad'))['total'] or 0

    # Obtener la cantidad de ropa en proceso de lavado
    total_ropa_en_lavado = ClothingCleanings.objects.aggregate(total=Sum('cantidad'))['total'] or 0

    # Obtener la cantidad de ropa asignada a diferentes áreas
    total_ropa_asignada = ClothingServices.objects.aggregate(total=Sum('cantidad'))['total'] or 0

    # Crear un diccionario con los datos del reporte
    reporte = {
        'total_ropa_limpia': total_ropa_limpia,
        'total_ropa_sucia': total_ropa_sucia,
        'total_ropa_en_lavado': total_ropa_en_lavado,
        'total_ropa_asignada': total_ropa_asignada,
    }

    # Obtener datos adicionales para las tablas
    all_clothing = Clothing.objects.all()  # Obtener todos los tipos de ropa
    all_cleanings = ClothingCleanings.objects.all()  # Obtener todos los registros de limpieza
    all_dirt = ClothingDirt.objects.all()  # Obtener todos los registros de ropa sucia
    all_services = ClothingServices.objects.all()  # Obtener todos los registros de ropa asignada

    return render(request, 'inventario/reportes.html', {
        'reporte': reporte,
        'all_clothing': all_clothing,
        'all_cleanings': all_cleanings,
        'all_dirt': all_dirt,
        'all_services': all_services,
    })

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

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:login')  # Redirige a la página de login o donde desees
    else:
        form = UserRegistrationForm()
    return render(request, 'inventario/registro.html', {'form': form})




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

                    # Actualizar ClothingServices
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
                clothing_services = ClothingServices.objects.filter(tipo_ropa=tipo_ropa, servicio=servicio).first()
                if clothing_services and clothing_services.cantidad >= cantidad:
                    clothing_services.cantidad -= cantidad  # Aquí clothing_services debe ser un objeto, no un int
                    clothing_services.save()


                    # Guardar en ClothingDirt
                    clothing_dirt, created = ClothingDirt.objects.get_or_create(
                        nombre=tipo_ropa.nombre,
                        tipo_ropa=tipo_ropa,  # Asegúrate de establecer el tipo de ropa
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
                    ClothingCleaning, created = ClothingCleanings.objects.get_or_create(
                        tipo_ropa=ropa_sucia.tipo_ropa,  # Asegúrate de que esto sea un objeto Clothing
                        lavanderia=lavanderia,  # Guardar la lavandería seleccionada
                        defaults={'cantidad': 0}
                    )
                    ClothingCleaning.cantidad += cantidad  # Sumar a ClothingCleanings
                    ClothingCleaning.save()  # Asegúrate de guardar el objeto

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
                    
            return redirect('inventario:gestionar_ropa_sucia')  # Redirigir a la misma página o a otra
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
