from django.contrib import admin
import os
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib import messages as django_messages
from twilio.rest import Client
from django import forms
from .models import ChatSession, Message
from .models import Customers, Order,IncomingMessage ,Message, ChatSession # Import your models

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER")


class MessageInline(admin.TabularInline):
    """Show messages inside ChatSession Admin."""
    model = Message
    extra = 0
    readonly_fields = ("sender", "body", "timestamp")


class ChatSessionAdmin(admin.ModelAdmin):
    """Admin panel for managing chat sessions."""
    list_display = ("session_id", "latest_message", "reply_action")
    search_fields = ("session_id",)
    inlines = [MessageInline]

    def latest_message(self, obj):
        """Show the latest user message."""
        last_msg = obj.message_set.filter(sender="user").order_by("-timestamp").first()
        return last_msg.body if last_msg else "No messages"

    latest_message.short_description = "Last Message"

    def reply_action(self, obj):
        """Button to open the reply page."""
        return format_html(
            '<a class="button" href="{}">Reply</a>',
            f"/admin/reply/{obj.session_id}"
        )

    reply_action.short_description = "Reply"
    reply_action.allow_tags = True

    def get_urls(self):
        """Add a custom URL for handling replies."""
        urls = super().get_urls()
        custom_urls = [
            path("reply/<str:session_id>/", self.admin_site.admin_view(self.reply_view), name="reply_message"),
        ]
        return custom_urls + urls

    def reply_view(self, request, session_id):
        """Admin panel form to send replies."""
        if request.method == "POST":
            message_body = request.POST.get("message_body")
            use_whatsapp = request.POST.get("use_whatsapp") == "on"

            # Send message via Twilio
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            from_number = TWILIO_WHATSAPP_NUMBER if use_whatsapp else TWILIO_SMS_NUMBER
            to_number = f"whatsapp:{session_id}" if use_whatsapp else session_id

            try:
                twilio_msg = client.messages.create(to=to_number, from_=from_number, body=message_body)

                # Save message in DB
                session, _ = ChatSession.objects.get_or_create(session_id=session_id)
                Message.objects.create(session=session, sender="agent", body=message_body)

                django_messages.success(request, f"Message sent! (ID: {twilio_msg.sid})")
            except Exception as e:
                django_messages.error(request, f"Error sending message: {str(e)}")

            return HttpResponseRedirect(request.path)

        return self.render_reply_form(request, session_id)

    def render_reply_form(self, request, session_id):
        """Render a simple HTML form inside Django Admin."""
        return HttpResponseRedirect(f"/admin/reply/{session_id}")


# Register the models in Django Admin
admin.site.register(ChatSession, ChatSessionAdmin)

# Register your models here.

admin.site.register(Customers)
admin.site.register(Order)
admin.site.register(Message)
