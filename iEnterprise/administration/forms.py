from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from .models import *


paying_for = (	
	('Loyer', 'Loyer'),
	('Garantie locative', 'Garantie locative'),
	('Autre', 'Autre'),
	)


class AppartmentForm(forms.ModelForm):
	class Meta:
		model = Appartment
		fields = ('designation', 'description', 'appartment_type', 'rent', 'rent_A', 'rent_B', 'rent_C', 'unit')
		labels = {
			"appartment_type": "Type",
			"rent": "Loyer",
			"rent_A": "Loyer cat. A",
			"rent_B": "Loyer cat. B",
			"rent_C": "Loyer cat. C",
			"unit": "Unité"
		}


class PartnerForm(forms.ModelForm):
	class Meta:
		model = Partner
		fields = ('designation', 'description')


class TenantForm(forms.ModelForm):
	class Meta:
		model = Tenant
		fields = ('firstname', 'lastname', 'gender', 'email', 'phone', 'maritalstatus', 'children', 'occupation', 'company', 'id_card_type', 'id_card_number', 'category', 'isActive')
		labels = {
			"firstname": "Prénom",
			"lastname": "Nom",
			"gender": "Genre",
			"email": "E-mail",
			"phone": "Téléphone",
			"maritalstatus": "Etat civil",
			"company": "Entreprise",
			"id_card_type": "Type de carte",
			"id_card_number": "No. Carte",
			"id_card_scan": "Scan de la carte",
			"children": "Enfants",
			"category": "Categorie",
			"isActive": "Actif ?"
		}

class TenantIdForm(forms.ModelForm):
	class Meta:
		model = Tenant
		fields = ['id_card_scan']


class RentalContractForm(forms.Form):
	locataire = forms.ModelChoiceField(queryset=Tenant.objects.all().order_by('firstname'), required=True)
	appartement = forms.ModelChoiceField(queryset=Appartment.objects.filter(isAvailable=True).order_by('designation'), required=True)
	#loyer = forms.FloatField(required=False, min_value=0, initial=0, widget=forms.NumberInput())
	#garantie_locative = forms.FloatField(required=False, min_value=0, initial=0, widget=forms.NumberInput())
	date_début = forms.DateField(widget=AdminDateWidget())
	date_fin = forms.DateField(widget=AdminDateWidget())
	prochain_paiement = forms.DateField(widget=AdminDateWidget())


class RentalContractEditForm(forms.ModelForm):
	class Meta:
		model = RentalContract
		fields = ('tenant', 'appartment', 'rent', 'deposit', 'start_date', 'end_date', 'next_payment_on')
		labels = {
			"tenant": "Locataire",
			"appartement": "Appartement",
			"start_date": "Date début",
			"end_date": "Date fin",
			"next_payment_on": "Prochain paiement"
		}


class RentForm(forms.Form):
	locataire = forms.ModelChoiceField(queryset=Tenant.objects.filter(isActive=True, isTerminated=False).order_by('firstname'), required=True)
	appartement = forms.ModelChoiceField(queryset=Appartment.objects.filter(isAvailable=False).order_by('designation'), required=True)
	paiement_pour = forms.ChoiceField(required=True, widget=forms.RadioSelect(), choices=paying_for)
	compte = forms.ModelChoiceField(queryset=BankAccount.objects.filter(isClosed=False).order_by('account_name'))
	montant_payé = forms.FloatField(required=True, min_value=0, initial=0, widget=forms.NumberInput())
	nombre_de_mois = forms.IntegerField(required=True, min_value=1, initial=1, widget=forms.NumberInput())
	remise = forms.FloatField(required=False, min_value=0, initial=0, widget=forms.NumberInput())
	libéllé = forms.CharField(required=False, max_length=500, widget=forms.TextInput())
	

class RentEditForm(forms.ModelForm):
	class Meta:
		model = RentPayment
		fields = ['paid_amount']
		labels = {'paid_amount': 'Montant payé'}


class IncomeForm(forms.ModelForm):
	class Meta:
		model = Income
		fields = ('entreprise', 'description', 'amount', 'account')
		labels = {
			'description': 'Libéllé',
			'amount': 'Montant',
			}


class ExpenseForm(forms.ModelForm):
	class Meta:
		model = Disbursement
		fields = ('entreprise', 'description', 'amount', 'account')
		labels = {
			'description': 'Libéllé',
			'amount': 'Montant',
			}


class PositionForm(forms.ModelForm):
	class Meta:
		model = Position
		fields = ('designation', 'description', 'department', 'salary')
		labels = {
			"department": "Departement",
			"salary": "Salaire"
		}


class EmployeeForm(forms.ModelForm):
	class Meta:
		model = Employee
		fields = ('entreprise', 'firstname', 'lastname', 'gender', 'email', 'phone', 'maritalstatus', 'children', 'id_card_type', 'id_card_number')
		labels = {
			"firstname": "Prénom",
			"lastname": "Nom",
			"gender": "Genre",
			"email": "E-mail",
			"phone": "Téléphone",
			"maritalstatus": "Etat civil",
			"position": "Poste",
			"id_card_type": "Type de carte",
			"id_card_number": "No. Carte",
			"id_card_scan": "Scan de la carte",
			"children": "Enfants",
			"department": "Departement"
		}

class EmployeeIdForm(forms.ModelForm):
	class Meta:
		model = Employee
		fields = ['id_card_scan']


class WorkContractForm(forms.Form):
	travailleur = forms.ModelChoiceField(queryset=Employee.objects.all().order_by('firstname'), required=True)
	poste = forms.ModelChoiceField(queryset=Position.objects.filter(isAvailable=True).order_by('designation'), required=True)
	date_début = forms.DateField(widget=AdminDateWidget())
	date_fin = forms.DateField(widget=AdminDateWidget())
	

class WorkContractEditForm(forms.ModelForm):
	class Meta:
		model = WorkContract
		fields = ('employee', 'position', 'department', 'salary', 'start_date', 'end_date')
		labels = {
			"employee": "Employé",
			"position": "Poste",
			"department": "Departement",
			"salary": "Salaire",
			"start_date": "Date début",
			"end_date": "Date fin",
		}


class SalaryForm(forms.ModelForm):
	class Meta:
		model = Salary
		fields = ('employee', 'description', 'month', 'year', 'amount', 'account')
		labels = {
			"employee": "Salarié",
			"description": "Libéllé",
			"month": "Mois",
			"year": "Année",
			"amount": "Montant",
			"account": "Compte",
		}


class BankAccountForm(forms.ModelForm):
	class Meta:
		model = BankAccount
		fields = ('account_name', 'account_type', 'balance', 'bank_name', 'account_number', 'iban', 'swift', 'account_holder')
		labels = {
			"account_name": "Intitulé de compte",
			"account_type": "Type de compte",
			"balance": "Solde initial",
			"bank_name": "Nom de la banque",
			"account_number": "Numéro de compte",
			"iban": "Numéro IBAN",
			"swift": "Code BIC/SWIFT",
			"account_holder": "Nom du propriétaire du compte",
		}


class BankAccountEditForm(forms.ModelForm):
	class Meta:
		model = BankAccount
		fields = ('account_name', 'account_type', 'bank_name', 'account_number', 'iban', 'swift', 'account_holder')
		labels = {
			"account_name": "Intitulé de compte",
			"account_type": "Type de compte",
			"bank_name": "Nom de la banque",
			"account_number": "Numéro de compte",
			"iban": "Numéro IBAN",
			"swift": "Code BIC/SWIFT",
			"account_holder": "Nom du propriétaire du compte",
		}


class TransferForm(forms.Form):
	source = forms.ModelChoiceField(queryset=BankAccount.objects.filter(isClosed=False).order_by('account_name'), required=True)
	destination = forms.ModelChoiceField(queryset=BankAccount.objects.filter(isClosed=False).order_by('account_name'), required=True)
	montant = forms.FloatField(required=True, min_value=0, initial=0, widget=forms.NumberInput())
	libéllé = forms.CharField(required=False, max_length=500, widget=forms.TextInput())


class EnterpriseForm(forms.ModelForm):
	class Meta: 
		model = Enterprise
		fields = ('name', 'legal_form', 'phone', 'email', 'website', 'address', 'devise', 'capital', 'vat', 'impf', 'irl', 'identification', 'vat_number')
		labels = {
        "name": "Nom d'Entreprise",
        "legal_form": "Forme judirique",
        "phone": "Téléphone",
        "email": "E-mail",
        "address": "Adresse",
        "vat": "TVA %",
        "impf": "Impots fonciers en $",
        "irl": "Impots sur Revenus Locatifs en %",
        "identification": "ID National ou RCCM",
        "vat_number": "Numéro d'impot"
    	}


class LogoForm(forms.ModelForm):
	class Meta:
		model = Enterprise
		fields = ['logo']