from django.db import models

class Customers(models.Model):
    # __Customers_FIELDS__
    name = models.CharField(max_length=255, null=True, blank=True)  # Changed to CharField
    phone = models.CharField(max_length=15, null=True, blank=True)  # Changed to CharField

    # __Customers_FIELDS__END

    class Meta:
        verbose_name = "Customer"  # Singular
        verbose_name_plural = "Customers"  # Plural

    def __str__(self):
        return self.name or "Unnamed Customer"  # Display name or fallback


class Order(models.Model):
    # __Order_FIELDS__
    pickup = models.CharField(max_length=255, null=True, blank=True)  # Changed to CharField
    dropoff = models.CharField(max_length=255, null=True, blank=True)  # Fixed typo
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # ✅ Allows decimals
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)

    # __Order_FIELDS__END

    class Meta:
        verbose_name = "Order"  # Singular
        verbose_name_plural = "Orders"  # Plural

    def __str__(self):
        return f"Order for {self.customer.name}"  # Display order reference

class IncomingMessage(models.Model):
    from_number = models.CharField(max_length=15)
    to_number = models.CharField(max_length=15)
    message_body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.from_number} to {self.to_number} at {self.timestamp}"
    
from django.db import models

class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50)  # "user" or "agent"
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
