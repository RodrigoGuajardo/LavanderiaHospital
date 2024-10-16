from django.db import models

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
class ClothingType(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
class ClothingInventory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
    ]
    CLOTHING_STATUS_CHOICES = [
        ('limpia', 'Limpia'),
        ('sucia', 'Sucia'),
    ]

    service = models.ForeignKey(ClinicalService, on_delete=models.CASCADE, null=True, blank=True)
    laundry = models.ForeignKey(ExternalLaundry, on_delete=models.CASCADE, null=True, blank=True)
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    clothing_status = models.CharField(max_length=6, choices=CLOTHING_STATUS_CHOICES)
    cantidad = models.IntegerField()
    fecha_transaccion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad} - {self.clothing_type.nombre} ({self.transaction_type})"
