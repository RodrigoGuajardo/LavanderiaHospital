from django.shortcuts import render, redirect
from .models import *

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
        return redirect('inventario:registro_exitoso')

    services = ClinicalService.objects.all()
    laundries = ExternalLaundry.objects.all()
    clothing_types = ClothingType.objects.all()

    context = {
        'services': services,
        'laundries': laundries,
        'clothing_types': clothing_types
    }
    return render(request, 'inventario/registro.html', context)


def home(request):
    return render(request, 'inventario/index.html')
def registro(request):
    return render(request,'inventario/registro.html')