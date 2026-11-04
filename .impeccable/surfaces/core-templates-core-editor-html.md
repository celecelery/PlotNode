---
version: 1
slug: "core-templates-core-editor-html"
primary_target: "core/templates/core/editor.html"
related_targets: ["core/templates/core/inicio.html","core/templates/core/proyectos.html","templates/base.html"]
---

# Superficies de la app PlotNode (portada, cuentas, mis obras, editor)

Scope: rediseño completo con identidad nueva. Modo: Operate (mis obras, editor, cuentas); la portada es Persuade dentro del mismo mundo.
Audiencia y tarea: escritores de ficción en español escriben capítulos largos y consultan datos de sus personajes sin salir del texto. Prueba disponible: el propio mecanismo (fichas al margen, alertas del auditor); no hay testimonios ni métricas reales.
Restricciones: $0, Django templates + JS sin compilar, Quill. Evitar lo genérico o "hecho por IA" y lo infantil o caricaturesco.

## Direction contract

THESIS: La pantalla es una galera de imprenta sobre la mesa del corrector: el texto del autor ocupa la hoja y todo lo que PlotNode aporta llega como marcas de lápiz en el margen. Rechaza el editor flotante sobre gris neutro con barra de herramientas y tarjetas genéricas.

OWN-WORLD: Mesa gris fría (#E9EAEC) con hoja blanca pura; riel y barra superior en grafito (#24272B) con texto blanco; tinta casi negra. Dos lápices con trabajos fijos: rojo corrector (#C8102E) solo para alertas, errores y borrar; azul de editor (#2148C0) para enlaces, foco y nombres con ficha, con resaltado azul no reproducible (#CDEBF5) en selección. Manuscrito en Literata (autoalojada); interfaz en la sans del sistema con cifras tabulares. Marcas de corrección dibujadas en SVG. Modo nocturno: mesa grafito y hoja oscura, mismos lápices aclarados.

STORY: El autor entiende que su texto es lo principal, que el contexto de su mundo aparece al margen sin cambiar de ventana y que la IA señala, no reescribe. Crea cuenta, abre una obra y escribe.

FIRST VIEWPORT: Editor: riel grafito a la izquierda (marca, Mis obras, índice de capítulos, cuenta); arriba sobre la mesa, migas (obra › capítulo), formato y estado de guardado; al centro la hoja blanca de 72ch con el título del capítulo y una columna de margen de ~220px dentro de la hoja, a la derecha del texto, con encabezado "Al margen". Portada: titular confirmado a la izquierda y, a la derecha, una galera de ejemplo con nombres marcados en azul y una marca roja al margen que conecta "ojos cafés" con la ficha (ojos verdes); acción principal "Probar gratis" bajo el titular.

FORM: Galeradas y marcas de corrección de estilo; candidato 1 de mi lista ordenada; seed: da044ef0664cc430.

SIGNATURE: Marcas al margen — cada nota (ficha consultada, alerta del auditor, estado vacío) vive en la columna de margen alineada con su párrafo y unida a la palabra por un trazo de lápiz. Movimiento: el trazo se dibuja una vez (stroke) al aparecer la marca; nada más se anima. Respeta prefers-reduced-motion.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
