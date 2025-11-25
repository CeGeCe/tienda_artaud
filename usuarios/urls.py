from django.urls import path
from .views import SignUpView
from . import views

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),

    path('perfil/', views.mi_perfil, name='mi_perfil'),

    path('vendedor/<str:username>/', views.ver_vendedor, name='ver_vendedor'),
]