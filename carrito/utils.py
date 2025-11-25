from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_pdf(template_src, context_dict):
    """
    Función auxiliar para generar un archivo PDF en memoria.
    Devuelve el contenido en bytes si es exitoso, o None si falla.
    """
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    
    # Generar PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None