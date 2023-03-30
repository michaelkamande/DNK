from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from django.views.i18n import JavaScriptCatalog

from administration import views as admin_views
from users import views as users_views

urlpatterns = [
    
    path('', admin_views.dashboard, name='dashboard'),

    path('login/', users_views.userLogin, name="login"),
    path('logout/', users_views.userLogout, name="logout"),
    path('register/', users_views.userRegister, name="register"),
    path('profile/', users_views.userProfile, name="profile"),
    path('users/', admin_views.users, name="users"),

    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catalog'),

    path('unpaidrent/', admin_views.unpaidrent, name='unpaidrent'),

    path('appartments/', admin_views.appartments, name='appartments'),
    path('appartments_available/', admin_views.appartments_available, name='appartments_available'),
    path('appartments_taken/', admin_views.appartments_taken, name='appartments_taken'),
    path('appartment_add/', admin_views.appartment_add, name='appartment_add'),
    path('appartment_view/<int:pk>/', admin_views.appartment_view, name='appartment_view'),
    path('appartment_edit/<int:pk>/', admin_views.appartment_edit, name='appartment_edit'),
    path('appartment_delete/<int:pk>/', admin_views.appartment_delete, name='appartment_delete'),

    path('tenants/', admin_views.tenants, name='tenants'),
    path('tenant_add/', admin_views.tenant_add, name='tenant_add'),
    path('tenant_view/<int:pk>/', admin_views.tenant_view, name='tenant_view'),
    path('tenant_edit/<int:pk>/', admin_views.tenant_edit, name='tenant_edit'),
    path('tenant_delete/<int:pk>/', admin_views.tenant_delete, name='tenant_delete'),

    path('rentalcontracts/', admin_views.rentalcontracts, name='rentalcontracts'),
    path('rentalcontracts_on/', admin_views.rentalcontracts_on, name='rentalcontracts_on'),
    path('rentalcontracts_off/', admin_views.rentalcontracts_off, name='rentalcontracts_off'),
    path('rentalcontracts_off_soon/', admin_views.rentalcontracts_off_soon, name='rentalcontracts_off_soon'),
    path('rentalcontract_add/', admin_views.rentalcontract_add, name='rentalcontract_add'),
    path('rentalcontract_view/<int:pk>/', admin_views.rentalcontract_view, name='rentalcontract_view'),
    path('rentalcontract_edit/<int:pk>/', admin_views.rentalcontract_edit, name='rentalcontract_edit'),
    path('rentalcontract_resiliate/<int:pk>/', admin_views.rentalcontract_resiliate, name='rentalcontract_resiliate'),
    path('rentalcontract_delete/<int:pk>/', admin_views.rentalcontract_delete, name='rentalcontract_delete'),

    path('payrent/', admin_views.PayRent.as_view(), name='payrent'),
    path('rentpaid_view/<int:pk>/', admin_views.rentpaid_view, name='rentpaid_view'),
    path('rentpaid_edit/<int:pk>/', admin_views.rentpaid_edit, name='rentpaid_edit'),
    path('rent_success/', admin_views.rent_success, name='rent_success'),

    path('invoicerent/', admin_views.GenerateInvoiceRent.as_view(), name='invoicerent'),
    path('invoicerentold/<int:pk>/', admin_views.GenerateInvoiceRentOld.as_view(), name='invoicerentold'),

    path('report_apparts/', admin_views.report_apparts, name='report_apparts'),

    path('accounting/', admin_views.accounting, name='accounting'),
    path('results/', admin_views.results, name="results"),

    path('expenses/', admin_views.expenses, name="expenses"),
    path('expense_add/', admin_views.expense_add, name = 'expense_add'),
    path('expense_edit/<int:pk>/', admin_views.expense_edit, name="expense_edit"),
    path('expense_delete/<int:pk>/', admin_views.expense_delete, name = 'expense_delete'),

    path('income/', admin_views.income, name="income"),
    path('income_add/', admin_views.income_add, name = 'income_add'),
    path('income_edit/<int:pk>/', admin_views.income_edit, name="income_edit"),
    path('income_delete/<int:pk>/', admin_views.income_delete, name = 'income_delete'),

    path('partners/', admin_views.partners, name="partners"),
    path('partner_add/', admin_views.partner_add, name = 'partner_add'),
    path('partner_view/<int:pk>/', admin_views.partner_view, name="partner_view"),
    path('partner_edit/<int:pk>/', admin_views.partner_edit, name="partner_edit"),
    path('partner_delete/<int:pk>/', admin_views.partner_delete, name = 'partner_delete'),

    path('positions/', admin_views.positions, name="positions"),
    path('position_add/', admin_views.position_add, name = 'position_add'),
    path('position_view/<int:pk>/', admin_views.position_view, name="position_view"),
    path('position_edit/<int:pk>/', admin_views.position_edit, name="position_edit"),
    path('position_delete/<int:pk>/', admin_views.position_delete, name = 'position_delete'),

    path('employees/', admin_views.employees, name="employees"),
    path('employee_add/', admin_views.employee_add, name = 'employee_add'),
    path('employee_view/<int:pk>/', admin_views.employee_view, name="employee_view"),
    path('employee_edit/<int:pk>/', admin_views.employee_edit, name="employee_edit"),
    path('employee_delete/<int:pk>/', admin_views.employee_delete, name = 'employee_delete'),

    path('workcontracts/', admin_views.workcontracts, name="workcontracts"),
    path('workcontracts_on/', admin_views.workcontracts_on, name='workcontracts_on'),
    path('workcontracts_off/', admin_views.workcontracts_off, name='workcontracts_off'),
    path('workcontracts_off_soon/', admin_views.workcontracts_off_soon, name='workcontracts_off_soon'),
    path('workcontract_add/', admin_views.workcontract_add, name = 'workcontract_add'),
    path('workcontract_edit/<int:pk>/', admin_views.workcontract_edit, name="workcontract_edit"),
    path('workcontract_view/<int:pk>/', admin_views.workcontract_view, name="workcontract_view"),
    path('workcontract_resiliate/<int:pk>/', admin_views.workcontract_resiliate, name='workcontract_resiliate'),
    path('workcontract_delete/<int:pk>/', admin_views.workcontract_delete, name = 'workcontract_delete'),

    path('salaries/', admin_views.salaries, name="salaries"),
    path('salary_add/', admin_views.salary_add, name = 'salary_add'),
    path('salary_edit/<int:pk>/', admin_views.salary_edit, name="salary_edit"),
    path('salary_delete/<int:pk>/', admin_views.salary_delete, name = 'salary_delete'),

    path('bankaccounts/', admin_views.bankaccounts, name="bankaccounts"),
    path('bankaccount_add/', admin_views.bankaccount_add, name = 'bankaccount_add'),
    path('bankaccount_view/<int:pk>/', admin_views.bankaccount_view, name="bankaccount_view"),
    path('bankaccount_edit/<int:pk>/', admin_views.bankaccount_edit, name="bankaccount_edit"),
    path('bankaccount_close/<int:pk>/', admin_views.bankaccount_close, name='bankaccount_close'),
    path('bankaccount_delete/<int:pk>/', admin_views.bankaccount_delete, name = 'bankaccount_delete'),

    path('transfers/', admin_views.transfers, name="transfers"),
    path('transfer_add/', admin_views.transfer_add, name = 'transfer_add'),
    path('transfer_delete/<int:pk>/', admin_views.transfer_delete, name = 'transfer_delete'),

    path('enterprise/', admin_views.enterprise, name="enterprise"),
    path('enterprise_mod/<int:id>/', admin_views.enterprise_mod, name="enterprise_mod"),

    path('__kits_admin__/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
