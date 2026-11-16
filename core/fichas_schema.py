"""Campos de cada tipo de ficha (HU-25 y HU-08).

Los datos se guardan en `Ficha.datos` (JSON) con la clave de cada campo; así se pueden
agregar o cambiar campos sin migraciones. El formulario, el panel y las pruebas leen de aquí.
"""

CORTO, LARGO, ELEGIR = "corto", "largo", "elegir"

ROLES = ["Protagonista / Principal", "Antagonista", "Secundario", "Aliado", "Mentor", "Interés amoroso", "Otro"]
PAPELES = ["Héroe", "Villano", "Guía", "Aliado", "Rival", "Víctima", "Cómico", "Otro"]
ESTADOS_VIDA = ["Vivo", "Muerto", "Desaparecido", "Otro"]
ARCOS = ["Positivo (crece)", "Negativo (se corrompe)", "Plano (no cambia)", "Redención", "Caída"]


def c(clave, etiqueta, tipo=CORTO, ayuda="", opciones=None):
    return {"clave": clave, "etiqueta": etiqueta, "tipo": tipo, "ayuda": ayuda, "opciones": opciones or []}


SECCIONES = {
    "personaje": [
        {"titulo": "Esenciales", "abierta": True, "campos": [
            c("rol", "Rol", ELEGIR, opciones=ROLES),
            c("edad", "Edad", ayuda="Edad"),
            c("genero", "Género", ayuda="Género"),
            c("especie", "Especie", ayuda="Humano, elfo, vampiro…"),
            c("resumen", "Descripción breve", LARGO, "Quién es, en una o dos frases…"),
        ]},
        {"titulo": "Historia", "abierta": False, "campos": [
            c("papel", "Papel en la historia", ELEGIR, opciones=PAPELES),
            c("vivo", "¿Vivo o muerto?", ELEGIR, opciones=ESTADOS_VIDA),
            c("bando", "Bando o lealtad", ayuda="Casa, reino, gremio, banda, a quién es leal…"),
            c("arco", "Arco de personaje", ELEGIR, opciones=ARCOS),
            c("motivacion", "Motivación", LARGO, "¿Qué quiere conseguir?"),
            c("debilidad", "Debilidad / conflicto interno", LARGO, "¿Cuál es su punto débil?"),
            c("orientacion", "Orientación", ayuda="Si es relevante para la historia"),
            c("estado_civil", "Estado civil", ayuda="Soltero, casada, viudo…"),
            c("nacimiento", "Lugar / fecha de nacimiento", ayuda="Lugar o fecha…"),
            c("hijos", "Hijos", LARGO, "Cuántos, nombres, edades…"),
            c("trabajo", "Trabajo o estudios", LARGO, "En qué trabaja, o qué estudia y dónde…"),
        ]},
        {"titulo": "Más detalles", "abierta": False, "campos": [
            c("personalidad", "Personalidad", LARGO, "Cómo es, cómo trata a los demás, cómo reacciona…"),
            c("virtudes", "Virtudes", LARGO, "Lo mejor de este personaje…"),
            c("defectos", "Defectos", LARGO, "Manías, vicios, lo que le mete en problemas…"),
            c("fisica", "Descripción física", LARGO, "Complexión, rasgos, cicatrices…"),
            c("altura", "Altura", ayuda="En centímetros"),
            c("vestir", "Forma de vestir", LARGO, "Estilo, prendas habituales, colores…"),
            c("habilidades", "Habilidades", LARGO, "Qué se le da bien, poderes, oficios…"),
            c("salud", "Salud, alergias o enfermedades", LARGO, "Intolerancias, alergias, condiciones…"),
            c("hobbies", "Hobbies e intereses", LARGO, "Aficiones que puedan influir en la trama…"),
            c("habla", "Forma de hablar", LARGO, "Muletillas, acento, si habla poco, si trata de usted…"),
            c("miedo", "Su mayor miedo", LARGO, "Lo que no soportaría que pasara…"),
            c("secreto", "Secreto que oculta", LARGO, "Lo que nadie sabe, y qué pasaría si se supiera…"),
        ]},
    ],
    "lugar": [
        {"titulo": "Esenciales", "abierta": True, "campos": [
            c("tipo_lugar", "Tipo de lugar", ayuda="Ciudad, bosque, castillo, nave…"),
            c("ubicacion", "Ubicación", ayuda="Dónde queda, en el mapa de tu mundo"),
            c("descripcion", "Descripción", LARGO, "Cómo es a primera vista…"),
        ]},
        {"titulo": "Más detalles", "abierta": False, "campos": [
            c("ambiente", "Ambiente o clima", LARGO, "Clima, olores, sonidos, sensación…"),
            c("habitantes", "Habitantes", LARGO, "Quién vive o trabaja aquí…"),
            c("importancia", "Importancia en la historia", LARGO, "Qué pasa aquí y por qué importa…"),
            c("secretos_lugar", "Secretos del lugar", LARGO, "Pasadizos, leyendas, lo que está oculto…"),
        ]},
    ],
    "objeto": [
        {"titulo": "Esenciales", "abierta": True, "campos": [
            c("tipo_objeto", "Tipo de objeto", ayuda="Espada, orbe, varita, libro…"),
            c("duenio", "Dueño actual", ayuda="Quién lo tiene ahora"),
            c("descripcion", "Aspecto", LARGO, "Cómo se ve, de qué está hecho…"),
        ]},
        {"titulo": "Más detalles", "abierta": False, "campos": [
            c("origen", "Origen", LARGO, "Quién lo creó y cuándo…"),
            c("poderes", "Poderes o propiedades", LARGO, "Qué hace, qué limitaciones tiene…"),
            c("historia_objeto", "Historia del objeto", LARGO, "Por qué manos ha pasado…"),
        ]},
    ],
    "evento": [
        {"titulo": "Esenciales", "abierta": True, "campos": [
            c("momento", "Momento en la historia", ayuda="Año 3, la noche de la boda…"),
            c("lugar_evento", "Lugar", ayuda="Dónde ocurre"),
            c("descripcion", "Descripción", LARGO, "Qué pasa…"),
        ]},
        {"titulo": "Más detalles", "abierta": False, "campos": [
            c("participantes", "Personajes involucrados", LARGO, "Quién participa y qué hace cada quien…"),
            c("consecuencias", "Consecuencias", LARGO, "Qué cambia después de este evento…"),
        ]},
    ],
}

TIPOS = list(SECCIONES)
TIPO_PLURAL = {"personaje": "Personajes", "lugar": "Lugares", "objeto": "Objetos", "evento": "Eventos"}
ETIQUETA_NOTAS = {"personaje": "Datos importantes", "lugar": "Notas", "objeto": "Notas", "evento": "Notas"}
AYUDA_NOTAS = {"personaje": "Notas clave, detalles que no olvidar…"}
MAX_CORTO, MAX_LARGO = 200, 2000


def campos_de(tipo):
    return [campo for sec in SECCIONES[tipo] for campo in sec["campos"]]


def secciones_con_datos(tipo, datos):
    """Secciones con solo los campos llenos, listas para mostrar en el panel."""
    salida = []
    for sec in SECCIONES.get(tipo, []):
        llenos = [{"etiqueta": f["etiqueta"], "valor": datos[f["clave"]]}
                  for f in sec["campos"] if (datos or {}).get(f["clave"])]
        if llenos:
            salida.append({"titulo": sec["titulo"], "abierta": sec["abierta"], "campos": llenos})
    return salida
