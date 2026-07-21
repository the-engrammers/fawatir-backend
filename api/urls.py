from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'permissions', views.PermissionViewSet)
router.register(r'role-permissions', views.RolePermissionViewSet)
router.register(r'company-settings', views.CompanySettingViewSet)
router.register(r'audit-logs', views.AuditLogViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'marketing-campaigns', views.MarketingCampaignViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'product-variants', views.ProductVariantViewSet)
router.register(r'inventory', views.InventoryViewSet)
router.register(r'stock-movements', views.StockMovementViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'invoice-items', views.InvoiceItemViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'bank-accounts', views.BankAccountViewSet)
router.register(r'quotations', views.QuotationViewSet)
router.register(r'purchase-orders', views.PurchaseOrderViewSet)
router.register(r'pos-sessions', views.PosSessionViewSet)
router.register(r'pos-sales', views.PosSaleViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'payrolls', views.PayrollViewSet)
router.register(r'ai-conversations', views.AiConversationViewSet)
router.register(r'ocr-documents', views.OcrDocumentViewSet)
router.register(r'tickets', views.TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]