import uuid
from django.db import models

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    legal_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=30, null=True, blank=True)
    tax_identifier = models.CharField(max_length=100, null=True, blank=True)
    ice = models.CharField(max_length=100, null=True, blank=True)
    rc = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clients')
    customer_code = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    ice = models.CharField(max_length=100, null=True, blank=True)
    rc = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, default='Active')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name