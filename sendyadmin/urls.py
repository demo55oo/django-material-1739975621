"""
URL configuration for sendyadmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sendo.views import incoming_message , CreateCustomerView, CreateOrderView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/incoming-message/', incoming_message, name='incoming_message'),
    path('api/customers/', CreateCustomerView.as_view(), name='create_customer'),  # Use as_view() here
    path('api/orders/', CreateOrderView.as_view(), name='create_order'), 
]
