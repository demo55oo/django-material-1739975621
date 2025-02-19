from django.contrib import admin

# Register your models here.
from .models import Customers, Order,IncomingMessage  # Import your models

admin.site.register(Customers)
admin.site.register(Order)
admin.site.register(IncomingMessage)
