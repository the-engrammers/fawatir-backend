from rest_framework import viewsets
from . import models, serializers
# foundation
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
class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.UserPreference.objects.all(), serializers.UserPreferenceSerializer

class UserSessionViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.UserSession.objects.all(), serializers.UserSessionSerializer

class PasswordResetViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PasswordReset.objects.all(), serializers.PasswordResetSerializer

class EmailVerificationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.EmailVerification.objects.all(), serializers.EmailVerificationSerializer

class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.ActivityLog.objects.all(), serializers.ActivityLogSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Notification.objects.all(), serializers.NotificationSerializer

class PdfTemplateViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PdfTemplate.objects.all(), serializers.PdfTemplateSerializer

# CRM
class ClientViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Client.objects.all(), serializers.ClientSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Supplier.objects.all(), serializers.SupplierSerializer

class MarketingCampaignViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.MarketingCampaign.objects.all(), serializers.MarketingCampaignSerializer
class ClientContactViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.ClientContact.objects.all(), serializers.ClientContactSerializer

class CustomerAddressViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.CustomerAddress.objects.all(), serializers.CustomerAddressSerializer

class CustomerPortalViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.CustomerPortal.objects.all(), serializers.CustomerPortalSerializer

class SupplierContactViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.SupplierContact.objects.all(), serializers.SupplierContactSerializer

class SupplierAddressViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.SupplierAddress.objects.all(), serializers.SupplierAddressSerializer

class WhatsappMessageViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.WhatsappMessage.objects.all(), serializers.WhatsappMessageSerializer

class MarketingAdViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.MarketingAd.objects.all(), serializers.MarketingAdSerializer

class MarketingMetricViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.MarketingMetric.objects.all(), serializers.MarketingMetricSerializer

# Inventory
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
class SupplierProductViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.SupplierProduct.objects.all(), serializers.SupplierProductSerializer

# Accounting 
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Invoice.objects.all(), serializers.InvoiceSerializer

class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.InvoiceItem.objects.all(), serializers.InvoiceItemSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Payment.objects.all(), serializers.PaymentSerializer

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.BankAccount.objects.all(), serializers.BankAccountSerializer
class RecurringInvoiceViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.RecurringInvoice.objects.all(), serializers.RecurringInvoiceSerializer

class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.BankTransaction.objects.all(), serializers.BankTransactionSerializer

class BankReconciliationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.BankReconciliation.objects.all(), serializers.BankReconciliationSerializer

#Quotation
class QuotationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Quotation.objects.all(), serializers.QuotationSerializer
class QuotationItemViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.QuotationItem.objects.all(), serializers.QuotationItemSerializer

# Purchase Orders
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PurchaseOrder.objects.all(), serializers.PurchaseOrderSerializer
class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PurchaseOrderItem.objects.all(), serializers.PurchaseOrderItemSerializer

#Pos
class PosSessionViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PosSession.objects.all(), serializers.PosSessionSerializer

class PosSaleViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PosSale.objects.all(), serializers.PosSaleSerializer
class PosSaleItemViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PosSaleItem.objects.all(), serializers.PosSaleItemSerializer

#HR
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Department.objects.all(), serializers.DepartmentSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Employee.objects.all(), serializers.EmployeeSerializer

class PayrollViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Payroll.objects.all(), serializers.PayrollSerializer
class PayrollItemViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.PayrollItem.objects.all(), serializers.PayrollItemSerializer

#AI 
class AiConversationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiConversation.objects.all(), serializers.AiConversationSerializer

class OcrDocumentViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.OcrDocument.objects.all(), serializers.OcrDocumentSerializer
class AiMessageViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiMessage.objects.all(), serializers.AiMessageSerializer

class AiTaskViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiTask.objects.all(), serializers.AiTaskSerializer

class AiRecommendationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiRecommendation.objects.all(), serializers.AiRecommendationSerializer

class AiAutomationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiAutomation.objects.all(), serializers.AiAutomationSerializer

class AiNotificationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiNotification.objects.all(), serializers.AiNotificationSerializer

class AiAdGenerationViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.AiAdGeneration.objects.all(), serializers.AiAdGenerationSerializer

# Support
class TicketViewSet(viewsets.ModelViewSet):
    queryset, serializer_class = models.Ticket.objects.all(), serializers.TicketSerializer