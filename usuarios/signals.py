# usuarios/signals.py
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.conf import settings

@receiver(user_signed_up)
def enviar_email_bienvenida(request, user, **kwargs):
    """
    Se ejecuta automáticamente cuando alguien se registra 
    (ya sea por Google o formulario normal).
    """
    
    # Verifica si es un registro social (Google)
    sociallogin = kwargs.get('sociallogin')
    
    asunto = f'¡Bienvenido a Tienda Artaud, {user.username}!'
    
    mensaje = f"""
    Hola {user.first_name or user.username},
    
    ¡Estamos muy felices de que te hayas unido a nuestra comunidad de coleccionistas!
    
    En Tienda Artaud vas a encontrar esas joyas en formato físico que estabas buscando.
    
    ¿Qué podés hacer ahora?
    1. Completar tu perfil (dirección y teléfono) para agilizar compras.
    2. Explorar el catálogo.
    3. ¡Empezar a vender tu propia colección!
    
    Gracias por confiar en nosotros.
    
    Saludos,
    El equipo de Tienda Artaud.
    """
    
    # Enviamos el correo
    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"📧 Email de bienvenida enviado a {user.email}")
    except Exception as e:
        print(f"❌ Error enviando email de bienvenida: {e}")