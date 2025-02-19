from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import IncomingMessage

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Customers, Order
import json

class CreateCustomerView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            customer = Customers.objects.create(
                name=data.get('name'),
                phone=data.get('phone')
            )
            return JsonResponse({'id': customer.id, 'message': 'Customer created successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class CreateOrderView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            customer = Customers.objects.get(id=data['customer_id'])
            order = Order.objects.create(
                pickup=data.get('pickup'),
                dropoff=data.get('dropoff'),
                cost=data.get('cost'),
                customer=customer
            )
            return JsonResponse({'id': order.id, 'message': 'Order created successfully!'}, status=201)
        except Customers.DoesNotExist:
            return JsonResponse({'error': 'Customer not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt  # Disable CSRF for this view
def incoming_message(request):
    if request.method == 'POST':
        from_number = request.POST.get('From')
        to_number = request.POST.get('To')
        message_body = request.POST.get('Body')
        
        # Save the incoming message to the database
        IncomingMessage.objects.create(
            from_number=from_number,
            to_number=to_number,
            message_body=message_body
        )
        
        return HttpResponse(status=200)  # Respond with a 200 OK status
    return HttpResponse(status=400)  # Respond with a 400 Bad Request status


