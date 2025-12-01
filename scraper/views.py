from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .utils import scrapear_libros, scrapear_jedbangers
import threading

# Create your views here.


def buscar_libros(request):
    resultados = []
    busqueda = ''
    
    if request.method == 'POST':
        if 'buscar' in request.POST:
            # SCRAPEAR
            busqueda = request.POST.get('termino')
            if busqueda:
                resultados = scrapear_libros(busqueda)
                if not resultados:
                    messages.warning(request, "No se encontraron libros que contengan '{busqueda}'.")
        
        elif 'enviar_email' in request.POST:
            # Recuperar los datos "crudos" que pasamos como strings ocultos (truco rápido)
            # O idealmente, volver a scrapear o guardar en sesión. 
            # Por cuestiones educativas, se vuelve a scrapear rápido:
            busqueda = request.POST.get('termino_hidden')
            email_destino = request.POST.get('email_destino')
            
            resultados = scrapear_libros(busqueda) # Re-scrapear para enviar lo fresco
            
            if resultados:
                cuerpo_mensaje = f"Libros encontrados para '{busqueda}':\n\n"
                for item in resultados:
                    cuerpo_mensaje += f"- {item['titulo']}: {item['precio']} ({item['stock']})\n"
                
                send_mail(
                    f'Resultados de Scraping: {busqueda}',
                    cuerpo_mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [email_destino],
                    fail_silently=False,
                )
                messages.success(request, f"Resultados enviados a {email_destino}")
                return redirect('scraper_libros')

    return render(request, 'scraper/scraper_libros.html', {'resultados': resultados, 'busqueda': busqueda})


def buscar_discos(request):
    resultados = []
    busqueda = ''
    
    if request.method == 'POST':
        if 'buscar' in request.POST:
            busqueda = request.POST.get('termino')
            if busqueda:
                # ⚠️ Llamamos a la nueva función
                resultados = scrapear_jedbangers(busqueda)
                
                if not resultados:
                    messages.warning(request, f"No se encontraron resultados en Jedbangers para '{busqueda}'.")
        
        elif 'enviar_email' in request.POST:
            # Recuperar los datos "crudos" que pasamos como strings ocultos (truco rápido)
            # O idealmente, volver a scrapear o guardar en sesión. 
            # Por cuestiones educativas, se vuelve a scrapear rápido:
            busqueda = request.POST.get('termino_hidden')
            email_destino = request.POST.get('email_destino')
            
            resultados = scrapear_jedbangers(busqueda) # Re-scrapear para enviar lo fresco
            
            if resultados:
                cuerpo_mensaje = f"Items encontrados para '{busqueda}':\n\n"
                for item in resultados:
                    cuerpo_mensaje += f"- {item['titulo']}: {item['precio']}\n"
                
                # Definir el envío como una función interna o usar lambda
                # Pero lo más limpio es usar threading directo con la función send_mail

                email_thread = threading.Thread(
                    target=send_mail,
                    args=(
                        f'Resultados de Scraping: {busqueda}', # Asunto
                        cuerpo_mensaje,                         # Mensaje
                        settings.DEFAULT_FROM_EMAIL,            # De
                        [email_destino],                        # Para
                    ),
                    kwargs={'fail_silently': True} # Importante: Si falla en el hilo, que no rompa nada
                )

                # Iniciar el envío en paralelo
                email_thread.start()

                # Responder al usuario INMEDIATAMENTE, sin esperar a Gmail
                messages.success(request, f"El envío está en proceso hacia {email_destino}")
                return redirect('scraper_jeds')

    return render(request, 'scraper/scraper_jeds.html', {'resultados': resultados, 'busqueda': busqueda})