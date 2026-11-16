# Iteración 2 · 5 a 11 de noviembre de 2026

**Objetivo:** ficha de personaje completa en un panel deslizable junto al editor, con barra de herramientas vertical, muletillas y glosario, todo funcional y guardando.

## Historias y tareas (programación)

| ID | Qué se hizo | Estado |
|---|---|---|
| HU-05 | Capítulos: crear, renombrar, reordenar y eliminar | Código listo; falta Pull Request y revisión |
| HU-07 | Fichas con alias y atributos (ahora «Otros atributos») | Código listo; falta Pull Request y revisión |
| HU-09 / HU-10 | Panel de fichas y ficha automática al seleccionar un nombre | Código listo; falta Pull Request y revisión |
| HU-18 | Eventos de uso: consultas de ficha y sesiones de escritura (palabras por sesión) | Código listo; falta Pull Request y revisión |
| HU-01 | Portada con botón de lista de espera (`MAILERLITE_FORM_URL`) | Falta pegar la URL del formulario |
| HU-25 | Ficha completa: ~30 campos en bloques plegables, foto o avatar | Código listo; falta Pull Request y revisión |
| T-07 | Subida de imágenes: JPG, PNG o WebP de hasta 2 MB, nombre aleatorio, sin archivos huérfanos | Código listo; falta Pull Request y revisión |
| HU-08 | Fichas de lugar, objeto y evento con campos propios; filtro por tipo | Código listo; falta Pull Request y revisión |
| HU-26 | Panel deslizable: animación, ancho ajustable (arrastre y teclado), crear y editar fichas dentro, cajón en pantallas angostas | Código listo; falta Pull Request y revisión |
| HU-27 | Barra de herramientas vertical plegable (texto, estilo, alineación, separador, enlace, imagen) | Código listo; falta Pull Request y revisión |
| HU-28 | Muletillas: detector, resaltado, sinónimos de lista fija y reemplazo | Código listo; falta Pull Request y revisión |
| HU-29 / HU-30 | Glosario (página y panel) y palabras marcadas con definición al pasar el cursor | Código listo; falta Pull Request y revisión |

Documentación y pruebas con escritores quedan con Paula (T-04, T-08). «Hecho» en el backlog solo cuando cada historia cumpla la Definición de Hecho (Pull Request revisado y pruebas en GitHub Actions).

## Decisiones
- Los campos de cada tipo de ficha viven en `core/fichas_schema.py` y se guardan en un campo JSON (`Ficha.datos`): agregar un campo no necesita migraciones.
- El panel pide el formulario al servidor como fragmento HTML (con la cabecera `X-Requested-With: fetch`) y guarda con `fetch`; así se usan las mismas validaciones que en la página completa.
- Las palabras del glosario se marcan con un formato propio de Quill (`<span class="glosario" data-termino="id">`) que se guarda con el capítulo.
- Las muletillas se resaltan con la API de resaltados de CSS: el texto no se modifica hasta que se reemplaza una palabra.
- Se corrigió el conteo de palabras: los bloques pegados (`<p>uno</p><p>dos</p>`) ya no unen palabras.

## Pendiente
Publicar en PythonAnywhere (T-06, iteración 3), revisar con Paula y pasar los estados a «Hecho».
