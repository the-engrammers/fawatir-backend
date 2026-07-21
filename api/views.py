from rest_framework import viewsets
from . import models, serializers

class CompanyViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Company.objects.all(), serializers.CompanySerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Role.objects.all(), serializers.RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.User.objects.all(), serializers.UserSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Permission.objects.all(), serializers.PermissionSerializer

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.RolePermission.objects.all(), serializers.RolePermissionSerializer

class CompanySettingViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.CompanySetting.objects.all(), serializers.CompanySettingSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AuditLog.objects.all(), serializers.AuditLogSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Client.objects.all(), serializers.ClientSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Supplier.objects.all(), serializers.SupplierSerializer

class MarketingCampaignViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.MarketingCampaign.objects.all(), serializers.MarketingCampaignSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Category.objects.all(), serializers.CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Product.objects.all(), serializers.ProductSerializer

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.ProductVariant.objects.all(), serializers.ProductVariantSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Inventory.objects.all(), serializers.InventorySerializer

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.StockMovement.objects.all(), serializers.StockMovementSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Invoice.objects.all(), serializers.InvoiceSerializer

class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.InvoiceItem.objects.all(), serializers.InvoiceItemSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Payment.objects.all(), serializers.PaymentSerializer

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.BankAccount.objects.all(), serializers.BankAccountSerializer

class QuotationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Quotation.objects.all(), serializers.QuotationSerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PurchaseOrder.objects.all(), serializers.PurchaseOrderSerializer

class PosSessionViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PosSession.objects.all(), serializers.PosSessionSerializer

class PosSaleViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PosSale.objects.all(), serializers.PosSaleSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Department.objects.all(), serializers.DepartmentSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Employee.objects.all(), serializers.EmployeeSerializer

class PayrollViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Payroll.objects.all(), serializers.PayrollSerializer

class AiConversationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiConversation.objects.all(), serializers.AiConversationSerializer

class OcrDocumentViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.OcrDocument.objects.all(), serializers.OcrDocumentSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Ticket.objects.all(), serializers.TicketSerializer