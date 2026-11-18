"""Proyecto de muestra para quien se registra: un capítulo, dos fichas, una relación, un término del glosario y una nota (MVE: «Iniciar»)."""
from ..models import Capitulo, Ficha, Nota, Proyecto, Relacion, Termino

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
    Termino.objects.create(proyecto=proyecto, nombre="la torre", categoria="Lugar",
                           definicion="Edificio antiguo junto al río. Dicen que está vacío, pero hay una luz en su ventana más alta.")
    Nota.objects.create(proyecto=proyecto, contenido="¿Quién vive en la ventana más alta? Idea: es alguien de la familia de Ana.",
                        ficha=ana, capitulo=capitulo, x=40, y=40)
    return capitulo
