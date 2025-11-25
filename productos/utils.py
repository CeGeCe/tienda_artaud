from pyzbar.pyzbar import decode
from PIL import Image

def decodificar_imagen(image_file):
    """
    Recibe un archivo de imagen (en memoria), lo abre con Pillow y trata de leer códigos de barras o QR.
    Retorna el string del código o None.
    """
    try:
        img = Image.open(image_file)
        codigos = decode(img) # Devuelve una lista de códigos encontrados
        
        if codigos:
            # Devuelve el primer código encontrado
            return codigos[0].data.decode('utf-8') # .data viene en bytes, hay que decodificar a utf-8
    except Exception as e:
        print(f"Error al leer código de barras: {e}")
    
    return None