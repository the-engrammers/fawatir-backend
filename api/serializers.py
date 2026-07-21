from rest_framework import serializers
from . import models

class CompanySerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Company, '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Role, '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.User, '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Permission, '__all__'

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.RolePermission, '__all__'

class CompanySettingSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.CompanySetting, '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.AuditLog, '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Client, '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Supplier, '__all__'

class MarketingCampaignSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.MarketingCampaign, '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Category, '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Product, '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.ProductVariant, '__all__'

class InventorySerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Inventory, '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.StockMovement, '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Invoice, '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.InvoiceItem, '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Payment, '__all__'

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.BankAccount, '__all__'

class QuotationSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Quotation, '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.PurchaseOrder, '__all__'

class PosSessionSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.PosSession, '__all__'

class PosSaleSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.PosSale, '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Department, '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Employee, '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Payroll, '__all__'

class AiConversationSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.AiConversation, '__all__'

class OcrDocumentSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.OcrDocument, '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta: model, fields = models.Ticket, '__all__'