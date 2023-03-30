from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, View, DeleteView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum
from django.views.decorators.cache import cache_page

from datetime import datetime, timedelta, time, date

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

import io
import os

from .models import *
from .forms import *
from .utils import *
from .decorators import allowed_users

from users.models import Profile


app_name = "iEnterprise"
version = "1.0.0"
warning_days = 15
trial_days = 7
alert_days = 35
caching_minutes = 15
deposit = 3
impf = 150
irl = 22
ipr = 15


#==================================================================================================================================================
#   APPARTEMENTS   #
#==================================================================================================================================================

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def dashboard(request):
	today = datetime.now().date()
	#warning = False
	#if request.exp is None:
	#	request.exp = today + timedelta(days=trial_days) 
	#warning_period = request.exp - timedelta(days=warning_days)

	#if today > warning_period and today < request.exp:
	#	warning = True

	#exp = request.exp
	#exp = exp.strftime('%d/%m/%Y')

	#if request.exp > today:
	rentpaid_sample = RentPayment.objects.all().order_by('-id')[:6]
	rentpaid_total = RentPayment.objects.aggregate(Sum('paid_amount')).get('paid_amount__sum')
	rentunpaid_count = RentalContract.objects.filter(next_payment_on__lte=today, isTerminated=False).count()
	total_income = Income.objects.aggregate(Sum('amount')).get('amount__sum')
	tenants_number = Tenant.objects.all().count()
	total_expenses = Disbursement.objects.aggregate(Sum('amount')).get('amount__sum')
	total_salaries = Salary.objects.aggregate(Sum('amount')).get('amount__sum')

	if rentunpaid_count is None:
		rentunpaid_count = 0

	if total_expenses is None:
		total_expenses = 0
	if total_salaries is None:
		total_salaries = 0
	expenses = total_expenses + total_salaries

	income = total_income
	if income is None:
		income = 0

	appartments_income = rentpaid_total
	if appartments_income is None:
		appartments_income = 0
		
	unpaid_invoices = rentunpaid_count + 0 + 0
	balance = (income + appartments_income) - expenses
	clients = tenants_number
	global_income = income + appartments_income
	

	income_percent = 0
	appartments_income_percent = 0
	balance_percent = 0
	expenses_percent = 0

	if global_income > 0:
		income_percent = (income * 100)/global_income
		appartments_income_percent = (appartments_income * 100)/global_income
		balance_percent = (balance * 100)/global_income
		expenses_percent = (expenses * 100)/global_income

	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	current_month = today.month
	current_year = today.year

	if current_month == 1:
		current_month_name = "Janvier"
	elif current_month == 2:
		current_month_name = "Février"
	elif current_month == 3:
		current_month_name = "Mars"
	elif current_month == 4:
		current_month_name = "Avril"
	elif current_month == 5:
		current_month_name = "Mai"
	elif current_month == 6:
		current_month_name = "Juin"
	elif current_month == 7:
		current_month_name = "Juillet"
	elif current_month == 8:
		current_month_name = "Aout"
	elif current_month == 9:
		current_month_name = "Septembre"
	elif current_month == 10:
		current_month_name = "Octobre"
	elif current_month == 11:
		current_month_name = "Novembre"
	elif current_month == 12:
		current_month_name = "Decembre"

	context = {
		'income': income,
		'appartments_income': appartments_income,
		'expenses': expenses,
		'balance': balance,
		'clients': clients,
		'unpaid_invoices': unpaid_invoices,
		'rentpaid_sample': rentpaid_sample,
		'income_percent': str(income_percent),
		'appartments_income_percent': str(appartments_income_percent),
		'balance_percent': str(balance_percent),
		'expenses_percent': str(expenses_percent),
		'global_income': global_income,
		'ent': ent,
		#'warning': warning,
		#'exp': exp,
		'current_month': current_month_name,
		'current_year': str(current_year),
		#'version': imart_version
	}

	return render(request, "dashboard.html", context)
	#else:
	#	return render(request, "exp.html")


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def unpaidrent(request):
	today = datetime.now().date()
	items = RentalContract.objects.filter(end_date__gt=today, next_payment_on__lt=(today+timedelta(days=1))).order_by('tenant')
	
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	context = {
		'items': items,
		'today': today,
		'ent': ent
	}
	return render(request, "unpaidrent.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def appartments(request):
	items = Appartment.objects.all().order_by('designation')
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	context = {
		'items': items,
		'ent': ent
	}
	return render(request, "appartments.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def appartments_available(request):
	items = Appartment.objects.filter(isAvailable=True).order_by('designation')
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	context = {
		'items': items,
		'ent': ent
	}
	return render(request, "appartments_available.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def appartments_taken(request):
	items = Appartment.objects.filter(isAvailable=False).order_by('designation')
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	context = {
		'items': items,
		'ent': ent
	}
	return render(request, "appartments_taken.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def appartment_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = AppartmentForm(request.POST)
		if form.is_valid():
			form.save()
			appartment = form.cleaned_data.get('designation')
			messages.success(request, f'"{appartment}" créé avec succès!')
			return redirect('appartments')		
	else:
		form = AppartmentForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'appartment_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def appartment_view(request, pk):
	item = get_object_or_404(Appartment, pk=pk)
	contracts = RentalContract.objects.filter(appartment=item)
	current_contract = RentalContract.objects.filter(appartment__exact=item).order_by('-id')[:1]
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	context = {
	'item': item,
	'current_contract': current_contract,
	'contracts': contracts,
	'ent': ent
	}
	return render(request, 'appartment.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def appartment_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Appartment, pk=pk)
	if request.method == 'POST':
		form = AppartmentForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			appartment = form.cleaned_data.get('designation')
			messages.success(request, f'"{appartment}" créé avec succès!')
			return redirect('appartments')
	else:
		form = AppartmentForm(instance = item)
		context = {
			'form': form,
			'ent': ent,
		}
		return render(request, 'appartment_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def appartment_delete(request, pk):
	item = get_object_or_404(Appartment, pk=pk)
	item.delete()
	messages.info(request, "Appartement supprimée !")
	return redirect('appartments')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def tenants(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Tenant.objects.all().order_by('firstname')
	searched = None
	lookup1 = None
	lookup2 = None
	lookup3 = None
	lookup4 = None
	lookup5 = None
	lookup6 = None
	if request.method == 'POST':
		searched = request.POST.get('search')
		lookup1 = Tenant.objects.filter(firstname__icontains = searched).order_by('firstname')
		lookup2 = Tenant.objects.filter(lastname__icontains = searched).order_by('firstname')
		lookup3 = Tenant.objects.filter(email__icontains = searched).order_by('firstname')
		lookup4 = Tenant.objects.filter(phone__icontains = searched).order_by('firstname')
		lookup5 = Tenant.objects.filter(occupation__icontains = searched).order_by('firstname')
		lookup6 = Tenant.objects.filter(company__icontains = searched).order_by('firstname')	
		context = {
			'lookup1': lookup1,
			'lookup2': lookup2,
			'lookup3': lookup3,
			'lookup4': lookup4,
			'lookup5': lookup5,
			'lookup6': lookup6,
			'ent': ent,
		}
	else:
		context = {
			'items': items,
			'ent': ent,
		}
	return render(request, "tenants.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def tenant_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = TenantForm(request.POST)
		if form.is_valid():
			form.save()
			tenant = form.cleaned_data.get('firstname')
			messages.success(request, f'"{tenant}" créé avec succès!')
			return redirect('tenants')	
	else:
		form = TenantForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'tenant_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def tenant_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Tenant, pk=pk)
	contract = RentalContract.objects.filter(tenant=item).last()
	contracts = RentalContract.objects.filter(tenant=item).order_by('-id')
	payments = RentPayment.objects.filter(tenant=item).order_by('-id')

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'contract': contract,
	'contracts': contracts,
	'payments': payments,
	'today': today,
	'alert_period': alert_period,
	'ent': ent,
	}
	return render(request, 'tenant.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def tenant_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Tenant, pk=pk)
	
	if request.method == 'POST':
		form = TenantForm(request.POST, instance = item)
		card_form = TenantIdForm(request.POST, request.FILES, instance = item)
		if form.is_valid() and card_form.is_valid():
			form.save()
			card_form.save()
			tenant = form.cleaned_data.get('firstname')
			messages.success(request, f'"{tenant}" créé avec succès!')
			return redirect('tenant_view', item.pk)

	else:
		form = TenantForm(instance = item)
		card_form = TenantIdForm(instance = item)

		context = {
			'form': form,
			'card_form': card_form,
			'ent': ent,
		}

		return render(request, 'tenant_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def tenant_delete(request, pk):
	item = get_object_or_404(Tenant, pk=pk)
	item.delete()
	messages.info(request, "Locataire supprimée !")
	return redirect('tenants')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontracts(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = RentalContract.objects.all().order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "rentalcontracts.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontracts_on(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = RentalContract.objects.filter(end_date__gt=today).order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "rentalcontracts_on.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontracts_off(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = RentalContract.objects.filter(end_date__lt=today).order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent
	}
	return render(request, "rentalcontracts_off.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontracts_off_soon(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = RentalContract.objects.all().order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "rentalcontracts_off_soon.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontract_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = RentalContractForm(request.POST)
		if form.is_valid():
			contract = RentalContract.objects.create(
				created_by = request.user,
				tenant = form.cleaned_data.get('locataire'),
				appartment = form.cleaned_data.get('appartement'),
				#rent = form.cleaned_data.get('loyer'),
				#deposit = form.cleaned_data.get('garantie_locative'),
				start_date = form.cleaned_data.get('date_début'),
				end_date = form.cleaned_data.get('date_fin'),
				next_payment_on = form.cleaned_data.get('prochain_paiement'),
				)

			if contract.tenant.category == 'A':
				contract.rent = contract.appartment.rent_A
				contract.deposit = contract.rent * deposit
			elif contract.tenant.category == 'B':
				contract.rent = contract.appartment.rent_B
				contract.deposit = contract.rent * deposit
			elif contract.tenant.category == 'C':
				contract.rent = contract.appartment.rent_C
				contract.deposit = contract.rent * deposit
			else:
				contract.rent = contract.appartment.rent
				contract.deposit = contract.rent * deposit
			contract.save()

			appartment = Appartment.objects.get(designation=form.cleaned_data.get('appartement'))
			appartment.isAvailable = False
			appartment.save()

			tenant = Tenant.objects.get(id=contract.tenant.id)
			tenant.isActive = True
			tenant.isTerminated = False
			tenant.save()

			messages.success(request, f'Contrat créé avec succès!')
			return redirect('rentalcontracts')
			
	else:
		form = RentalContractForm()

	
	context = {
			'form': form,
			'ent': ent
		}
	return render(request, 'rentalcontract_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontract_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(RentalContract, pk=pk)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'today': today,
	'alert_period': alert_period,
	'ent': ent
	}
	return render(request, 'rentalcontract.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontract_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(RentalContract, pk=pk)
	
	if request.method == 'POST':
		form = RentalContractEditForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			messages.success(request, f'Contrat créé avec succès!')
			return redirect('rentalcontracts')

	else:
		form = RentalContractEditForm(instance = item)

	context = {
			'form': form,
			'ent': ent
		}

	return render(request, 'rentalcontract_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentalcontract_resiliate(request, pk):
	today = datetime.now().date() - timedelta(days=1) 

	item_contract = get_object_or_404(RentalContract, pk=pk)
	item_appartment = Appartment.objects.get(pk=item_contract.appartment.pk)
	item_tenant = Tenant.objects.get(pk=item_contract.tenant.pk)

	item_contract.end_date = today
	item_contract.isTerminated = True
	item_appartment.isAvailable = True
	item_tenant.isTerminated = True

	item_tenant.save()
	item_contract.save()
	item_appartment.save()

	messages.info(request, "Contrat terminé !")
	return redirect('rentalcontract_view', item_contract.pk)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def rentalcontract_delete(request, pk):
	item = get_object_or_404(RentalContract, pk=pk)
	item.delete()
	messages.info(request, "Contrat supprimé !")
	return redirect('rentalcontracts')
	

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentpaid_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(RentPayment, pk=pk)
	context = {
		'item': item,
		'ent': ent
	}
	return render(request, 'rentpaid_view.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rentpaid_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(RentPayment, pk=pk)
	previous_amount = item.paid_amount

	if request.method == 'POST':
		form = RentEditForm(request.POST, instance = item)
		if form.is_valid():
			if item.account is not None:
				credit = BankAccount.objects.get(account_name=item.account)
				credit.balance -= previous_amount
				credit.balance += form.cleaned_data.get('paid_amount')
				credit.save()
			form.save()

			item.pending_payment = item.due_amount - item.paid_amount
			if item.pending_payment < 1:
				item.isPaid = True
			item.save()
			messages.success(request, f'Paiement modifié avec succès!')
			return redirect('rentpaid_view', item.pk)

	else:
		form = RentEditForm(instance = item)

		context = {
			'form': form,
			'item': item,
			'ent': ent
		}

		return render(request, 'rentpaid_edit.html', context)


class PayRent(View, LoginRequiredMixin):
	def get(self, request, *args, **kwargs):
		ent = None
		if Enterprise.objects.filter(id=1).exists():
			ent = Enterprise.objects.get(id=1)

		form = RentForm()
		items = RentPayment.objects.all().order_by('-id')[:10]
		try:
			context = {
				'form': form,
				'items': items,
				'ent': ent,
			}
			return render(self.request, 'payrent.html', context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "Aucune commande en cours")
			return redirect('unpaidrent')
		return render(self.request, 'payrent.html', context)

	def post(self, *args, **kwargs):
		form = RentForm(self.request.POST or None)
		today = datetime.now().date()
		alert_period = today + timedelta(days=alert_days)
		try:
			if form.is_valid():
				tenant = form.cleaned_data.get('locataire')
				appartment = form.cleaned_data.get('appartement')
				months = form.cleaned_data.get('nombre_de_mois')
				amount = form.cleaned_data.get('montant_payé')
				discount = form.cleaned_data.get('remise')
				account = form.cleaned_data.get('compte')
				label = form.cleaned_data.get('libéllé')
				paying_for = form.cleaned_data.get('paiement_pour')

				prev_payment = RentPayment.objects.filter(invoiced=False)
				for item in prev_payment:
					item.invoiced = True
					item.save()

				
				if account is not None:
					topup = BankAccount.objects.get(account_name=account)
					topup.balance += amount
					topup.save()


				contract = RentalContract.objects.get(tenant=tenant, appartment=appartment, end_date__gt=today)

				payrent = RentPayment.objects.create(
					created_by=self.request.user,
					tenant=tenant,
					appartment=appartment,
					paying_for=paying_for,
					quantity=months,
					account=account,
					label=label
					)

				payrent.discount = discount

				if paying_for == 'Loyer':
					payrent.due_amount = contract.rent * months
				elif paying_for == 'Garantie locative':
					payrent.due_amount = contract.deposit
				else:
					payrent.due_amount = amount

				
				if amount > payrent.due_amount:
					payrent.paid_amount = payrent.due_amount
				else:
					payrent.paid_amount = amount

				payrent.pending_payment = payrent.due_amount - payrent.paid_amount
				payrent.cash = amount
				if amount > payrent.due_amount:
					payrent.change = payrent.cash - payrent.due_amount

				if payrent.pending_payment < 1:
					payrent.isPaid = True
				payrent.invoiced = False
				payrent.save()

				if paying_for == 'Loyer':
					contract.next_payment_on = contract.next_payment_on + timedelta(days=(months*30))
					contract.save() 

				appartment = Appartment.objects.get(designation__exact=appartment)
				if paying_for == 'Loyer':
					if contract.end_date < alert_period and contract.end_date > today:
						appartment.isAvailable = True
						appartment.save()
					elif contract.end_date == today:
						appartment.isAvailable = True
						appartment.save()

				return redirect('rent_success')
				
		except:
			messages.warning(self.request, "Vérifiez les informations entrées !")
			return redirect('payrent')

		messages.warning(self.request, 'Informations invalides !')
		return redirect('payrent')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def rent_success(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now()
	item = RentPayment.objects.filter(created_by__exact=request.user).order_by('-id')[:1]
	context = {
			'item': item,
			'ent': ent,
	}
	return render(request, 'successrent.html', context)



class GenerateInvoiceRent(View, LoginRequiredMixin):
	def get(self, request, *args, **kwargs):
		ent = None
		if Enterprise.objects.filter(id=1).exists():
			ent = Enterprise.objects.get(id=1)

		item = RentPayment.objects.get(created_by__exact=self.request.user, invoiced=False)
		item.invoiced = True
		item.save()

		contract = RentalContract.objects.filter(tenant=item.tenant).last()

		context = {
			'item': item,
			'contract': contract,
			'ent': ent,
		}

		pdf = render_to_pdf('invoicerent.html', context)
		return HttpResponse(pdf, content_type='application/pdf')


class GenerateInvoiceRentOld(View, LoginRequiredMixin):
	def get(self, request, pk, *args, **kwargs):
		ent = None
		if Enterprise.objects.filter(id=1).exists():
			ent = Enterprise.objects.get(id=1)
		item = get_object_or_404(RentPayment, pk=pk)
		contract = RentalContract.objects.filter(tenant=item.tenant).last()
		
		context = {
			'item': item,
			'contract': contract,
			'ent': ent,
		}

		pdf = render_to_pdf('invoicerent.html', context)
		return HttpResponse(pdf, content_type='application/pdf')


#================================================================================================================================
#    REPORT    #
#================================================================================================================================


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def report_apparts(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	yesterday = today - timedelta(1)
	current_year = today.year
	last_year = current_year - 1

	start_date = today - timedelta(days=1095)
	end_date = today

	current_month = today.month
	current_month_name = None

	last_month = current_month - 1
	last_month_name = None

	if last_month < 1:
		last_month = 12
		current_year = last_year

	#warning = False
	#if request.exp is None:
	#	request.exp = today + timedelta(days=trial_days)
	#warning_period = request.exp - timedelta(days=warning_days)

	#if today > warning_period and today < request.exp:
	#	warning = True

	#exp = request.exp
	#exp = exp.strftime('%d/%m/%Y')

	if current_month == 1:
		current_month_name = "Janvier"
	elif current_month == 2:
		current_month_name = "Février"
	elif current_month == 3:
		current_month_name = "Mars"
	elif current_month == 4:
		current_month_name = "Avril"
	elif current_month == 5:
		current_month_name = "Mai"
	elif current_month == 6:
		current_month_name = "Juin"
	elif current_month == 7:
		current_month_name = "Juillet"
	elif current_month == 8:
		current_month_name = "Aout"
	elif current_month == 9:
		current_month_name = "Septembre"
	elif current_month == 10:
		current_month_name = "Octobre"
	elif current_month == 11:
		current_month_name = "Novembre"
	elif current_month == 12:
		current_month_name = "Decembre"

	if last_month == 1:
		last_month_name = "Janvier"
	elif last_month == 2:
		last_month_name = "Février"
	elif last_month == 3:
		last_month_name = "Mars"
	elif last_month == 4:
		last_month_name = "Avril"
	elif last_month == 5:
		last_month_name = "Mai"
	elif last_month == 6:
		last_month_name = "Juin"
	elif last_month == 7:
		last_month_name = "Juillet"
	elif last_month == 8:
		last_month_name = "Aout"
	elif last_month == 9:
		last_month_name = "Septembre"
	elif last_month == 10:
		last_month_name = "Octobre"
	elif last_month == 11:
		last_month_name = "Novembre"
	elif last_month == 12:
		last_month_name = "Decembre"

	rentpaid = RentPayment.objects.filter().aggregate(Sum('paid_amount')).get('paid_amount__sum')
	rentpaid_current_month = RentPayment.objects.filter(date_created__year=current_year, date_created__month=current_month).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	rentpaid_last_month = RentPayment.objects.filter(date_created__year=current_year, date_created__month=last_month).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	rentpaid_this_year = RentPayment.objects.filter(date_created__year=current_year).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	rentpaid_last_year = RentPayment.objects.filter(date_created__year=last_year).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	rentunpaid = RentalContract.objects.filter(next_payment_on__lte=today, isTerminated=False).order_by('next_payment_on')
	rentunpaid_count = RentalContract.objects.filter(next_payment_on__lte=today, isTerminated=False).count()
	rentunpaid_amount = RentalContract.objects.filter(next_payment_on__lte=today, isTerminated=False).aggregate(Sum('rent')).get('rent__sum')
	rentpaid_partially_amount = RentPayment.objects.filter().aggregate(Sum('pending_payment')).get('pending_payment__sum')
	rentpaid_partially = RentPayment.objects.filter().count()
	tenants_count = Tenant.objects.filter(date_created__year=current_year, date_created__month=current_month, isTerminated=False).count()
	apparts_taken = Appartment.objects.filter(isAvailable=False).count()
	apparts_free = Appartment.objects.filter(isAvailable=True).count()
	income = Income.objects.filter(entreprise='DNK Appartements').aggregate(Sum('amount')).get('amount__sum')
	income_current_month = Income.objects.filter(entreprise='DNK Appartements', date_created__year=current_year, date_created__month=current_month).aggregate(Sum('amount')).get('amount__sum')
	income_last_month = Income.objects.filter(entreprise='DNK Appartements', date_created__year=current_year, date_created__month=last_month).aggregate(Sum('amount')).get('amount__sum')
	income_this_year = Income.objects.filter(entreprise='DNK Appartements', date_created__year=current_year).aggregate(Sum('amount')).get('amount__sum')
	income_last_year = Income.objects.filter(entreprise='DNK Appartements', date_created__year=last_year).aggregate(Sum('amount')).get('amount__sum')
	expenses = Disbursement.objects.filter(entreprise='DNK Appartements').aggregate(Sum('amount')).get('amount__sum')
	expenses_current_month = Disbursement.objects.filter(entreprise='DNK Appartements', date_created__year=current_year, date_created__month=current_month).aggregate(Sum('amount')).get('amount__sum')
	expenses_last_month = Disbursement.objects.filter(entreprise='DNK Appartements', date_created__year=current_year, date_created__month=last_month).aggregate(Sum('amount')).get('amount__sum')
	expenses_this_year = Disbursement.objects.filter(entreprise='DNK Appartements', date_created__year=current_year).aggregate(Sum('amount')).get('amount__sum')
	expenses_last_year = Disbursement.objects.filter(entreprise='DNK Appartements', date_created__year=last_year).aggregate(Sum('amount')).get('amount__sum')
	salaries = Salary.objects.filter().aggregate(Sum('amount')).get('amount__sum')
	salaries_current_month = Salary.objects.filter(date_created__year=current_year, date_created__month=current_month).aggregate(Sum('amount')).get('amount__sum')
	salaries_last_month = Salary.objects.filter(date_created__year=current_year, date_created__month=last_month).aggregate(Sum('amount')).get('amount__sum')
	salaries_this_year = Salary.objects.filter(date_created__year=current_year).aggregate(Sum('amount')).get('amount__sum')
	salaries_last_year = Salary.objects.filter(date_created__year=last_year).aggregate(Sum('amount')).get('amount__sum')

	if rentunpaid_amount is None:
		rentunpaid_amount = 0

	if rentunpaid_count is None:
		rentunpaid_count = 0

	if rentpaid_partially_amount is None:
		rentpaid_partially_amount = 0

	if rentpaid is None:
		rentpaid = 0
	if rentpaid_current_month is None:
		rentpaid_current_month = 0
	if rentpaid_last_month is None:
		rentpaid_last_month = 0
	if rentpaid_this_year is None:
		rentpaid_this_year = 0
	if rentpaid_last_year is None:
		rentpaid_last_year = 0

	if income is None:
		income = 0
	if income_current_month is None:
		income_current_month = 0
	if income_last_month is None:
		income_last_month = 0
	if income_this_year is None:
		income_this_year = 0
	if income_last_year is None:
		income_last_year = 0

	if expenses is None:
		expenses = 0
	if expenses_current_month is None:
		expenses_current_month = 0
	if expenses_last_month is None:
		expenses_last_month = 0
	if expenses_this_year is None:
		expenses_this_year = 0
	if expenses_last_year is None:
		expenses_last_year = 0

	if salaries is None:
		salaries = 0
	if salaries_current_month is None:
		salaries_current_month = 0
	if salaries_last_month is None:
		salaries_last_month = 0
	if salaries_this_year is None:
		salaries_this_year = 0
	if salaries_last_year is None:
		salaries_last_year = 0

	total_expenses = expenses + salaries
	total_expenses_current_month = expenses_current_month + salaries_current_month
	total_expenses_last_month = expenses_last_month + salaries_last_month
	total_expenses_this_year = expenses_this_year + salaries_this_year
	total_expenses_last_year = expenses_last_year + salaries_last_year

	total_income = income + rentpaid
	total_income_current_month = income_current_month + rentpaid_current_month
	total_income_last_month = income_last_month + rentpaid_last_month
	total_income_this_year = income_this_year + rentpaid_this_year
	total_income_last_year = income_last_year + rentpaid_last_year

	impf_amount = impf

	irl_total = (rentpaid * irl)/100
	irl_current_month = (rentpaid_current_month * ent.irl)/100
	irl_last_month = (rentpaid_last_month * ent.irl)/100
	irl_this_year = (rentpaid_this_year * ent.irl)/100
	irl_last_year = (rentpaid_last_year * ent.irl)/100

	ipr_total = (salaries * ipr)/100
	ipr_current_month = (salaries_current_month * ipr)/100
	ipr_last_month = (salaries_last_month * ipr)/100
	ipr_this_year = (salaries_this_year * ipr)/100
	ipr_last_year = (salaries_last_year * ipr)/100

	context = {
		'today': today,
		'yesterday': yesterday,
		'current_year': str(current_year),
		'last_year': str(last_year),
		'current_month': current_month,
		'current_month_name': current_month_name,
		'last_month': last_month,
		'last_month_name': last_month_name,
		'rentpaid_partially': rentpaid_partially,
		'rentpaid_partially_amount': rentpaid_partially_amount,
		'rentunpaid': rentunpaid,
		'rentunpaid_count': rentunpaid_count,
		'rentunpaid_amount': rentunpaid_amount,
		'tenants_count': tenants_count,
		'apparts_free': apparts_free,
		'apparts_taken': apparts_taken,
		'rentpaid': rentpaid,
		'rentpaid_current_month': rentpaid_current_month,
		'rentpaid_last_month': rentpaid_last_month,
		'rentpaid_last_year': rentpaid_last_year,
		'rentpaid_this_year': rentpaid_this_year,
		'income': income,
		'income_current_month': income_current_month,
		'income_last_month': income_last_month,
		'income_last_year': income_last_year,
		'income_this_year': income_this_year,
		'expenses': expenses,
		'expenses_current_month': expenses_current_month,
		'expenses_last_month': expenses_last_month,
		'expenses_last_year': expenses_last_year,
		'expenses_this_year': expenses_this_year,
		'salaries': salaries,
		'salaries_current_month': salaries_current_month,
		'salaries_last_month': salaries_last_month,
		'salaries_last_year': salaries_last_year,
		'salaries_this_year': salaries_this_year,
		'total_income': total_income,
		'total_income_current_month': total_income_current_month,
		'total_income_last_month': total_income_last_month,
		'total_income_last_year': total_income_last_year,
		'total_income_this_year': total_income_this_year,
		'total_expenses': total_expenses,
		'total_expenses_current_month': total_expenses_current_month,
		'total_expenses_last_month': total_expenses_last_month,
		'total_expenses_last_year': total_expenses_last_year,
		'total_expenses_this_year': total_expenses_this_year,
		'irl_total': irl_total,
		'irl_current_month': irl_current_month,
		'irl_last_month': irl_last_month,
		'irl_last_year': irl_last_year,
		'irl_this_year': irl_this_year,
		'ipr_total': ipr_total,
		'ipr_current_month': ipr_current_month,
		'ipr_last_month': ipr_last_month,
		'ipr_last_year': ipr_last_year,
		'ipr_this_year': ipr_this_year,
		'impf': ent.impf,
		'ent': ent,
	}
	return render(request, "report_apparts.html", context)


#================================================================================================================================
#    RH    #
#================================================================================================================================


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def partners(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Partner.objects.all().order_by('designation')
	searched = None
	lookup1 = None
	lookup2 = None
	if request.method == 'POST':
		searched = request.POST.get('search')
		lookup1 = Tenant.objects.filter(designation__icontains = searched).order_by('designation')
		lookup2 = Tenant.objects.filter(description__icontains = searched).order_by('designation')
		
		context = {
			'lookup1': lookup1,
			'lookup2': lookup2,
			'ent': ent,
		}
	else:
		context = {
			'items': items,
		}
	return render(request, "partners.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def partner_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = PartnerForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, f'Partenaire créé avec succès!')
			return redirect('partners')	
	else:
		form = PartnerForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'partner_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def partner_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Partner, pk=pk)
	#contract = RentalContract.objects.filter(tenant=item).last()
	#contracts = RentalContract.objects.filter(tenant=item).order_by('-id')
	#payments = RentPayment.objects.filter(tenant=item).order_by('-id')

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'ent': ent,
	#'contract': contract,
	#'contracts': contracts,
	#'payments': payments,
	'today': today,
	'alert_period': alert_period
	}
	return render(request, 'partner.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def partner_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Partner, pk=pk)
	
	if request.method == 'POST':
		form = PartnerForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			messages.success(request, f'Partenaire modifié avec succès!')
			return redirect('partner_view', item.pk)

	else:
		form = PartnerForm(instance = item)

		context = {
			'form': form,
			'ent': ent,
		}

		return render(request, 'partner_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def partner_delete(request, pk):
	item = get_object_or_404(Partner, pk=pk)
	item.delete()
	messages.info(request, "Partenaire supprimé !")
	return redirect('partners')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def positions(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Position.objects.all().order_by('designation')
	searched = None
	lookup1 = None
	lookup2 = None
	if request.method == 'POST':
		searched = request.POST.get('search')
		lookup1 = Position.objects.filter(designation__icontains = searched).order_by('designation')
		lookup2 = Position.objects.filter(description__icontains = searched).order_by('designation')
		
		context = {
			'lookup1': lookup1,
			'lookup2': lookup2,
			'ent': ent,
		}
	else:
		context = {
			'items': items,
			'ent': ent,
		}
	return render(request, "positions.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def position_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = PositionForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, f'Poste créé avec succès!')
			return redirect('positions')	
	else:
		form = PositionForm()
		context = {
			'form': form,
			'ent': ent
		}
	return render(request, 'position_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def position_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Position, pk=pk)
	#contract = RentalContract.objects.filter(tenant=item).last()
	#contracts = RentalContract.objects.filter(tenant=item).order_by('-id')
	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'ent': ent,
	#'contract': contract,
	#'contracts': contracts,
	'today': today,
	'alert_period': alert_period
	}
	return render(request, 'position.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def position_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Position, pk=pk)
	
	if request.method == 'POST':
		form = PositionForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			messages.success(request, f'"Poste modifié avec succès!')
			return redirect('position_view', item.pk)

	else:
		form = PositionForm(instance = item)

		context = {
			'form': form,
			'ent': ent,
		}

		return render(request, 'position_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def position_delete(request, pk):
	item = get_object_or_404(Position, pk=pk)
	item.delete()
	messages.info(request, "Poste supprimé !")
	return redirect('positions')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def employees(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Employee.objects.all().order_by('firstname')
	searched = None
	lookup1 = None
	lookup2 = None
	lookup3 = None
	lookup4 = None
	if request.method == 'POST':
		searched = request.POST.get('search')
		lookup1 = Employee.objects.filter(firstname__icontains = searched).order_by('firstname')
		lookup2 = Employee.objects.filter(lastname__icontains = searched).order_by('firstname')
		lookup3 = Employee.objects.filter(email__icontains = searched).order_by('firstname')
		lookup4 = Employee.objects.filter(phone__icontains = searched).order_by('firstname')
		
		context = {
			'lookup1': lookup1,
			'lookup2': lookup2,
			'lookup3': lookup3,
			'lookup4': lookup4,
			'ent': ent,
		}
	else:
		context = {
			'items': items,
			'ent': ent,
		}
	return render(request, "employees.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def employee_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = EmployeeForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, f'Employé créé avec succès!')
			return redirect('employees')	
	else:
		form = EmployeeForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'employee_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def employee_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Employee, pk=pk)
	contract = WorkContract.objects.filter(employee=item).last()
	contracts = WorkContract.objects.filter(employee=item).order_by('-id')
	payments = Salary.objects.filter(employee=item).order_by('-id')

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'ent': ent,
	'contract': contract,
	'contracts': contracts,
	'payments': payments,
	'today': today,
	'alert_period': alert_period
	}
	return render(request, 'employee.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def employee_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Employee, pk=pk)
	
	if request.method == 'POST':
		form = EmployeeForm(request.POST, instance = item)
		card_form = EmployeeIdForm(request.POST, request.FILES, instance = item)
		if form.is_valid() and card_form.is_valid():
			form.save()
			card_form.save()
			messages.success(request, f'Employé créé avec succès!')
			return redirect('employee_view', item.pk)

	else:
		form = EmployeeForm(instance = item)
		card_form = EmployeeIdForm(instance = item)

		context = {
			'form': form,
			'card_form': card_form,
			'ent': ent,
		}

		return render(request, 'employee_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def employee_delete(request, pk):
	item = get_object_or_404(Employee, pk=pk)
	item.delete()
	messages.info(request, "Employé supprimé !")
	return redirect('employees')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontracts(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = WorkContract.objects.all().order_by('id')
	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "workcontracts.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontracts_on(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = WorkContract.objects.filter(end_date__gt=today).order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "workcontracts_on.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontracts_off(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = WorkContract.objects.filter(end_date__lt=today).order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "workcontracts_off.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontracts_off_soon(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)
	items = WorkContract.objects.all().order_by('-id')
	context = {
		'items': items,
		'today': today,
		'alert_period': alert_period,
		'ent': ent,
	}
	return render(request, "workcontracts_off_soon.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontract_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = WorkContractForm(request.POST)
		if form.is_valid():
			contract = WorkContract.objects.create(
				created_by = request.user,
				employee = form.cleaned_data.get('travailleur'),
				position = form.cleaned_data.get('poste'),
				start_date = form.cleaned_data.get('date_début'),
				end_date = form.cleaned_data.get('date_fin'),
				)

			contract.department = contract.position.department
			contract.salary = contract.position.salary
			contract.save()

			position = Position.objects.get(designation=form.cleaned_data.get('poste'))
			position.isAvailable = False
			position.save()

			#employee = Employee.objects.get(id=contract.employee.id)
			#employee.isTerminated = False
			#employee.save()

			messages.success(request, f'Contrat créé avec succès!')
			return redirect('workcontracts')
				
	else:
		form = WorkContractForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'workcontract_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontract_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(WorkContract, pk=pk)
	#contract = RentalContract.objects.filter(tenant=item).last()
	#contracts = RentalContract.objects.filter(tenant=item).order_by('-id')
	#payments = RentPayment.objects.filter(tenant=item).order_by('-id')

	today = datetime.now().date()
	alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'ent': ent,
	#'contract': contract,
	#'contracts': contracts,
	#'payments': payments,
	'today': today,
	'alert_period': alert_period
	}
	return render(request, 'workcontract.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontract_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(WorkContract, pk=pk)
	
	if request.method == 'POST':
		form = WorkContractEditForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			messages.success(request, f'Contrat de travail modifié avec succès!')
			return redirect('workcontract_view', item.pk)

	else:
		form = WorkContractEditForm(instance = item)

		context = {
			'form': form,
			'ent': ent,
		}

		return render(request, 'workcontract_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def workcontract_resiliate(request, pk):
	today = datetime.now().date() - timedelta(days=1) 

	item_contract = get_object_or_404(WorkContract, pk=pk)
	item_position = Position.objects.get(pk=item_contract.position.pk)
	item_employee = Employee.objects.get(pk=item_contract.employee.pk)

	item_contract.end_date = today
	item_contract.isTerminated = True
	item_position.isAvailable = True
	item_employee.isTerminated = True

	item_employee.save()
	item_contract.save()
	item_position.save()

	messages.info(request, "Contrat terminé !")
	return redirect('workcontract_view', item_contract.pk)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def workcontract_delete(request, pk):
	item = get_object_or_404(WorkContract, pk=pk)
	item.delete()
	messages.info(request, "Contrat de travail supprimé !")
	return redirect('workcontracts')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def salaries(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Salary.objects.all().order_by('-id')
	context = {
		'items': items,
		'ent': ent,
	}
	return render(request, "salaries.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def salary_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = SalaryForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, f'Paiement enregistré avec succès!')
			return redirect('salaries')	
	else:
		form = SalaryForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'salary_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def salary_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Salary, pk=pk)
	
	if request.method == 'POST':
		form = SalaryForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			messages.success(request, f'Paiement modifié avec succès!')
			return redirect('salaries')

	else:
		form = SalaryForm(instance = item)

		context = {
			'form': form,
			'ent': ent,
		}
		return render(request, 'salary_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def salary_delete(request, pk):
	item = get_object_or_404(Salary, pk=pk)
	item.delete()
	messages.info(request, "Paiement supprimé !")
	return redirect('salaries')



#================================================================================================================================
#    ACCOUNTING    #
#================================================================================================================================


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def accounting(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	appartments_income = RentPayment.objects.aggregate(Sum('paid_amount')).get('paid_amount__sum')
	
	income = Income.objects.aggregate(Sum('amount')).get('amount__sum')
	expenses = Disbursement.objects.aggregate(Sum('amount')).get('amount__sum')
	salaries = Salary.objects.aggregate(Sum('amount')).get('amount__sum')

	apparts = appartments_income
	if apparts is None:
		apparts = 0

	other_income = income
	if other_income is None:
		other_income = 0

	expenses = expenses
	if expenses is None:
		expenses = 0

	salaries = salaries
	if salaries is None:
		salaries = 0

	balance = (apparts + 0 + 0 + income) - (expenses + salaries)
	income = apparts + other_income
	expenses = expenses + salaries

	context = {
		'apparts': apparts,
		'other_income': other_income,
		'balance': balance,
		'income': income,
		'expenses': expenses,
		'ent': ent,
	}
	return render(request, "accounting.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def expenses(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Disbursement.objects.all().order_by('-date_created')
	
	if request.method == 'POST':
		searched = request.POST.get('search')
		lookup1 = Disbursement.objects.filter(description__icontains = searched).order_by('-date_created')
		
		context = {
		'lookup1': lookup1,
		'ent': ent,
	}
	else:	

		context = {
			'items': items,
			'ent': ent,
		}
	return render(request, "expenses.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def expense_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = ExpenseForm(request.POST)
		if form.is_valid():
			if form.cleaned_data.get('account') is not None:
				debit = BankAccount.objects.get(account_name=form.cleaned_data.get('account'))
				debit.balance -= form.cleaned_data.get('amount')
				debit.save()
			form.save()
			
			messages.success(request, f'Dépense créée avec succès!')
			return redirect('expenses')
	else:
		form = ExpenseForm()
		context = {
			'form': form,
			'ent': ent,
		}
		return render(request, 'expense_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def expense_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Disbursement, pk=pk)
	previous_amount = item.amount
	
	if request.method == 'POST':
		form = ExpenseForm(request.POST, instance = item)
		if form.is_valid():
			if item.account is not None:
				debit = BankAccount.objects.get(account_name=form.cleaned_data.get('account'))
				debit.balance += previous_amount
				debit.balance -= form.cleaned_data.get('amount')
				debit.save()
			form.save()
			messages.success(request, f'Dépense modifiée avec succès!')
			return redirect('expenses')
	else:
		form = ExpenseForm(instance = item)
		context = {
			'form': form,
			'ent': ent,
		}
		return render(request, 'expense_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def expense_delete(request, pk):
	item = get_object_or_404(Disbursement, pk=pk)
	item.delete()
	messages.info(request, "Dépense supprimée !")
	return redirect('expenses')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def income(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Income.objects.all().order_by('-date_created')

	if request.method == 'POST':
		searched = request.POST.get('search')
		lookup1 = Income.objects.filter(description__icontains = searched).order_by('-date_created')
		
		context = {
		'lookup1': lookup1,
		'ent': ent,
	}
	else:	
		context = {
			'items': items,
			'ent': ent,
		}

	return render(request, "income.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def income_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = IncomeForm(request.POST)
		if form.is_valid():
			if form.cleaned_data.get('account') is not None:
				credit = BankAccount.objects.get(account_name=form.cleaned_data.get('account'))
				credit.balance += form.cleaned_data.get('amount')
				credit.save()
			form.save()

			messages.success(request, f'Encaissement créé avec succès!')
			return redirect('income')
	else:
		form = IncomeForm()
		context = {
			'form': form,
			'ent': ent,
		}
		return render(request, 'income_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def income_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(Income, pk=pk)
	previous_amount = item.amount
	
	if request.method == 'POST':
		form = IncomeForm(request.POST, instance = item)
		if form.is_valid():
			if item.account is not None:
				credit = BankAccount.objects.get(account_name=form.cleaned_data.get('account'))
				credit.balance -= previous_amount
				credit.balance += form.cleaned_data.get('amount')
				credit.save()
			form.save()
			messages.success(request, f'Encaissement modifié avec succès!')
			return redirect('income')
	else:
		form = IncomeForm(instance = item)
		context = {
			'form': form,
			'ent': ent,
		}
		return render(request, 'income_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def income_delete(request, pk):
	item = get_object_or_404(Income, pk=pk)
	item.delete()
	messages.info(request, "Encaissement supprimé !")
	return redirect('income')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def bankaccounts(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = BankAccount.objects.filter().order_by('account_name')
	total_balance = BankAccount.objects.all().aggregate(Sum('balance')).get('balance__sum')
	#today = datetime.now().date()
	#alert_period = today + timedelta(days=alert_days)
	context = {
		'items': items,
		'total_balance': total_balance,
		'ent': ent,
		#'today': today,
		#'alert_period': alert_period
	}
	return render(request, "bankaccounts.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def bankaccount_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = BankAccountForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, f'Compte financier créé avec succès!')
			return redirect('bankaccounts')
				
	else:
		form = BankAccountForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'bankaccount_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def bankaccount_view(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(BankAccount, pk=pk)

	#today = datetime.now().date()
	#alert_period = today + timedelta(days=alert_days)

	context = {
	'item': item,
	'ent': ent,
	#'today': today,
	#'alert_period': alert_period
	}
	return render(request, 'bankaccount.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def bankaccount_edit(request, pk):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	item = get_object_or_404(BankAccount, pk=pk)
	
	if request.method == 'POST':
		form = BankAccountEditForm(request.POST, instance = item)
		if form.is_valid():
			form.save()
			messages.success(request, f'Compte financier modifié avec succès!')
			return redirect('bankaccount_view', item.pk)

	else:
		form = BankAccountEditForm(instance = item)

		context = {
			'form': form,
			'ent': ent,
		}

		return render(request, 'bankaccount_edit.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def bankaccount_close(request, pk):
	item = get_object_or_404(BankAccount, pk=pk)
	if item.balance < 1:
		item.isClosed = True
		item.save()
		messages.info(request, "Compte financier fermé !")
		return redirect('bankaccount_view', item.pk)
	else:
		messages.warning(request, "Veuillez d'abord transférer le solde de ce compte vers un autre !")
		return redirect('bankaccount_view', item.pk)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def bankaccount_delete(request, pk):
	item = get_object_or_404(BankAccount, pk=pk)
	item.delete()
	messages.info(request, "Compte financier supprimé !")
	return redirect('bankaccounts')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def transfers(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	items = Transfer.objects.all().order_by('-id')
	
	context = {
		'items': items,
		'ent': ent,
	}
	return render(request, "transfers.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def transfer_add(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	if request.method == 'POST':
		form = TransferForm(request.POST)
		if form.is_valid():
			transfer = Transfer.objects.create(
				created_by = request.user,
				from_account = form.cleaned_data.get('source'),
				to_account = form.cleaned_data.get('destination'),
				amount = form.cleaned_data.get('montant'),
				description = form.cleaned_data.get('libéllé'),
				)

			source = BankAccount.objects.get(account_name=transfer.from_account)
			source.balance -= transfer.amount
			source.save()

			destination = BankAccount.objects.get(account_name=transfer.to_account) 
			destination.balance += transfer.amount
			destination.save()

			messages.success(request, f'Virement interne effectué avec succès!')
			return redirect('bankaccounts')
				
	else:
		form = TransferForm()
		context = {
			'form': form,
			'ent': ent,
		}
	return render(request, 'transfer_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def transfer_delete(request, pk):
	item = get_object_or_404(Transfer, pk=pk)

	source = BankAccount.objects.get(account_name=item.from_account)
	source.balance += item.amount
	source.save()

	destination = BankAccount.objects.get(account_name=item.to_account) 
	destination.balance -= transfer.amount
	destination.save()

	item.delete()

	messages.info(request, "Virement interne supprimé !")
	return redirect('transfers')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def results(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	today = datetime.now()
	
	year1 = today.year - 2
	year2 = today.year - 1
	year3 = today.year

	appartments_year1 = RentPayment.objects.filter(date_created__year=year1).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2 = RentPayment.objects.filter(date_created__year=year2).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3 = RentPayment.objects.filter(date_created__year=year3).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_jan = RentPayment.objects.filter(date_created__year=year3, date_created__month=1).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_feb = RentPayment.objects.filter(date_created__year=year3, date_created__month=2).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_mar = RentPayment.objects.filter(date_created__year=year3, date_created__month=3).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_apr = RentPayment.objects.filter(date_created__year=year3, date_created__month=4).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_may = RentPayment.objects.filter(date_created__year=year3, date_created__month=5).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_jun = RentPayment.objects.filter(date_created__year=year3, date_created__month=6).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_jul = RentPayment.objects.filter(date_created__year=year3, date_created__month=7).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_aug = RentPayment.objects.filter(date_created__year=year3, date_created__month=8).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_sep = RentPayment.objects.filter(date_created__year=year3, date_created__month=9).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_oct = RentPayment.objects.filter(date_created__year=year3, date_created__month=10).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_nov = RentPayment.objects.filter(date_created__year=year3, date_created__month=11).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year3_dec = RentPayment.objects.filter(date_created__year=year3, date_created__month=12).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_jan = RentPayment.objects.filter(date_created__year=year2, date_created__month=1).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_feb = RentPayment.objects.filter(date_created__year=year2, date_created__month=2).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_mar = RentPayment.objects.filter(date_created__year=year2, date_created__month=3).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_apr = RentPayment.objects.filter(date_created__year=year2, date_created__month=4).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_may = RentPayment.objects.filter(date_created__year=year2, date_created__month=5).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_jun = RentPayment.objects.filter(date_created__year=year2, date_created__month=6).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_jul = RentPayment.objects.filter(date_created__year=year2, date_created__month=7).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_aug = RentPayment.objects.filter(date_created__year=year2, date_created__month=8).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_sep = RentPayment.objects.filter(date_created__year=year2, date_created__month=9).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_oct = RentPayment.objects.filter(date_created__year=year2, date_created__month=10).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_nov = RentPayment.objects.filter(date_created__year=year2, date_created__month=11).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year2_dec = RentPayment.objects.filter(date_created__year=year2, date_created__month=12).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_jan = RentPayment.objects.filter(date_created__year=year1, date_created__month=1).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_feb = RentPayment.objects.filter(date_created__year=year1, date_created__month=2).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_mar = RentPayment.objects.filter(date_created__year=year1, date_created__month=3).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_apr = RentPayment.objects.filter(date_created__year=year1, date_created__month=4).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_may = RentPayment.objects.filter(date_created__year=year1, date_created__month=5).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_jun = RentPayment.objects.filter(date_created__year=year1, date_created__month=6).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_jul = RentPayment.objects.filter(date_created__year=year1, date_created__month=7).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_aug = RentPayment.objects.filter(date_created__year=year1, date_created__month=8).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_sep = RentPayment.objects.filter(date_created__year=year1, date_created__month=9).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_oct = RentPayment.objects.filter(date_created__year=year1, date_created__month=10).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_nov = RentPayment.objects.filter(date_created__year=year1, date_created__month=11).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	appartments_year1_dec = RentPayment.objects.filter(date_created__year=year1, date_created__month=12).aggregate(Sum('paid_amount')).get('paid_amount__sum')
	other_year1 = Income.objects.filter(date_created__year=year1).aggregate(Sum('amount')).get('amount__sum')
	other_year2 = Income.objects.filter(date_created__year=year2).aggregate(Sum('amount')).get('amount__sum')
	other_year3 = Income.objects.filter(date_created__year=year3).aggregate(Sum('amount')).get('amount__sum')
	other_year3_jan = Income.objects.filter(date_created__year=year3, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	other_year3_feb = Income.objects.filter(date_created__year=year3, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	other_year3_mar = Income.objects.filter(date_created__year=year3, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	other_year3_apr = Income.objects.filter(date_created__year=year3, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	other_year3_may = Income.objects.filter(date_created__year=year3, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	other_year3_jun = Income.objects.filter(date_created__year=year3, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	other_year3_jul = Income.objects.filter(date_created__year=year3, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	other_year3_aug = Income.objects.filter(date_created__year=year3, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	other_year3_sep = Income.objects.filter(date_created__year=year3, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	other_year3_oct = Income.objects.filter(date_created__year=year3, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	other_year3_nov = Income.objects.filter(date_created__year=year3, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	other_year3_dec = Income.objects.filter(date_created__year=year3, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	other_year2_jan = Income.objects.filter(date_created__year=year2, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	other_year2_feb = Income.objects.filter(date_created__year=year2, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	other_year2_mar = Income.objects.filter(date_created__year=year2, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	other_year2_apr = Income.objects.filter(date_created__year=year2, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	other_year2_may = Income.objects.filter(date_created__year=year2, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	other_year2_jun = Income.objects.filter(date_created__year=year2, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	other_year2_jul = Income.objects.filter(date_created__year=year2, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	other_year2_aug = Income.objects.filter(date_created__year=year2, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	other_year2_sep = Income.objects.filter(date_created__year=year2, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	other_year2_oct = Income.objects.filter(date_created__year=year2, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	other_year2_nov = Income.objects.filter(date_created__year=year2, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	other_year2_dec = Income.objects.filter(date_created__year=year2, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	other_year1_jan = Income.objects.filter(date_created__year=year1, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	other_year1_feb = Income.objects.filter(date_created__year=year1, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	other_year1_mar = Income.objects.filter(date_created__year=year1, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	other_year1_apr = Income.objects.filter(date_created__year=year1, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	other_year1_may = Income.objects.filter(date_created__year=year1, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	other_year1_jun = Income.objects.filter(date_created__year=year1, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	other_year1_jul = Income.objects.filter(date_created__year=year1, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	other_year1_aug = Income.objects.filter(date_created__year=year1, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	other_year1_sep = Income.objects.filter(date_created__year=year1, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	other_year1_oct = Income.objects.filter(date_created__year=year1, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	other_year1_nov = Income.objects.filter(date_created__year=year1, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	other_year1_dec = Income.objects.filter(date_created__year=year1, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1 = Disbursement.objects.filter(date_created__year=year1).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2 = Disbursement.objects.filter(date_created__year=year2).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3 = Disbursement.objects.filter(date_created__year=year3).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_jan = Disbursement.objects.filter(date_created__year=year3, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_feb = Disbursement.objects.filter(date_created__year=year3, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_mar = Disbursement.objects.filter(date_created__year=year3, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_apr = Disbursement.objects.filter(date_created__year=year3, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_may = Disbursement.objects.filter(date_created__year=year3, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_jun = Disbursement.objects.filter(date_created__year=year3, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_jul = Disbursement.objects.filter(date_created__year=year3, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_aug = Disbursement.objects.filter(date_created__year=year3, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_sep = Disbursement.objects.filter(date_created__year=year3, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_oct = Disbursement.objects.filter(date_created__year=year3, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_nov = Disbursement.objects.filter(date_created__year=year3, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	expenses_year3_dec = Disbursement.objects.filter(date_created__year=year3, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_jan = Disbursement.objects.filter(date_created__year=year2, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_feb = Disbursement.objects.filter(date_created__year=year2, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_mar = Disbursement.objects.filter(date_created__year=year2, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_apr = Disbursement.objects.filter(date_created__year=year2, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_may = Disbursement.objects.filter(date_created__year=year2, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_jun = Disbursement.objects.filter(date_created__year=year2, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_jul = Disbursement.objects.filter(date_created__year=year2, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_aug = Disbursement.objects.filter(date_created__year=year2, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_sep = Disbursement.objects.filter(date_created__year=year2, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_oct = Disbursement.objects.filter(date_created__year=year2, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_nov = Disbursement.objects.filter(date_created__year=year2, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	expenses_year2_dec = Disbursement.objects.filter(date_created__year=year2, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_jan = Disbursement.objects.filter(date_created__year=year1, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_feb = Disbursement.objects.filter(date_created__year=year1, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_mar = Disbursement.objects.filter(date_created__year=year1, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_apr = Disbursement.objects.filter(date_created__year=year1, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_may = Disbursement.objects.filter(date_created__year=year1, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_jun = Disbursement.objects.filter(date_created__year=year1, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_jul = Disbursement.objects.filter(date_created__year=year1, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_aug = Disbursement.objects.filter(date_created__year=year1, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_sep = Disbursement.objects.filter(date_created__year=year1, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_oct = Disbursement.objects.filter(date_created__year=year1, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_nov = Disbursement.objects.filter(date_created__year=year1, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	expenses_year1_dec = Disbursement.objects.filter(date_created__year=year1, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1 = Salary.objects.filter(date_created__year=year1).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2 = Salary.objects.filter(date_created__year=year2).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3 = Salary.objects.filter(date_created__year=year3).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_jan = Salary.objects.filter(date_created__year=year3, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_feb = Salary.objects.filter(date_created__year=year3, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_mar = Salary.objects.filter(date_created__year=year3, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_apr = Salary.objects.filter(date_created__year=year3, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_may = Salary.objects.filter(date_created__year=year3, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_jun = Salary.objects.filter(date_created__year=year3, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_jul = Salary.objects.filter(date_created__year=year3, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_aug = Salary.objects.filter(date_created__year=year3, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_sep = Salary.objects.filter(date_created__year=year3, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_oct = Salary.objects.filter(date_created__year=year3, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_nov = Salary.objects.filter(date_created__year=year3, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	salaries_year3_dec = Salary.objects.filter(date_created__year=year3, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_jan = Salary.objects.filter(date_created__year=year2, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_feb = Salary.objects.filter(date_created__year=year2, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_mar = Salary.objects.filter(date_created__year=year2, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_apr = Salary.objects.filter(date_created__year=year2, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_may = Salary.objects.filter(date_created__year=year2, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_jun = Salary.objects.filter(date_created__year=year2, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_jul = Salary.objects.filter(date_created__year=year2, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_aug = Salary.objects.filter(date_created__year=year2, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_sep = Salary.objects.filter(date_created__year=year2, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_oct = Salary.objects.filter(date_created__year=year2, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_nov = Salary.objects.filter(date_created__year=year2, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	salaries_year2_dec = Salary.objects.filter(date_created__year=year2, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_jan = Salary.objects.filter(date_created__year=year1, date_created__month=1).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_feb = Salary.objects.filter(date_created__year=year1, date_created__month=2).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_mar = Salary.objects.filter(date_created__year=year1, date_created__month=3).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_apr = Salary.objects.filter(date_created__year=year1, date_created__month=4).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_may = Salary.objects.filter(date_created__year=year1, date_created__month=5).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_jun = Salary.objects.filter(date_created__year=year1, date_created__month=6).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_jul = Salary.objects.filter(date_created__year=year1, date_created__month=7).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_aug = Salary.objects.filter(date_created__year=year1, date_created__month=8).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_sep = Salary.objects.filter(date_created__year=year1, date_created__month=9).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_oct = Salary.objects.filter(date_created__year=year1, date_created__month=10).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_nov = Salary.objects.filter(date_created__year=year1, date_created__month=11).aggregate(Sum('amount')).get('amount__sum')
	salaries_year1_dec = Salary.objects.filter(date_created__year=year1, date_created__month=12).aggregate(Sum('amount')).get('amount__sum')
	
	if appartments_year1 is None:
		appartments_year1 = 0
	if appartments_year1_jan is None:
		appartments_year1_jan = 0
	if appartments_year1_feb is None:
		appartments_year1_feb = 0
	if appartments_year1_mar is None:
		appartments_year1_mar = 0
	if appartments_year1_apr is None:
		appartments_year1_apr = 0
	if appartments_year1_may is None:
		appartments_year1_may = 0
	if appartments_year1_jun is None:
		appartments_year1_jun = 0
	if appartments_year1_jul is None:
		appartments_year1_jul = 0
	if appartments_year1_aug is None:
		appartments_year1_aug = 0
	if appartments_year1_sep is None:
		appartments_year1_sep = 0
	if appartments_year1_oct is None:
		appartments_year1_oct = 0
	if appartments_year1_nov is None:
		appartments_year1_nov = 0
	if appartments_year1_dec is None:
		appartments_year1_dec = 0

	if appartments_year2 is None:
		appartments_year2 = 0
	if appartments_year2_jan is None:
		appartments_year2_jan = 0
	if appartments_year2_feb is None:
		appartments_year2_feb = 0
	if appartments_year2_mar is None:
		appartments_year2_mar = 0
	if appartments_year2_apr is None:
		appartments_year2_apr = 0
	if appartments_year2_may is None:
		appartments_year2_may = 0
	if appartments_year2_jun is None:
		appartments_year2_jun = 0
	if appartments_year2_jul is None:
		appartments_year2_jul = 0
	if appartments_year2_aug is None:
		appartments_year2_aug = 0
	if appartments_year2_sep is None:
		appartments_year2_sep = 0
	if appartments_year2_oct is None:
		appartments_year2_oct = 0
	if appartments_year2_nov is None:
		appartments_year2_nov = 0
	if appartments_year2_dec is None:
		appartments_year2_dec = 0

	if appartments_year3 is None:
		appartments_year3 = 0
	if appartments_year3_jan is None:
		appartments_year3_jan = 0
	if appartments_year3_feb is None:
		appartments_year3_feb = 0
	if appartments_year3_mar is None:
		appartments_year3_mar = 0
	if appartments_year3_apr is None:
		appartments_year3_apr = 0
	if appartments_year3_may is None:
		appartments_year3_may = 0
	if appartments_year3_jun is None:
		appartments_year3_jun = 0
	if appartments_year3_jul is None:
		appartments_year3_jul = 0
	if appartments_year3_aug is None:
		appartments_year3_aug = 0
	if appartments_year3_sep is None:
		appartments_year3_sep = 0
	if appartments_year3_oct is None:
		appartments_year3_oct = 0
	if appartments_year3_nov is None:
		appartments_year3_nov = 0
	if appartments_year3_dec is None:
		appartments_year3_dec = 0

	if other_year1 is None:
		other_year1 = 0
	if other_year1_jan is None:
		other_year1_jan = 0
	if other_year1_feb is None:
		other_year1_feb = 0
	if other_year1_mar is None:
		other_year1_mar = 0
	if other_year1_apr is None:
		other_year1_apr = 0
	if other_year1_may is None:
		other_year1_may = 0
	if other_year1_jun is None:
		other_year1_jun = 0
	if other_year1_jul is None:
		other_year1_jul = 0
	if other_year1_aug is None:
		other_year1_aug = 0
	if other_year1_sep is None:
		other_year1_sep = 0
	if other_year1_oct is None:
		other_year1_oct = 0
	if other_year1_nov is None:
		other_year1_nov = 0
	if other_year1_dec is None:
		other_year1_dec = 0

	if other_year2 is None:
		other_year2 = 0
	if other_year2_jan is None:
		other_year2_jan = 0
	if other_year2_feb is None:
		other_year2_feb = 0
	if other_year2_mar is None:
		other_year2_mar = 0
	if other_year2_apr is None:
		other_year2_apr = 0
	if other_year2_may is None:
		other_year2_may = 0
	if other_year2_jun is None:
		other_year2_jun = 0
	if other_year2_jul is None:
		other_year2_jul = 0
	if other_year2_aug is None:
		other_year2_aug = 0
	if other_year2_sep is None:
		other_year2_sep = 0
	if other_year2_oct is None:
		other_year2_oct = 0
	if other_year2_nov is None:
		other_year2_nov = 0
	if other_year2_dec is None:
		other_year2_dec = 0

	if other_year3 is None:
		other_year3 = 0
	if other_year3_jan is None:
		other_year3_jan = 0
	if other_year3_feb is None:
		other_year3_feb = 0
	if other_year3_mar is None:
		other_year3_mar = 0
	if other_year3_apr is None:
		other_year3_apr = 0
	if other_year3_may is None:
		other_year3_may = 0
	if other_year3_jun is None:
		other_year3_jun = 0
	if other_year3_jul is None:
		other_year3_jul = 0
	if other_year3_aug is None:
		other_year3_aug = 0
	if other_year3_sep is None:
		other_year3_sep = 0
	if other_year3_oct is None:
		other_year3_oct = 0
	if other_year3_nov is None:
		other_year3_nov = 0
	if other_year3_dec is None:
		other_year3_dec = 0

	if expenses_year1 is None:
		expenses_year1 = 0
	if expenses_year1_jan is None:
		expenses_year1_jan = 0
	if expenses_year1_feb is None:
		expenses_year1_feb = 0
	if expenses_year1_mar is None:
		expenses_year1_mar = 0
	if expenses_year1_apr is None:
		expenses_year1_apr = 0
	if expenses_year1_may is None:
		expenses_year1_may = 0
	if expenses_year1_jun is None:
		expenses_year1_jun = 0
	if expenses_year1_jul is None:
		expenses_year1_jul = 0
	if expenses_year1_aug is None:
		expenses_year1_aug = 0
	if expenses_year1_sep is None:
		expenses_year1_sep = 0
	if expenses_year1_oct is None:
		expenses_year1_oct = 0
	if expenses_year1_nov is None:
		expenses_year1_nov = 0
	if expenses_year1_dec is None:
		expenses_year1_dec = 0

	if expenses_year2 is None:
		expenses_year2 = 0
	if expenses_year2_jan is None:
		expenses_year2_jan = 0
	if expenses_year2_feb is None:
		expenses_year2_feb = 0
	if expenses_year2_mar is None:
		expenses_year2_mar = 0
	if expenses_year2_apr is None:
		expenses_year2_apr = 0
	if expenses_year2_may is None:
		expenses_year2_may = 0
	if expenses_year2_jun is None:
		expenses_year2_jun = 0
	if expenses_year2_jul is None:
		expenses_year2_jul = 0
	if expenses_year2_aug is None:
		expenses_year2_aug = 0
	if expenses_year2_sep is None:
		expenses_year2_sep = 0
	if expenses_year2_oct is None:
		expenses_year2_oct = 0
	if expenses_year2_nov is None:
		expenses_year2_nov = 0
	if expenses_year2_dec is None:
		expenses_year2_dec = 0

	if expenses_year3 is None:
		expenses_year3 = 0
	if expenses_year3_jan is None:
		expenses_year3_jan = 0
	if expenses_year3_feb is None:
		expenses_year3_feb = 0
	if expenses_year3_mar is None:
		expenses_year3_mar = 0
	if expenses_year3_apr is None:
		expenses_year3_apr = 0
	if expenses_year3_may is None:
		expenses_year3_may = 0
	if expenses_year3_jun is None:
		expenses_year3_jun = 0
	if expenses_year3_jul is None:
		expenses_year3_jul = 0
	if expenses_year3_aug is None:
		expenses_year3_aug = 0
	if expenses_year3_sep is None:
		expenses_year3_sep = 0
	if expenses_year3_oct is None:
		expenses_year3_oct = 0
	if expenses_year3_nov is None:
		expenses_year3_nov = 0
	if expenses_year3_dec is None:
		expenses_year3_dec = 0

	if salaries_year1 is None:
		salaries_year1 = 0
	if salaries_year1_jan is None:
		salaries_year1_jan = 0
	if salaries_year1_feb is None:
		salaries_year1_feb = 0
	if salaries_year1_mar is None:
		salaries_year1_mar = 0
	if salaries_year1_apr is None:
		salaries_year1_apr = 0
	if salaries_year1_may is None:
		salaries_year1_may = 0
	if salaries_year1_jun is None:
		salaries_year1_jun = 0
	if salaries_year1_jul is None:
		salaries_year1_jul = 0
	if salaries_year1_aug is None:
		salaries_year1_aug = 0
	if salaries_year1_sep is None:
		salaries_year1_sep = 0
	if salaries_year1_oct is None:
		salaries_year1_oct = 0
	if salaries_year1_nov is None:
		salaries_year1_nov = 0
	if salaries_year1_dec is None:
		salaries_year1_dec = 0

	if salaries_year2 is None:
		salaries_year2 = 0
	if salaries_year2_jan is None:
		salaries_year2_jan = 0
	if salaries_year2_feb is None:
		salaries_year2_feb = 0
	if salaries_year2_mar is None:
		salaries_year2_mar = 0
	if salaries_year2_apr is None:
		salaries_year2_apr = 0
	if salaries_year2_may is None:
		salaries_year2_may = 0
	if salaries_year2_jun is None:
		salaries_year2_jun = 0
	if salaries_year2_jul is None:
		salaries_year2_jul = 0
	if salaries_year2_aug is None:
		salaries_year2_aug = 0
	if salaries_year2_sep is None:
		salaries_year2_sep = 0
	if salaries_year2_oct is None:
		salaries_year2_oct = 0
	if salaries_year2_nov is None:
		salaries_year2_nov = 0
	if salaries_year2_dec is None:
		salaries_year2_dec = 0

	if salaries_year3 is None:
		salaries_year3 = 0
	if salaries_year3_jan is None:
		salaries_year3_jan = 0
	if salaries_year3_feb is None:
		salaries_year3_feb = 0
	if salaries_year3_mar is None:
		salaries_year3_mar = 0
	if salaries_year3_apr is None:
		salaries_year3_apr = 0
	if salaries_year3_may is None:
		salaries_year3_may = 0
	if salaries_year3_jun is None:
		salaries_year3_jun = 0
	if salaries_year3_jul is None:
		salaries_year3_jul = 0
	if salaries_year3_aug is None:
		salaries_year3_aug = 0
	if salaries_year3_sep is None:
		salaries_year3_sep = 0
	if salaries_year3_oct is None:
		salaries_year3_oct = 0
	if salaries_year3_nov is None:
		salaries_year3_nov = 0
	if salaries_year3_dec is None:
		salaries_year3_dec = 0


	income_year1 = appartments_year1 + other_year1
	income_year1_jan = appartments_year1_jan + other_year1_jan
	income_year1_feb = appartments_year1_feb + other_year1_feb
	income_year1_mar = appartments_year1_mar + other_year1_mar
	income_year1_apr = appartments_year1_apr + other_year1_apr
	income_year1_may = appartments_year1_may + other_year1_may
	income_year1_jun = appartments_year1_jun + other_year1_jun
	income_year1_jul = appartments_year1_jul + other_year1_jul
	income_year1_aug = appartments_year1_aug + other_year1_aug
	income_year1_sep = appartments_year1_sep + other_year1_sep
	income_year1_oct = appartments_year1_oct + other_year1_oct
	income_year1_nov = appartments_year1_nov + other_year1_nov
	income_year1_dec = appartments_year1_dec + other_year1_dec

	income_year2 = appartments_year2 + other_year2
	income_year2_jan = appartments_year2_jan + other_year2_jan
	income_year2_feb = appartments_year2_feb + other_year2_feb
	income_year2_mar = appartments_year2_mar + other_year2_mar
	income_year2_apr = appartments_year2_apr + other_year2_apr
	income_year2_may = appartments_year2_may + other_year2_may
	income_year2_jun = appartments_year2_jun + other_year2_jun
	income_year2_jul = appartments_year2_jul + other_year2_jul
	income_year2_aug = appartments_year2_aug + other_year2_aug
	income_year2_sep = appartments_year2_sep + other_year2_sep
	income_year2_oct = appartments_year2_oct + other_year2_oct
	income_year2_nov = appartments_year2_nov + other_year2_nov
	income_year2_dec = appartments_year2_dec + other_year2_dec

	income_year3 = appartments_year3 + other_year3
	income_year3_jan = appartments_year3_jan + other_year3_jan
	income_year3_feb = appartments_year3_feb + other_year3_feb
	income_year3_mar = appartments_year3_mar + other_year3_mar
	income_year3_apr = appartments_year3_apr + other_year3_apr
	income_year3_may = appartments_year3_may + other_year3_may
	income_year3_jun = appartments_year3_jun + other_year3_jun
	income_year3_jul = appartments_year3_jul + other_year3_jul
	income_year3_aug = appartments_year3_aug + other_year3_aug
	income_year3_sep = appartments_year3_sep + other_year3_sep
	income_year3_oct = appartments_year3_oct + other_year3_oct
	income_year3_nov = appartments_year3_nov + other_year3_nov
	income_year3_dec = appartments_year3_dec + other_year3_dec

	results_year1 = income_year1 - (expenses_year1 + salaries_year1)
	results_year1_jan = income_year1_jan - expenses_year1_jan
	results_year1_feb = income_year1_feb - expenses_year1_feb
	results_year1_mar = income_year1_mar - expenses_year1_mar
	results_year1_apr = income_year1_apr - expenses_year1_apr
	results_year1_may = income_year1_may - expenses_year1_may
	results_year1_jun = income_year1_jun - expenses_year1_jun
	results_year1_jul = income_year1_jul - expenses_year1_jul
	results_year1_aug = income_year1_aug - expenses_year1_aug
	results_year1_sep = income_year1_sep - expenses_year1_sep
	results_year1_oct = income_year1_oct - expenses_year1_oct
	results_year1_nov = income_year1_nov - expenses_year1_nov
	results_year1_dec = income_year1_dec - expenses_year1_dec

	results_year2 = income_year2 - (expenses_year2 + salaries_year2)
	#results_year2_jan = income_year2_jan - expenses_year2_jan
	#results_year2_feb = income_year2_feb - expenses_year2_feb
	#results_year2_mar = income_year2_mar - expenses_year2_mar
	#results_year2_apr = income_year2_apr - expenses_year2_apr
	#results_year2_may = income_year2_may - expenses_year2_may
	#results_year2_jun = income_year2_jun - expenses_year2_jun
	#results_year2_jul = income_year2_jul - expenses_year2_jul
	#results_year2_aug = income_year2_aug - expenses_year2_aug
	#results_year2_sep = income_year2_sep - expenses_year2_sep
	#results_year2_oct = income_year2_oct - expenses_year2_oct
	#results_year2_nov = income_year2_nov - expenses_year2_nov
	#results_year2_dec = income_year2_dec - expenses_year2_dec

	results_year3 = income_year3 - (expenses_year3 + salaries_year3)
	#results_year3_jan = income_year3_jan - expenses_year3_jan
	#results_year3_feb = income_year3_feb - expenses_year3_feb
	#results_year3_mar = income_year3_mar - expenses_year3_mar
	#results_year3_apr = income_year3_apr - expenses_year3_apr
	#results_year3_may = income_year3_may - expenses_year3_may
	#results_year3_jun = income_year3_jun - expenses_year3_jun
	#results_year3_jul = income_year3_jul - expenses_year3_jul
	#results_year3_aug = income_year3_aug - expenses_year3_aug
	#results_year3_sep = income_year3_sep - expenses_year3_sep
	#results_year3_oct = income_year3_oct - expenses_year3_oct
	#results_year3_nov = income_year3_nov - expenses_year3_nov
	#results_year3_dec = income_year3_dec - expenses_year3_dec

	context = {
		'income_year1': income_year1,
		'income_year1_jan': income_year1_jan,
		'income_year1_feb': income_year1_feb,
		'income_year1_mar': income_year1_mar,
		'income_year1_apr': income_year1_apr,
		'income_year1_may': income_year1_may,
		'income_year1_jun': income_year1_jun,
		'income_year1_jul': income_year1_jul,
		'income_year1_aug': income_year1_aug,
		'income_year1_sep': income_year1_sep,
		'income_year1_oct': income_year1_oct,
		'income_year1_nov': income_year1_nov,
		'income_year1_dec': income_year1_dec,
		'income_year2': income_year2,
		'income_year2_jan': income_year2_jan,
		'income_year2_feb': income_year2_feb,
		'income_year2_mar': income_year2_mar,
		'income_year2_apr': income_year2_apr,
		'income_year2_may': income_year2_may,
		'income_year2_jun': income_year2_jun,
		'income_year2_jul': income_year2_jul,
		'income_year2_aug': income_year2_aug,
		'income_year2_sep': income_year2_sep,
		'income_year2_oct': income_year2_oct,
		'income_year2_nov': income_year2_nov,
		'income_year2_dec': income_year2_dec,
		'income_year3': income_year3,
		'income_year3_jan': income_year3_jan,
		'income_year3_feb': income_year3_feb,
		'income_year3_mar': income_year3_mar,
		'income_year3_apr': income_year3_apr,
		'income_year3_may': income_year3_may,
		'income_year3_jun': income_year3_jun,
		'income_year3_jul': income_year3_jul,
		'income_year3_aug': income_year3_aug,
		'income_year3_sep': income_year3_sep,
		'income_year3_oct': income_year3_oct,
		'income_year3_nov': income_year3_nov,
		'income_year3_dec': income_year3_dec,
		'expenses_year1': expenses_year1 + salaries_year1,
		'expenses_year1_jan': expenses_year1_jan + salaries_year1_jan,
		'expenses_year1_feb': expenses_year1_feb + salaries_year1_feb,
		'expenses_year1_mar': expenses_year1_mar + salaries_year1_mar,
		'expenses_year1_apr': expenses_year1_apr + salaries_year1_apr,
		'expenses_year1_may': expenses_year1_may + salaries_year1_may,
		'expenses_year1_jun': expenses_year1_jun + salaries_year1_jun,
		'expenses_year1_jul': expenses_year1_jul + salaries_year1_jul,
		'expenses_year1_aug': expenses_year1_aug + salaries_year1_aug,
		'expenses_year1_sep': expenses_year1_sep + salaries_year1_sep,
		'expenses_year1_oct': expenses_year1_oct + salaries_year1_oct,
		'expenses_year1_nov': expenses_year1_nov + salaries_year1_nov,
		'expenses_year1_dec': expenses_year1_dec + salaries_year1_dec,
		'expenses_year2': expenses_year2 + salaries_year2,
		'expenses_year2_jan': expenses_year2_jan + salaries_year2_jan,
		'expenses_year2_feb': expenses_year2_feb + salaries_year2_feb,
		'expenses_year2_mar': expenses_year2_mar + salaries_year2_mar,
		'expenses_year2_apr': expenses_year2_apr + salaries_year2_apr,
		'expenses_year2_may': expenses_year2_may + salaries_year2_may,
		'expenses_year2_jun': expenses_year2_jun + salaries_year2_jun,
		'expenses_year2_jul': expenses_year2_jul + salaries_year2_jul,
		'expenses_year2_aug': expenses_year2_aug + salaries_year2_aug,
		'expenses_year2_sep': expenses_year2_sep + salaries_year2_sep,
		'expenses_year2_oct': expenses_year2_oct + salaries_year2_oct,
		'expenses_year2_nov': expenses_year2_nov + salaries_year2_nov,
		'expenses_year2_dec': expenses_year2_dec + salaries_year2_dec,
		'expenses_year3': expenses_year3 + salaries_year3,
		'expenses_year3_jan': expenses_year3_jan + salaries_year3_jan,
		'expenses_year3_feb': expenses_year3_feb + salaries_year3_feb,
		'expenses_year3_mar': expenses_year3_mar + salaries_year3_mar,
		'expenses_year3_apr': expenses_year3_apr + salaries_year3_apr,
		'expenses_year3_may': expenses_year3_may + salaries_year3_may,
		'expenses_year3_jun': expenses_year3_jun + salaries_year3_jun,
		'expenses_year3_jul': expenses_year3_jul + salaries_year3_jul,
		'expenses_year3_aug': expenses_year3_aug + salaries_year3_aug,
		'expenses_year3_sep': expenses_year3_sep + salaries_year3_sep,
		'expenses_year3_oct': expenses_year3_oct + salaries_year3_oct,
		'expenses_year3_nov': expenses_year3_nov + salaries_year3_nov,
		'expenses_year3_dec': expenses_year3_dec + salaries_year3_dec,
		'results_year1': results_year1,
		'results_year2': results_year2,
		'results_year3': results_year3,
		#'results_year3_jan': results_year3_jan,
		#'results_year3_feb': results_year3_feb,
		#'results_year3_mar': results_year3_mar,
		#'results_year3_apr': results_year3_apr,
		#'results_year3_may': results_year3_may,
		#'results_year3_jun': results_year3_jun,
		#'results_year3_jul': results_year3_jul,
		#'results_year3_aug': results_year3_aug,
		#'results_year3_sep': results_year3_sep,
		#'results_year3_oct': results_year3_oct,
		#'results_year3_nov': results_year3_nov,
		#'results_year3_dec': results_year3_dec,
		'year1': str(year1),
		'year2': str(year2),
		'year3': str(year3),
		'ent': ent,
	}

	return render(request, "results.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def enterprise(request):
	today = datetime.now().date()
	lifetime = today + timedelta(days=36000)
	warning = False
	if request.exp is None:
		request.exp = today + timedelta(days=trial_days)
	warning_period = request.exp - timedelta(days=warning_days)

	if today > warning_period and today < request.exp:
		warning = True

	exp = request.exp
	exp = exp.strftime('%d/%m/%Y')

	item = None
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	exp = request.exp
	exp_2 = exp.strftime('%d/%m/%Y à %H:%M')

	context = {
		'ent': ent,
		'today': today,
		'lifetime': lifetime,
		'exp': exp,
		'exp_2': exp_2,
		#'version': imart_version,
		'warning': warning
	}
	return render(request, "enterprise.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def enterprise_mod(request, id):
	item = get_object_or_404(Enterprise, id=1)

	if request.method == 'POST':
		e_form = EnterpriseForm(request.POST, instance = item)
		l_form = LogoForm(request.POST, request.FILES, instance = item)
		if e_form.is_valid() and l_form.is_valid():
			e_form.save()
			l_form.save()
			messages.success(request, f'Informations modifiées avec succès!')
			return redirect('enterprise')

	else:
		e_form = EnterpriseForm(instance = item)
		l_form = LogoForm(instance = item)

		context = {
			'e_form': e_form,
			'l_form': l_form,
			#'version': imart_version,
		}

		return render(request, 'entreprise_mod.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'agent'])
def users(request):
	items = Profile.objects.all().order_by('user')
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)

	context = {
		'items': items,
		#'version': imart_version,
		'ent': ent
	}
	return render(request, "users.html", context)