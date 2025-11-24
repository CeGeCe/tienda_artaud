from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm

# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm # Form Personalizado (En español)
    success_url = reverse_lazy('login') # Redirige al usuario a la página de login después del registro
    template_name = 'account/signup.html'