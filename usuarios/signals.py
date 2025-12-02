# usuarios/signals.py
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.conf import settings
import threading


# Clase para encapsular la tarea del hilo (más limpio que usar lambdas)
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list, from_email):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.from_email = from_email
        threading.Thread.__init__(self)

    def run(self):
        # La lógica de envío real
        send_mail(
            self.subject,
            self.message,
            self.from_email,
            self.recipient_list,
            # Importante: Si el hilo falla, que no rompa el hilo principal (fail_silently=True)
            fail_silently=True, 
        )


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
    
    # En lugar de enviar, iniciamos el hilo
    EmailThread(
        asunto,
        mensaje,
        [user.email],
        settings.DEFAULT_FROM_EMAIL
    ).start()
    
    print(f"📧 Tarea de Email de bienvenida para {user.email} enviada a hilo.")