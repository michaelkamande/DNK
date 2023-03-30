from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from datetime import datetime
from PIL import Image


gender_choice = (
	('Homme','Homme'),
	('Femme','Femme'),
	)

category_choice = (
	('A','A'),
	('B','B'),
	('C','C'),
	)

ent_choice = (
	('DNK Appartements','DNK Appartements'),
	('DNK Génie civil','DNK Génie civil'),
	('DNK Ferme','DNK Ferme'),
	)

month_choice = (
	('Janvier','Janvier'),
	('Février','Février'),
	('Mars','Mars'),
	('Avril','Avril'),
	('Mai','Mai'),
	('Juin','Juin'),
	('Juillet','Juillet'),
	('Aout','Aout'),
	('Septembre','Septembre'),
	('Octobre','Octobre'),
	('Novembre','Novembre'),
	('Décembre','Décembre'),
	)


id_card_choice = (
	('Carte d\'électeur','Carte d\'électeur'),
	('Permis de conduire','Permis de conduire'),
	('Passeport','Passeport'),
	('Autre','Autre'),
	)

maritalstats_choice = (
	('Célibataire','Célibataire'),
	('Marié','Marié'),
	('Divorcé','Divorcé'),
	)

type_choice = (
	('Produit','Produit'),
	('Service','Service'),
	)

account_choice = (
	('Compte caisse/liquide','Compte caisse/liquide'),
	('Compte bancaire courant ou carte','Compte bancaire courant ou carte'),
	('Compte bancaire épargne','Compte bancaire épargne'),
	)

department_choice = (
	('Appartements','Appartements'),
	('Génie civil','Génie civil'),
	('Ferme','Ferme'),
	)

appartment_choice = (
	('Meublé','Meublé'),
	('Non-meublé','Non-meublé'),
	)

currencies = (
	('$','$'),
	('€','€'),
	('Fc','Fc'),
	('FCFA','FCFA'),
	)

invoice_type = (
	('A4','A4'),
	('88mm - Imprimante Thermique','88mm - Imprimante Thermique'),
	)

legal = (
	('Ets','Ets'),
	('SARL','SARL'),
	('SARLU','SARLU'),
	('SAS','SAS'),
	('SASU','SASU'),
	('SA','SA'),
	('',''),
	)

type_unit = (
	('Mois','Mois'),
	('Jour','Jour'),
	('Heure','Heure'),
	('pièce','pièce'),
	)


class Tag(models.Model):
	title = models.CharField(max_length=30, db_index=True)

	def __str__(self):
		return self.title


class Enterprise(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
	legal_form = models.CharField(max_length=100, blank=True, null=True, choices=legal, db_index=True)
	phone = models.CharField(max_length=20, blank=True, null=True, db_index=True)
	email = models.EmailField(blank=True, null=True, db_index=True)
	website = models.CharField(max_length=100, blank=True, null=True, db_index=True)
	address = models.CharField(max_length=100, blank=True, null=True, db_index=True)
	devise = models.CharField(default='$', max_length=5, blank=True, null=True, choices=currencies, db_index=True)
	format_facture = models.CharField(default='A4', max_length=30, blank=True, null=True, choices=invoice_type, db_index=True)
	vat = models.FloatField(default=0, blank=True, null=True, db_index=True)
	impf = models.FloatField(default=0, blank=True, null=True, db_index=True)
	irl = models.FloatField(default=0, blank=True, null=True, db_index=True)
	capital = models.FloatField(blank=True, null=True, db_index=True)
	identification = models.CharField(max_length=100, blank=True, null=True, db_index=True)
	vat_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
	logo = models.ImageField(default='logo.png', upload_to = 'logo', db_index=True)
	check_status = models.DateField(blank=True, null=True, db_index=True)

	def __str__(self):
		return f'{self.name}'

	def save(self):
		super().save()
		img = Image.open(self.logo.path)
		if img.height > 200 or img.width > 200:
			output_size = (200, 200)
			img.thumbnail(output_size)
			img.save(self.logo.path)


class Partner(models.Model):
	designation = models.CharField(max_length=100, db_index=True)
	description = models.CharField(max_length=500, blank=True, null=True, db_index=True)
	isTerminated = models.BooleanField(blank=False, null=False, default=False, db_index=True)
	
	def __str__(self):
		return f'{self.designation}'


class Tenant(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	category = models.CharField(max_length=1, blank=True, null=True, choices=category_choice, db_index=True)
	firstname = models.CharField(max_length=30, db_index=True)
	lastname = models.CharField(max_length=30, blank=True, null=True, db_index=True)
	gender = models.CharField(max_length=10, blank=True, null=True, choices=gender_choice, db_index=True)
	email = models.EmailField(null=True, blank=True, unique=True, db_index=True)
	phone = models.CharField(max_length=20, null=True, blank=True, unique=True, db_index=True)
	maritalstatus = models.CharField(max_length=15, blank=True, null=True, choices=maritalstats_choice, db_index=True)
	children = models.IntegerField(default=0, db_index=True)
	occupation = models.CharField(max_length=30, null=True, blank=True, db_index=True)
	company = models.CharField(max_length=30, null=True, blank=True, db_index=True)
	id_card_type = models.CharField(max_length=20, blank=True, null=True, choices=id_card_choice, db_index=True)
	id_card_number = models.CharField(max_length=30, null=True, blank=True, db_index=True)
	id_card_scan = models.ImageField(default = 'default-id.png', upload_to = 'id_cards', blank=True, null=True)
	isActive = models.BooleanField(blank=False, null=False, default=True, db_index=True)
	isTerminated = models.BooleanField(blank=False, null=False, default=False, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, db_index=True)
	
	def __str__(self):
		if self.lastname is None:
			return f'{self.firstname}'
		else:
			return f'{self.firstname}' + " " + f'{self.lastname}'

	def save(self, *args, **kwargs):
		super(Tenant, self).save(*args, **kwargs)

		img = Image.open(self.id_card_scan.path)

		if img:
			output_size = (600, 400)
			img.thumbnail(output_size)
			img.save(self.id_card_scan.path)


class Appartment(models.Model):
	designation = models.CharField(max_length=100, db_index=True)
	description = models.CharField(max_length=500, blank=True, null=True, db_index=True)
	appartment_type = models.CharField(max_length=20, blank=False, null=False, choices=appartment_choice, db_index=True)
	rent = models.FloatField(default=0, blank=True, null=True, db_index=True)
	rent_A = models.FloatField(default=0, blank=True, null=True, db_index=True)
	rent_B = models.FloatField(default=0, blank=True, null=True, db_index=True)
	rent_C = models.FloatField(default=0, blank=True, null=True, db_index=True)
	unit = models.CharField(max_length=20, choices=type_unit, default="Mois", db_index=True)
	isAvailable = models.BooleanField(blank=False, null=False, default=True, db_index=True)
	
	def __str__(self):
		return f'{self.designation}'


class RentalContract(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	appartment = models.ForeignKey(Appartment, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	rent = models.FloatField(default=0, blank=True, null=True, db_index=True)
	deposit = models.FloatField(default=0, blank=True, null=True, db_index=True)
	start_date = models.DateField(db_index=True)
	end_date = models.DateField(db_index=True)
	next_payment_on = models.DateField(db_index=True)
	isTerminated = models.BooleanField(blank=False, null=False, default=False, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, db_index=True)

	def __str__(self):
		return f'Contrat de bail pour : {self.tenant.firstname}' + " " + f'{self.tenant.lastname}'


class BankAccount(models.Model):
	account_name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
	account_type = models.CharField(max_length=100, blank=True, null=True, choices=account_choice, db_index=True)
	balance = models.FloatField(default=0, db_index=True)
	bank_name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
	account_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
	iban = models.CharField(max_length=50, blank=True, null=True, db_index=True)
	swift = models.CharField(max_length=10, blank=True, null=True, db_index=True)
	account_holder = models.CharField(max_length=100, blank=True, null=True, db_index=True)
	isClosed = models.BooleanField(blank=False, null=False, default=False, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True)

	def __str__(self):
		return self.account_name


class RentPayment(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	appartment = models.ForeignKey(Appartment, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	quantity = models.IntegerField(default=1, db_index=True)
	paying_for = models.CharField(max_length=10, blank=True, null=True, db_index=True)
	label = models.CharField(max_length=500, blank=True, null=True, db_index=True)
	due_amount = models.FloatField(default=0, db_index=True)
	discount = models.FloatField(default=0, db_index=True)
	paid_amount = models.FloatField(default=0, db_index=True)
	pending_payment = models.FloatField(default=0, db_index=True)
	cash = models.FloatField(default=0, db_index=True)
	change = models.FloatField(default=0, db_index=True)
	account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	isPaid = models.BooleanField(default=False, db_index=True)
	invoiced = models.BooleanField(blank=True, null=True, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, db_index=True)
	
	def __str__(self):
		return f'{self.appartment} | {self.quantity} Mois'


class Disbursement(models.Model):
	created_by = models.ForeignKey(User, on_delete = models.SET_NULL, blank=True, null=True, db_index=True)
	entreprise = models.CharField(max_length=100, choices=ent_choice, db_index=True)
	description = models.CharField(max_length=200, blank=True, null=True, db_index=True)
	amount = models.FloatField(default=0, db_index=True)
	account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	date_created = models.DateTimeField(auto_now_add = True, db_index=True)


class Income(models.Model):
	created_by = models.ForeignKey(User, on_delete = models.SET_NULL, blank=True, null=True, db_index=True)
	entreprise = models.CharField(max_length=100, choices=ent_choice, db_index=True)
	description = models.CharField(max_length=200, blank=True, null=True, db_index=True)
	amount = models.FloatField(default=0, db_index=True)
	account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	date_created = models.DateTimeField(auto_now_add = True, db_index=True)


class Position(models.Model):
	outsourcer = models.ForeignKey(Partner, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	designation = models.CharField(max_length=100, db_index=True)
	description = models.CharField(max_length=500, blank=True, null=True, db_index=True)
	department = models.CharField(max_length=50, blank=True, null=True, choices=department_choice, db_index=True)
	salary = models.FloatField(default=0, blank=True, null=True, db_index=True)
	isAvailable = models.BooleanField(blank=False, null=False, default=True, db_index=True)
	
	def __str__(self):
		return f'{self.designation}'


class Employee(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	entreprise = models.CharField(max_length=100, choices=ent_choice, db_index=True)
	firstname = models.CharField(max_length=30, db_index=True)
	lastname = models.CharField(max_length=30, blank=True, null=True, db_index=True)
	gender = models.CharField(max_length=10, blank=True, null=True, choices=gender_choice, db_index=True)
	email = models.EmailField(null=True, blank=True, unique=True, db_index=True)
	phone = models.CharField(max_length=20, null=True, blank=True, unique=True, db_index=True)
	maritalstatus = models.CharField(max_length=15, blank=True, null=True, choices=maritalstats_choice, db_index=True)
	children = models.IntegerField(default=0, db_index=True)
	id_card_type = models.CharField(max_length=20, blank=True, null=True, choices=id_card_choice, db_index=True)
	id_card_number = models.CharField(max_length=30, null=True, blank=True, db_index=True)
	id_card_scan = models.ImageField(default = 'default-id.png', upload_to = 'id_cards', blank=True, null=True)
	isTerminated = models.BooleanField(blank=False, null=False, default=False, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, db_index=True)
	
	def __str__(self):
		if self.lastname != None:
			return f'{self.firstname}' + " " + f'{self.lastname}'
		else:
			return f'{self.firstname}'

	def save(self, *args, **kwargs):
		super(Employee, self).save(*args, **kwargs)

		img = Image.open(self.id_card_scan.path)

		if img:
			output_size = (600, 400)
			img.thumbnail(output_size)
			img.save(self.id_card_scan.path)


class WorkContract(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	position = models.ForeignKey(Position, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	department = models.CharField(max_length=50, blank=True, null=True, db_index=True)
	salary = models.FloatField(default=0, blank=True, null=True, db_index=True)
	start_date = models.DateField(db_index=True)
	end_date = models.DateField(db_index=True)
	isTerminated = models.BooleanField(blank=False, null=False, default=False, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, db_index=True)

	def __str__(self):
		return f'Contrat de travail pour : {self.employee.firstname}' + " " + f'{self.employee.lastname}'


class Transfer(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	from_account = models.CharField(max_length=300, blank=True, null=True, db_index=True)
	to_account = models.CharField(max_length=300, blank=True, null=True, db_index=True)
	amount = models.FloatField(default=0, db_index=True)
	description = models.CharField(max_length=300, default='Virement interne', blank=True, null=True, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True)	 


class Salary(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	description = models.CharField(max_length=200, default='Paiement salaire', blank=True, null=True, db_index=True)
	month = models.CharField(max_length=20, choices=month_choice, db_index=True)
	year = models.IntegerField(default=datetime.now().year, db_index=True)
	amount = models.FloatField(default=0, db_index=True)
	account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
	date_created = models.DateTimeField(auto_now_add=True, db_index=True)

