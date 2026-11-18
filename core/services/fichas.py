"""Búsqueda y serialización de fichas (HU-09, HU-10)."""
import re

from django.urls import reverse

from ..fichas_schema import secciones_con_datos
from ..utils import normalizar


RELACIONES_PRECARGA = ("atributos", "relaciones_salientes__destino", "relaciones_entrantes__origen")


def _relaciones_de(ficha):
    lista = [(r, r.destino) for r in ficha.relaciones_salientes.all()] + [(r, r.origen) for r in ficha.relaciones_entrantes.all()]
    return [{"id": r.pk, "con": otra.nombre, "con_id": otra.pk, "color": otra.color, "texto": r.texto, "nota": r.nota}
            for r, otra in sorted(lista, key=lambda par: par[0].pk)]


def ficha_a_dict(ficha):
    """Ficha -> dict listo para JSON. Usa los atributos precargados si los hay."""
    atributos = sorted(ficha.atributos.all(), key=lambda a: a.pk)
    return {
        "id": ficha.pk,
        "nombre": ficha.nombre,
        "tipo": ficha.get_tipo_display(),
        "tipo_clave": ficha.tipo,
        "foto": ficha.foto.url if ficha.foto else "",
        "secciones": secciones_con_datos(ficha.tipo, ficha.datos),
        "alias": list(ficha.alias or []),
        "notas": ficha.notas,
        "color": ficha.color,
        "inicial": ficha.inicial,
        "atributos": [{"clave": a.clave, "valor": a.valor} for a in atributos],
        "relaciones": _relaciones_de(ficha),
        "url_editar": reverse("ficha_editar", args=[ficha.proyecto_id, ficha.pk]),
        "url_relaciones": reverse("relaciones", args=[ficha.proyecto_id]) + f"?de={ficha.pk}",
    }


_PUNTUACION = re.compile(r"[^\w\s'’-]", re.UNICODE)


def _limpiar(texto):
    """Normaliza y quita comillas, signos y rayas sueltas: «"Ana," dijo» -> 'ana dijo'."""
    clave = normalizar(_PUNTUACION.sub(" ", texto or ""))
    return " ".join(p for p in clave.split() if p.strip("-—–"))


def buscar_ficha(proyecto, texto):
    """Ficha del proyecto cuyo nombre o alias coincide (sin mayúsculas, acentos ni signos), o None.

    1) Coincidencia exacta. 2) Si no hay, una coincidencia por palabra completa: seleccionar
    «Elena Marrón» o «la capitana Elena» encuentra a «Elena». Si varias fichas empatan, no adivina.
    """
    clave = _limpiar(texto)
    if not clave:
        return None
    fichas = list(proyecto.fichas.prefetch_related(*RELACIONES_PRECARGA))
    for ficha in fichas:
        if ficha.coincide(clave):
            return ficha
    palabras = clave.split()
    if len(palabras) > 6:        # una frase larga no es un nombre
        return None
    mejores, largo = [], 0
    for ficha in fichas:
        for termino in filter(None, ficha.terminos.split("|")):
            if len(termino) < 3:
                continue
            t = termino.split()
            if palabras[:len(t)] == t or palabras[-len(t):] == t:
                if len(termino) > largo:
                    mejores, largo = [ficha], len(termino)
                elif len(termino) == largo and ficha not in mejores:
                    mejores.append(ficha)
    return mejores[0] if len(mejores) == 1 else None   # gana el término más largo; si empatan, no adivina
