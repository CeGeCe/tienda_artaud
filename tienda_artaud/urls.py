"""
URL configuration for tienda_artaud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Esto intercepta /accounts/login/ y usa el sistema nativo que sabemos que funciona.
    path('accounts/login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='account_login'),

    # URLs de autenticación de Django (login/logout)
    path('accounts/', include('allauth.urls')),
    
    # URLs para registro (signup) 
    path('accounts/', include('usuarios.urls')),

    path('', include('productos.urls')),

    path('carrito/', include('carrito.urls')),

    path('pedidos/', include('pedidos.urls')),

    path('blog/', include('blog.urls')),

    path('scraper/', include('scraper.urls')),
]

# **ÚNICAMENTE para desarrollo local**
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
