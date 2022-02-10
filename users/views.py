from django.shortcuts import render, redirect
from .forms import UserRegisterForm, LoginForm
from django.contrib.auth import views as auth_views


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html',{ 'form' : form })

class LoginView(auth_views.LoginView):
    form_class = LoginForm

class LogoutView(auth_views.LogoutView):
    next_page = '/login/'
