from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.db.models import Q
from .models import Articulo, CATEGORIA_CHOICES
from .forms import ArticuloForm
from django.contrib import messages

# Create your views here.


# Lista de Artículos (PÚBLICA)
def lista_articulos(request):
    # Filtrar solo los aprobados
    articulos = Articulo.objects.filter(aprobado=True)
    
    # Filtro por Categoría (opcional desde la URL)
    categoria = request.GET.get('categoria')
    if categoria:
        articulos = articulos.filter(categoria=categoria)
        
    # Búsqueda simple (opcional)
    query = request.GET.get('q')
    if query:
        articulos = articulos.filter(
            Q(titulo__icontains=query) | 
            Q(cuerpo__icontains=query) |
            Q(autor__username__icontains=query)
        )

    context = {
        'articulos': articulos,
        'categorias': CATEGORIA_CHOICES,
        'categoria_actual': categoria,
        'query_actual': query,
        'titulo_pagina': 'Blog de Tienda Artaud'
    }
    return render(request, 'blog/lista_articulos.html', context)


# Detalle de Artículo (PÚBLICA CON PROTECCIÓN)
def detalle_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    
    # Seguridad: Si no está aprobado, solo lo ve el autor o el admin
    if not articulo.aprobado:
        if request.user != articulo.autor and not request.user.is_staff:
            raise Http404("Este artículo no está disponible.")
            
    return render(request, 'blog/detalle_articulo.html', {'articulo': articulo})


# Crear Artículo (SOLO USUARIOS)
class CrearArticuloView(LoginRequiredMixin, CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'blog/crear_articulo.html'
    success_url = reverse_lazy('blog_lista') # Redirige a la lista tras publicar

    def form_valid(self, form):
        form.instance.autor = self.request.user
        
        # Auto-aprobación para admins
        if self.request.user.is_staff or self.request.user.is_superuser:
            form.instance.aprobado = True
            messages.success(self.request, "¡Tu artículo ha sido publicado!")
        else:
            form.instance.aprobado = False # Pendiente para usuarios normales
            messages.info(self.request, "Gracias por escribir. Tu artículo fue enviado y está pendiente de aprobación por un Admin.")

        return super().form_valid(form)


class EliminarArticuloView(UserPassesTestMixin, DeleteView):
    model = Articulo
    template_name = 'blog/articulo_confirm_delete.html'
    success_url = reverse_lazy('blog_lista')

    # Esta función define quién puede acceder a la vista
    def test_func(self):
        # Solo permite acceso si el usuario es Staff (Admin)
        return self.request.user.is_staff