---
version: 1
slug: "core-templates-core-editor-html"
primary_target: "core/templates/core/editor.html"
related_targets: ["core/templates/core/inicio.html","core/templates/core/proyectos.html","templates/base.html"]
---

# Superficies de la app PlotNode (portada, cuentas, mis proyectos, editor)

Scope: rediseño completo con identidad «Desvelo», elegida por la usuaria a partir de la maqueta B tras pedir algo menos corporativo que «Galeradas». Modo: Operate (mis proyectos, editor, cuentas); la portada es Persuade dentro del mismo mundo.
Audiencia y tarea: escritores de ficción en español (novela y fanfic) que escriben de noche y consultan datos de sus personajes sin salir del texto. Prueba disponible: el propio mecanismo; no hay testimonios ni métricas reales.
Restricciones: $0, Django templates + JS sin compilar, Quill; no mostrar funciones que todavía no existen (meta diaria, reparto real, revisar coherencia) como si funcionaran.

## Direction contract

THESIS: Un cuarto de escritura de madrugada: paneles redondeados y suaves sobre un violeta muy oscuro, donde cada personaje tiene su color y el texto del autor es lo más luminoso de la pantalla. Rechaza la barra lateral grafito y la mesa gris de software de oficina.

OWN-WORLD: Fondo noche #17142b; paneles #1f1a3a / #221d3f / #2a2450 con radios de 22, 16 y 12 px; texto #efe9fb y del libro #e6dff6. Tres colores de personaje con trabajos fijos: lila #b69cff (acción principal, selección, actual), durazno #ffb38a (avatar del usuario, pendiente) y menta #7fd8be (guardado, éxito); coral #ff7a85 solo para alertas, errores y borrar. Figtree (autoalojada) para la interfaz, Literata para títulos de obra y manuscrito. Nombres de personaje con subrayado ondulado de su color.

STORY: La escritora entra a un espacio tranquilo y propio, ve sus historias como objetos con color, abre una y escribe; entiende que su reparto vivirá al lado del texto y que PlotNode avisa pero no escribe.

FIRST VIEWPORT: Editor: tres paneles sobre la noche: izquierda (marca, Mis proyectos, índice de capítulos con palabras, contador «En este capítulo», cuenta con avatar durazno), centro (barra de formato redondeada y estado de guardado con punto menta; migas, título del capítulo en Literata y el texto a 40rem), derecha «Reparto de este capítulo» con estado vacío honesto. Portada: titular confirmado en Figtree 800 a la izquierda; a la derecha dos lunas planas (violeta y durazno), una tarjeta de ejemplo con nombres subrayados en ondas de color y un aviso coral, y fichas en píldoras; «Empezar a escribir gratis» bajo el titular.

FORM: Maqueta B «Desvelo» del lienzo de maquetas; elegida por la usuaria (pin del brief, sustituye la tirada anterior); seed: da044ef0664cc430.

SIGNATURE: Cada personaje con su color: inicial en círculo, subrayado ondulado en el texto y píldora de ficha del mismo color. Sin animaciones decorativas; solo transiciones de color en hover. Respeta prefers-reduced-motion.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
