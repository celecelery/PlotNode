"""Proyecto de muestra para quien se registra: un capítulo, dos fichas y una relación (MVE: «Iniciar»)."""
from ..models import Capitulo, Ficha, Proyecto, Relacion

TEXTO = (
    "<p>Ana se detuvo en mitad del puente. Abajo, el río llevaba la niebla hacia la torre, y el viento olía a ceniza.</p>"
    "<p>—No deberíamos estar aquí —dijo Lía, y le apretó la mano—. Dicen que la torre está vacía.</p>"
    "<p>Ana no respondió. Había visto una luz en la ventana más alta, justo donde nadie debía vivir.</p>"
)


def crear_proyecto_de_muestra(usuario):
    proyecto = Proyecto.objects.create(dueno=usuario, titulo="Mi primera historia (ejemplo)", es_plantilla=True)
    capitulo = Capitulo.objects.create(proyecto=proyecto, titulo="La llegada", orden=1, contenido=TEXTO)
    ana = Ficha.objects.create(proyecto=proyecto, nombre="Ana", alias=["la capitana"],
                               notas="Valiente y terca. No sabe nadar.",
                               datos={"edad": "30", "rol": "Protagonista"})
    lia = Ficha.objects.create(proyecto=proyecto, nombre="Lía", notas="Prudente. Siempre lleva un diario.")
    Relacion.objects.create(proyecto=proyecto, origen=ana, destino=lia, categoria=Relacion.Categoria.FAMILIA,
                            etiqueta="Hermanas", nota="Crecieron juntas en la torre")
    return capitulo
