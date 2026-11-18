from django.contrib import admin

from .models import (Alerta, Atributo, Capitulo, EventoTrama, EventoUso, Ficha, Nota, Perfil, Proyecto, Relacion,
                     Termino)


class CapituloInline(admin.TabularInline):
    model = Capitulo
    fields = ("orden", "titulo", "palabras", "actualizado")
    readonly_fields = ("palabras", "actualizado")
    extra = 0


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "dueno", "genero", "es_plantilla", "actualizado")
    list_filter = ("genero", "es_plantilla")
    search_fields = ("titulo", "dueno__username")
    inlines = [CapituloInline]


@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ("titulo", "proyecto", "orden", "palabras", "actualizado")
    search_fields = ("titulo", "proyecto__titulo")


class AtributoInline(admin.TabularInline):
    model = Atributo
    extra = 1


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "proyecto")
    list_filter = ("tipo",)
    search_fields = ("nombre", "terminos")
    readonly_fields = ("terminos",)
    inlines = [AtributoInline]


@admin.register(Termino)
class TerminoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "proyecto")
    search_fields = ("nombre", "definicion")
    readonly_fields = ("clave",)


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ("capitulo", "ficha", "estado", "creada")
    list_filter = ("estado",)


@admin.register(EventoUso)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "proyecto", "valor", "fecha")
    list_filter = ("tipo", "usuario")
    search_fields = ("usuario__username", "proyecto__titulo")
    date_hierarchy = "fecha"


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "onboarding_completado", "acepto_privacidad")


admin.site.site_header = "PlotNode · Administración"
admin.site.site_title = "PlotNode"


@admin.register(Relacion)
class RelacionAdmin(admin.ModelAdmin):
    list_display = ("origen", "destino", "categoria", "etiqueta", "proyecto")
    list_filter = ("categoria",)


@admin.register(EventoTrama)
class EventoTramaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "etapa", "proyecto", "capitulo")


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ("contenido", "tipo", "proyecto", "creada")
    list_filter = ("tipo",)
