from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ClinicalService)
admin.site.register(ClothingType)
admin.site.register(ExternalLaundry)
admin.site.register(ClothingInventory)
admin.site.register(Clothing)
admin.site.register(ClothingDirt)
admin.site.register(ClothingCleaning)
admin.site.register(ClothingCleanings)
admin.site.register(ClothingServices)