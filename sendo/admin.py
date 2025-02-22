import os
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from twilio.rest import Client
from django import forms
from .models import ChatSession, Message, Customers, Order, IncomingMessage
from urllib.parse import quote

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


class ReplyForm(forms.Form):
    """Form to send replies in Django Admin."""
    message_body = forms.CharField(widget=forms.Textarea, required=True, label="Reply Message")
    use_whatsapp = forms.BooleanField(required=False, label="Send via WhatsApp")


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
        encoded_session_id = quote(obj.session_id, safe="")  # Encode session_id
        encoded_session_id = encoded_session_id.replace(":", "%3A")  # Encode colon
        return format_html(
    '<a class="button" href="{}">Reply</a>',
    f"/admin/reply/{encoded_session_id}"
)

        return format_html(
        '<a class="button" href="{}">Reply</a>',
        f"/admin/reply/{encoded_session_id}"
    )
    reply_action.short_description = "Reply"

    def get_urls(self):
        """Add a custom URL for handling replies."""
        urls = super().get_urls()
        custom_urls = [
        path("reply/<path:session_id>/", self.admin_site.admin_view(self.reply_view), name="reply_message"),
        ]
        return custom_urls + urls

    def reply_view(self, request, session_id):
        session_id = session_id.replace("%3A", ":")  # Decode colon
        print(f"Decoded session_id: {session_id}")  # Debugging
        session, _ = ChatSession.objects.get_or_create(session_id=session_id)

        if request.method == "POST":
            form = ReplyForm(request.POST)
            if form.is_valid():
                message_body = form.cleaned_data["message_body"]
                use_whatsapp = form.cleaned_data["use_whatsapp"]

                # Send message via Twilio
                client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                from_number = TWILIO_WHATSAPP_NUMBER if use_whatsapp else TWILIO_SMS_NUMBER
                to_number = f"whatsapp:{session_id}" if use_whatsapp else session_id

                try:
                    twilio_msg = client.messages.create(to=to_number, from_=from_number, body=message_body)

                    # Save message in DB
                    Message.objects.create(session=session, sender="agent", body=message_body)

                    messages.success(request, f"Message sent! (ID: {twilio_msg.sid})")
                    return HttpResponseRedirect(request.path)
                except Exception as e:
                    messages.error(request, f"Error sending message: {str(e)}")

        else:
            form = ReplyForm()

        return render(request, "admin/reply_form.html", {"form": form, "session_id": session_id})

# Register models in Django Admin
admin.site.register(ChatSession, ChatSessionAdmin)
admin.site.register(Customers)
admin.site.register(Order)
admin.site.register(Message)
