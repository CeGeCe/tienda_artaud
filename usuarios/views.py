from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, UserUpdateForm, PerfilUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Perfil
from django.contrib.auth.models import User
from productos.models import Producto
from blog.models import Articulo

# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm # Form Personalizado (En español)
    success_url = reverse_lazy('login') # Redirige al usuario a la página de login después del registro
    template_name = 'account/signup.html'


@login_required
def mi_perfil(request):
    # Intenta obtener el perfil. Si no existe, se crea automáticamente acá
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        # Instancia ambos formularios con los datos POST
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PerfilUpdateForm(request.POST, request.FILES, instance=request.user.perfil)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('mi_perfil') # Redirigir para evitar reenvío de formulario (PRG pattern)
    else:
        # Cargar datos existentes
        u_form = UserUpdateForm(instance=request.user)
        p_form = PerfilUpdateForm(instance=perfil)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'titulo_pagina': 'Mi Perfil'
    }
    return render(request, 'account/perfil.html', context)


def ver_vendedor(request, username):
    """Vista pública del perfil de un vendedor y sus aportes."""
    vendedor = get_object_or_404(User, username=username)
    
    # Obtener productos APROBADOS y con STOCK de ESTE vendedor
    productos = Producto.objects.filter(
        vendedor=vendedor, 
        aprobado=True, 
        stock__gt=0
    ).order_by('-id')
    
    # OBTENER ARTÍCULOS DE BLOG (Solo aprobados)
    articulos = Articulo.objects.filter(
        autor=vendedor,
        aprobado=True
    ).order_by('-fecha_publicacion')

    context = {
        'vendedor': vendedor,
        'productos': productos,
        'articulos': articulos,
        'titulo_pagina': f'Perfil de {vendedor.username}'
    }
    return render(request, 'account/ver_vendedor.html', context)