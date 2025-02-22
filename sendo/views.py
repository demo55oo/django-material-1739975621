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
from django.views.decorators.csrf import csrf_exempt

from .models import Customers, Order  # Ensure these models exist

class CreateCustomerView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            customer = Customers.objects.create(
                name=data['name'],
                phone=data['phone']
            )
            return JsonResponse({'id': customer.id, 'message': 'Customer created successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class CreateOrderView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            customer = Customers.objects.get(id=data['customer_id'])
            order = Order.objects.create(
                pickup=data['pickup'],
                dropoff=data['dropoff'],
                cost=data['cost'],
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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from twilio.rest import Client
from .models import ChatSession, Message
import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

@api_view(["POST"])
def incoming_sms(request):
    from_number = request.data.get("From")
    body = request.data.get("Body")
    session, created = ChatSession.objects.get_or_create(session_id=from_number)

    Message.objects.create(session=session, sender="user", body=body)

    return Response({"message": "Received"})

@api_view(["GET"])
def list_messages(request, session_id):
    messages = Message.objects.filter(session__session_id=session_id).values()
    return Response(messages)

@api_view(["POST"])
def send_message(request):
    to = request.data.get("to")
    body = request.data.get("body")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to=to, from_=TWILIO_PHONE_NUMBER, body=body
    )

    session, _ = ChatSession.objects.get_or_create(session_id=to)
    Message.objects.create(session=session, sender="agent", body=body)

    return Response({"message_id": message.sid})
