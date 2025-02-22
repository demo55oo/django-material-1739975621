from django.contrib import admin

# Register your models here.
from .models import Customers, Order,IncomingMessage ,Message, ChatSession # Import your models

admin.site.register(Customers)
admin.site.register(Order)
admin.site.register(IncomingMessage)
admin.site.register(Message)
admin.site.register(ChatSession)