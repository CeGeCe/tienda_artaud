from django.contrib import admin
from .models import Articulo

# Register your models here.


@admin.action(description='✅ Aprobar artículos seleccionados')
def aprobar_articulos(modeladmin, request, queryset):
    queryset.update(aprobado=True)

@admin.action(description='❌ Desaprobar artículos seleccionados')
def desaprobar_articulos(modeladmin, request, queryset):
    queryset.update(aprobado=False)

class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha_publicacion', 'aprobado')
    list_filter = ('aprobado', 'categoria', 'fecha_publicacion')
    search_fields = ('titulo', 'cuerpo', 'autor__username')
    actions = [aprobar_articulos, desaprobar_articulos]
    
    # Campos que se ven al editar
    fields = ('aprobado', 'titulo', 'categoria', 'cuerpo', 'autor')
    readonly_fields = ('fecha_publicacion', 'fecha_actualizacion')

admin.site.register(Articulo, ArticuloAdmin)