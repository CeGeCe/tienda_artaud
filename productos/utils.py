from PIL import Image
import zxingcpp

def decodificar_imagen(image_file):
    """
    Recibe un archivo de imagen, lo abre con Pillow
    y lee códigos de barras usando zxing-cpp.
    """
    try:
        img = Image.open(image_file)
        
        # zxingcpp puede leer directamente objetos de Pillow
        resultados = zxingcpp.read_barcodes(img)
        
        if resultados:
            # Devuelve el texto del primer código encontrado
            return resultados[0].text
            
    except Exception as e:
        print(f"Error al leer código de barras: {e}")
    
    return None