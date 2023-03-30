from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from administration.decorators import allowed_users
from .forms import UserUpdateForm, ProfileUpdateForm
from administration.models import Enterprise



#@login_required(login_url = 'login')
def userProfile(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance = request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.profile)
		
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Vos informations ont été modifiées !')
			return redirect('profile')

	else:
		u_form = UserUpdateForm(instance = request.user)
		p_form = ProfileUpdateForm(instance = request.user.profile)

	context = {
		'u_form': u_form,
		'p_form': p_form,
		'ent': ent
	}
	return render(request, "profile.html", context)



def userLogin(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)
	if request.user.is_authenticated:
		return redirect('dashboard')
	else:
		if request.method == "POST":
			login_name = request.POST.get('login_name')
			pass1 = request.POST.get('password')

			user = authenticate(request, username = login_name, password = pass1)
			if user is not None:
				login(request, user)
				return redirect('dashboard')
			else:
				messages.info(request, f'Nom d\'utilisateur ou mot de passe incorrect !')
				
				context = {
					'ent': ent
				}

				return render(request, 'login.html', context)

	context = {
		'ent': ent
	}

	return render(request, "login.html", context)

def userLogout(request):
	logout(request)
	return redirect('login')

#@allowed_users(allowed_roles=['admin'])
def userRegister(request):
	ent = None
	if Enterprise.objects.filter(id=1).exists():
		ent = Enterprise.objects.get(id=1)
	if request.method == "POST":
		uname = request.POST.get('username')
		email = request.POST.get('email')
		pass1 = request.POST.get('password1')
		pass2 = request.POST.get('password2')

		if User.objects.filter(username__iexact=uname):
			messages.info(request, f'Le nom d\'utilisateur {uname} est déjà pris ! Veuillez en choisir un autre.')
			return render(request, 'page-register.html')

		elif uname == "":
			messages.warning(request, f'Entrez le nom d\'utilisateur !')
			return render(request, 'page-register.html')

		elif pass1 == "":
			messages.warning(request, f'Entrez le mot de passe !')
			return render(request, 'page-register.html')

		elif pass1 != pass2:
			messages.warning(request, f'Les deux mots de passe ne correspondent pas !')
			return render(request, 'page-register.html')
		else:
			new_user = User.objects.create_user(uname, email, pass1)
			new_user.groups.add(Group.objects.get(name = 'agent'))
			messages.success(request, f'L\'utilisateur {uname} a été créé !')
			return redirect('users')

	context = {
		'ent': ent
	}
	return render(request, 'register.html', context)



