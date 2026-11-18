---
name: PlotNode
description: Desvelo. Un cuarto de escritura de madrugada donde cada personaje tiene su color y el texto del autor manda.
colors:
  noche: "#17142b"
  panel: "#1f1a3a"
  panel-2: "#221d3f"
  panel-3: "#2a2450"
  panel-4: "#2e2754"
  borde: "#332c5c"
  borde-2: "#4a4175"
  campo-borde: "#7a6db0"
  texto: "#efe9fb"
  texto-libro: "#e6dff6"
  texto-2: "#c3badf"
  texto-3: "#a99fcc"
  lila: "#b69cff"
  lila-claro: "#c9b8ff"
  sobre-lila: "#1a1235"
  durazno: "#ffb38a"
  sobre-durazno: "#2b1607"
  menta: "#7fd8be"
  sobre-menta: "#0f2b23"
  coral: "#ff7a85"
  coral-texto: "#ffa3ab"
  sobre-coral: "#2b0b10"
typography:
  display:
    fontFamily: "Figtree, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(2.4rem, 4.4vw, 3.85rem)"
    fontWeight: 800
    lineHeight: 1.04
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Figtree, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(2rem, 3vw, 2.6rem)"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Figtree, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.01em"
  titulo-obra:
    fontFamily: "Literata, Iowan Old Style, Georgia, serif"
    fontSize: "clamp(2rem, 3vw, 2.4rem)"
    fontWeight: 600
    lineHeight: 1.12
    letterSpacing: "-0.01em"
  titulo-historia:
    fontFamily: "Literata, Iowan Old Style, Georgia, serif"
    fontSize: "1.3rem"
    fontWeight: 600
    lineHeight: 1.12
    letterSpacing: "-0.01em"
  manuscrito:
    fontFamily: "Literata, Iowan Old Style, Georgia, serif"
    fontSize: "1.19rem"
    fontWeight: 400
    lineHeight: 1.9
    fontFeature: "\"kern\", \"liga\", \"onum\""
  body:
    fontFamily: "Figtree, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "\"tnum\""
  label:
    fontFamily: "Figtree, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "0.93rem"
    fontWeight: 650
    lineHeight: 1.5
  cifra:
    fontFamily: "Figtree, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.85rem"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.02em"
rounded:
  panel: "22px"
  tarjeta: "16px"
  boton: "14px"
  control: "12px"
  herramienta: "10px"
  tecla: "6px"
  pildora: "999px"
  circulo: "50%"
spacing:
  hueco-xs: "0.3rem"
  hueco-sm: "0.45rem"
  hueco: "0.65rem"
  hueco-md: "0.9rem"
  panel-interior: "1.3rem"
  seccion: "1.8rem"
  marco: "18px"
  marco-movil: "10px"
components:
  button-primary:
    backgroundColor: "{colors.lila}"
    textColor: "{colors.sobre-lila}"
    typography: "{typography.label}"
    rounded: "{rounded.boton}"
    padding: "0.6rem 1.15rem"
    height: "2.75rem"
  button-primary-hover:
    backgroundColor: "{colors.lila-claro}"
    textColor: "{colors.sobre-lila}"
  button-large:
    backgroundColor: "{colors.lila}"
    textColor: "{colors.sobre-lila}"
    rounded: "{rounded.tarjeta}"
    padding: "0.9rem 1.6rem"
    height: "3.4rem"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.texto}"
    rounded: "{rounded.boton}"
    padding: "0.6rem 1.15rem"
    height: "2.75rem"
  button-outline-hover:
    backgroundColor: "{colors.panel-3}"
    textColor: "{colors.texto}"
  button-danger:
    backgroundColor: "{colors.coral}"
    textColor: "{colors.sobre-coral}"
    rounded: "{rounded.boton}"
    padding: "0.6rem 1.15rem"
    height: "2.75rem"
  button-danger-hover:
    backgroundColor: "{colors.coral-texto}"
    textColor: "{colors.sobre-coral}"
  input:
    backgroundColor: "{colors.noche}"
    textColor: "{colors.texto}"
    rounded: "{rounded.control}"
    padding: "0.6rem 0.9rem"
    height: "2.9rem"
  rail:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.panel}"
    padding: "1.3rem 1rem 1rem"
    width: "250px"
  rail-link:
    backgroundColor: "transparent"
    textColor: "{colors.texto-2}"
    rounded: "{rounded.control}"
    padding: "0.7rem 0.75rem"
  rail-link-hover:
    backgroundColor: "{colors.panel-3}"
    textColor: "{colors.texto}"
  rail-link-active:
    backgroundColor: "{colors.lila}"
    textColor: "{colors.sobre-lila}"
  panel-texto:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.texto-libro}"
    typography: "{typography.manuscrito}"
    rounded: "{rounded.panel}"
  card-obra:
    backgroundColor: "{colors.panel-3}"
    textColor: "{colors.texto}"
    rounded: "{rounded.tarjeta}"
    padding: "1.1rem 1.3rem"
  card-obra-hover:
    backgroundColor: "{colors.panel-4}"
  inicial-obra:
    backgroundColor: "{colors.lila}"
    textColor: "{colors.sobre-lila}"
    rounded: "{rounded.circulo}"
    size: "3rem"
  avatar:
    backgroundColor: "{colors.durazno}"
    textColor: "{colors.sobre-durazno}"
    rounded: "{rounded.circulo}"
    size: "2.4rem"
  chip-ficha:
    backgroundColor: "{colors.texto}"
    textColor: "{colors.sobre-lila}"
    rounded: "{rounded.pildora}"
    padding: "0.5rem 0.9rem 0.5rem 0.5rem"
  aviso:
    backgroundColor: "{colors.panel-4}"
    textColor: "{colors.texto}"
    rounded: "{rounded.boton}"
    padding: "0.9rem 1rem"
  mensaje:
    backgroundColor: "{colors.panel-4}"
    textColor: "{colors.texto}"
    rounded: "{rounded.tarjeta}"
    padding: "0.8rem 1rem"
  toolbar-button:
    backgroundColor: "{colors.panel-4}"
    textColor: "{colors.texto}"
    rounded: "{rounded.herramienta}"
    size: "2.3rem"
  toolbar-button-active:
    backgroundColor: "{colors.borde-2}"
    textColor: "{colors.lila-claro}"
---

# Design System: PlotNode

## Overview

**Creative North Star: "El cuarto de desvelo"**

PlotNode es un cuarto de escritura a las dos de la mañana: una noche violeta muy oscura (sin negro) sobre la que flotan paneles redondeados y suaves, apenas más claros que el fondo. No hay mesa gris ni barra lateral grafito de software de oficina; el espacio se siente propio, tranquilo y nocturno. El texto del autor, en Literata y en un tono lavanda casi blanco, es lo más legible de la pantalla; la interfaz, en Figtree, se queda en tonos medios y se retira mientras se escribe.

El color tiene trabajo, no decoración. Tres colores de personaje (lila, durazno y menta) cumplen oficios fijos en toda la app, y el coral aparece solo cuando algo choca o se borra. La firma del sistema es que cada personaje (y cada historia) tiene su color: una inicial en círculo, un subrayado ondulado en el texto y una ficha en píldora, siempre del mismo tono. La densidad es media y el ritmo es amable: paneles grandes, esquinas generosas, contenido corto.

El movimiento es mínimo: transiciones de color de 0.15s al pasar el cursor, un desplazamiento de 1px al pulsar un botón y el deslizamiento del panel lateral (única excepción, porque comunica de dónde viene y a dónde va). Sin animaciones decorativas; `prefers-reduced-motion` anula todas las transiciones. Existe un solo tema, el oscuro (`color-scheme: dark`, `theme-color` igual a la noche).

**Key Characteristics:**
- Fondo noche violeta y paneles en cuatro pasos de luz, separados por 18px de noche, sin líneas divisorias entre regiones.
- Radios anidados: 22px el panel, 16px la tarjeta, 14px el botón, 12px el campo y el enlace.
- Dos voces tipográficas: Literata para la obra, Figtree para la herramienta.
- Lila, durazno y menta con oficios fijos; coral reservado para alertas, errores y borrar.
- Identidad en círculos: iniciales, avatar, puntos de color y lunas planas.
- Estados vacíos honestos con borde punteado, que anuncian lo que todavía no existe sin fingirlo.

## Colors

Una noche violeta en capas con tres colores de personaje cálidos y claros encima, y un coral de alarma que casi nunca aparece.

### Primary
- **Lila de desvelo** (`lila`): la acción principal (botón primario; un solo relleno lila por pantalla, el resto de acciones van con borde lila), la marca de «aquí estás» (filo de 2px o punto lila en el elemento actual, nunca relleno), el anillo de foco, el cursor de escritura y el primer personaje o historia. Su variante **Lila claro** (`lila-claro`) es el hover del botón, el color de los enlaces y el icono activo de la barra de formato. Sobre lila siempre va **Tinta de lila** (`sobre-lila`).

### Secondary
- **Durazno de lámpara** (`durazno`): el avatar del usuario, el punto de estado «pendiente / guardando», la luna chica de la portada y el tercer personaje de un reparto. No se usa para historias, para que la historia no se confunda con la persona. Sobre durazno va **Tinta de durazno** (`sobre-durazno`).

### Tertiary
- **Menta de guardado** (`menta`): el punto de «Guardado», el punto de los mensajes de éxito y el tercer personaje o historia. Sobre menta va **Tinta de menta** (`sobre-menta`).

### Alert
- **Coral de alarma** (`coral`): punto de aviso de continuidad, punto de mensaje de error, botón de eliminar y subrayado de la frase que choca con una ficha. Como texto sobre paneles se usa **Coral legible** (`coral-texto`), que también es el hover del botón coral; sobre coral va **Tinta de coral** (`sobre-coral`).

### Neutral
- **Noche** (`noche`): el fondo de toda la app y el relleno de los campos de formulario.
- **Panel** (`panel`): la capa más baja; riel de navegación, panel de reparto y pasos de la portada.
- **Panel 2** (`panel-2`): la hoja de trabajo; panel del texto, zona de Mis proyectos y tarjetas de cuenta.
- **Panel 3** (`panel-3`): tarjetas dentro de un panel (obra, formulario de nueva obra, contador, cuenta del riel) y hover de enlaces.
- **Panel 4** (`panel-4`): lo que flota o avisa dentro de una tarjeta; mensajes, avisos, botones de la barra de formato y hover de la tarjeta de obra.
- **Borde** (`borde`): la única línea interna (bajo la barra de formato) y el contorno de las tarjetas de cuenta.
- **Borde 2** (`borde-2`): borde del botón secundario, bordes punteados de estados vacíos, teclas y el botón de formato activo.
- **Borde de campo** (`campo-borde`): el contorno de los inputs; supera 3:1 contra la noche (3.96:1).
- **Texto** (`texto`): títulos y texto de interfaz principal.
- **Texto del libro** (`texto-libro`): el manuscrito y el texto de ejemplo; ligeramente más cálido que el de interfaz para que la lectura larga no deslumbre.
- **Texto 2** (`texto-2`): párrafos secundarios, enlaces del riel en reposo, entradas de formulario.
- **Texto 3** (`texto-3`): metadatos, migas, placeholders, conteos y etiquetas de grupo (6.5:1 sobre panel 2).

### Named Rules
**La regla de los oficios fijos.** Lila es acción y «aquí estás», durazno es la persona y lo pendiente, menta es lo guardado y lo correcto. Un color de personaje nunca cambia de oficio entre pantallas; entre personajes el ciclo es lila, menta, durazno; entre historias, solo lila y menta (durazno queda para la persona).

**La regla del coral escaso.** El coral solo marca alertas de continuidad, errores y la acción de borrar. Si algo coral no es un problema ni una pérdida, está mal.

**La regla de la noche sin negro.** Todos los neutros llevan el mismo matiz violeta (≈288° en OKLCH); no hay grises ni negros puros en superficies. La profundidad se gana subiendo luz dentro de ese matiz.

## Typography

**Display Font:** Figtree (autoalojada, variable 300–900; con system-ui, -apple-system, Segoe UI, Roboto)
**Body Font:** Figtree
**Libro Font:** Literata (autoalojada, variable 200–900 con cursiva; con Iowan Old Style, Georgia)

**Character:** Figtree pone la voz de la herramienta: geométrica, redonda y muy pesada en los titulares (800), cálida sin ser infantil. Literata es la voz de la obra: una serif de lectura en pantalla con cifras elzevirianas, que separa lo que escribe el autor de lo que dice la app.

### Hierarchy
- **Display** (800, clamp(2.4rem, 4.4vw, 3.85rem), 1.04, −0.03em): solo el titular de la portada.
- **Headline** (800, clamp(2rem, 3vw, 2.6rem), 1.12, −0.02em): título de página dentro de la app (Mis proyectos) y, a 2rem, el título de las tarjetas de cuenta. «Cómo funciona» usa 1.8rem.
- **Title** (800, 1.08–1.25rem, 1.12, −0.01em): títulos de panel (Fichas, Glosario, Muletillas), pasos de la portada y estados vacíos.
- **Título de obra** (Literata 600, clamp(2rem, 3vw, 2.4rem), −0.01em): el título del capítulo sobre el manuscrito.
- **Título de historia** (Literata 600, 1.3rem, −0.01em): el nombre de cada historia en Mis proyectos y su inicial en círculo.
- **Manuscrito** (Literata 400, 1.19rem, 1.9, `kern liga onum`): el texto del autor, con medida de 40rem; los párrafos se separan con 1em. El texto de ejemplo de la portada usa 1.18rem / 1.85.
- **Body** (400, 1rem, 1.5, cifras tabulares): toda la interfaz. El subtítulo de la portada sube a 1.2rem / 1.55 con medida de 34rem.
- **Label** (650, 0.93rem): etiquetas de formulario, acciones de tarjeta. El texto de botón va a 750 y 0.98rem. La etiqueta de grupo del riel (nombre del proyecto sobre el índice de capítulos) es la única en mayúsculas: 750, 0.8rem, +0.02em, Texto 3.
- **Cifra** (800, 1.85rem, −0.02em): el número de palabras del capítulo en el contador del riel.
- **Meta** (400, 0.82–0.9rem, Texto 3): conteos, migas, datos de la obra separados por «·», estado de guardado.

### Named Rules
**La regla de las dos voces.** Literata solo para lo que pertenece a la obra: manuscrito, títulos de capítulo e historia, iniciales de historia y texto de ejemplo. Todo lo que es herramienta (botones, navegación, etiquetas, avisos, títulos de panel) va en Figtree.

**La regla del titular pesado.** Los titulares de interfaz van en Figtree 800 con tracking negativo y `text-wrap: balance`; los pasos intermedios (550, 650, 750) existen gracias a la fuente variable y se usan para jerarquía fina, no para titulares.

## Layout

La app es un marco de paneles sobre la noche: una rejilla de riel (250px) más área de trabajo, con 18px de hueco y 18px de margen exterior. El riel es fijo (sticky) y ocupa la altura de la ventana menos el margen. En el editor el área de trabajo se divide otra vez en panel de texto flexible más panel de reparto de 330px (270px por debajo de 1200px), y toda la página mide exactamente el alto de la ventana: solo el texto hace scroll dentro de su panel.

Dentro de los paneles el contenido se limita a 56rem (Mis proyectos) o 40rem (migas, título y manuscrito del editor, centrados). Las tarjetas de cuenta miden 28rem y van centradas sobre la noche. La portada usa un contenedor de 80rem con titular a la izquierda (columna de hasta 37rem) y la tarjeta de ejemplo a la derecha, con márgenes laterales `clamp(1rem, 5vw, 5rem)`.

El ritmo de espaciado va de huecos pequeños (0.3–0.65rem entre icono y texto o entre enlaces) a rellenos de panel de 1.3rem y separaciones de sección de 1.8–2rem. Los rellenos grandes usan `clamp()` para respirar en pantallas anchas.

Respuesta por anchos:
- **≤1100px**: el riel baja a 210px.
- **≤1000px** (editor): el reparto pasa debajo del texto, la página deja de fijarse al alto de la ventana y el panel de texto conserva al menos 70vh.
- **≤900px** (portada): una sola columna; las lunas bajan detrás de la tarjeta de ejemplo y los pasos se apilan.
- **≤760px**: el marco se vuelve una pila con 10px de margen; el riel se convierte en una barra horizontal con la marca a la izquierda, los enlaces solo con icono (texto oculto para lectores de pantalla) y «Cerrar sesión» sin avatar; el índice de capítulos, el contador y el atajo de teclado se ocultan; el estado de guardado sube sobre la barra de formato.
- **≤480px**: la barra pública deja solo el botón principal.

### Named Rules
**La regla de los paneles sobre la noche.** Cada región de la app es un panel redondeado separado de los demás por noche, nunca por una línea. La única línea interna permitida es la que separa la barra de formato del texto.

## Elevation & Depth

El sistema es tonal: la profundidad se construye subiendo luz dentro del mismo violeta (noche → panel → panel 2 → panel 3 → panel 4), no con sombras. Un panel sobre la noche, una tarjeta sobre el panel y un aviso sobre la tarjeta se leen como capas sin necesitar borde. Las sombras existen solo en dos objetos que flotan de verdad, y el foco de los campos usa un halo lila translúcido.

### Shadow Vocabulary
- **Tarjeta flotante de portada** (`box-shadow: 0 30px 60px -24px rgba(0, 0, 0, .7)`): solo la tarjeta de ejemplo de la portada, que flota sobre la luna.
- **Menú desplegable** (`box-shadow: 0 16px 32px -12px rgba(0, 0, 0, .6)`): opciones del selector de estilo de párrafo.
- **Halo de foco de campo** (`box-shadow: 0 0 0 3px rgba(182, 156, 255, .25)`): input o select con foco, junto con el borde lila.
- **Choque** (`box-shadow: inset 0 -2px 0` coral, sobre fondo coral al 22%): marca la frase que contradice una ficha.

### Named Rules
**La regla de la luz por capas.** Lo que está más arriba es más claro. Una sombra solo aparece cuando algo flota por encima de la página (menú, tarjeta de demostración); los paneles y tarjetas de trabajo son planos.

## Shapes

Todo es suave. Los radios se anidan de fuera hacia dentro: panel 22px, tarjeta 16px (y botón grande), botón 14px (y aviso), campo y enlace del riel 12px, botón de la barra de formato 10px, tecla y contorno de foco 6px. La identidad usa círculos completos: la inicial de cada historia, el avatar, los iconos de los pasos, los puntos de estado y las dos lunas planas de la portada. Las fichas de personaje son píldoras (999px). Los bordes son finos (1–1.5px) y solo sólidos en botones secundarios, campos y teclas; lo que aún no existe lleva borde punteado de 1.5px. Los nombres de personaje se marcan con subrayado ondulado (`wavy`, 1.5px, desplazado 0.35em) en el color del personaje.

### Named Rules
**La regla del radio anidado.** Un elemento dentro de otro siempre tiene un radio menor que su contenedor. Nada es cuadrado; nada usa radios de píldora salvo las fichas.

## Components

### Buttons
Redondos, sólidos y amables; el peso del texto hace el trabajo.
- **Shape:** esquinas suaves (14px; 16px en el botón grande), borde de 1.5px del mismo color que el relleno.
- **Primary:** relleno lila con tinta de lila, Figtree 750 a 0.98rem, altura mínima de 2.75rem y relleno de 0.6rem × 1.15rem. El botón grande (portada) sube a 3.4rem y 1.08rem.
- **Hover / Focus:** el relleno pasa a lila claro con transición de color de 0.15s; al pulsar baja 1px. El foco visible es un contorno lila de 2px a 3px de distancia.
- **Con borde (secundario):** fondo transparente, texto claro, borde Borde 2, peso 650; en hover se rellena de Panel 3 y el borde sube a Texto 3.
- **Coral (destructivo):** relleno coral con tinta de coral; solo para confirmar un borrado. El enlace «Eliminar» de una tarjeta usa coral legible como texto.
- **Enlace de texto:** lila claro subrayado; en hover pasa a blanco.

### Chips
- **Ficha de personaje:** píldora de fondo Texto (casi blanco) con tinta de lila, Figtree 750 a 0.93rem, e inicial del personaje en un círculo de 1.65rem de su color. Es la única superficie clara del sistema y por eso destaca como objeto.

### Cards / Containers
- **Corner Style:** 22px para paneles, 16px para tarjetas.
- **Background:** paneles en Panel o Panel 2; tarjetas en Panel 3; avisos y mensajes en Panel 4.
- **Shadow Strategy:** planas (ver Elevation & Depth).
- **Border:** ninguno, salvo las tarjetas de cuenta (1px Borde).
- **Internal Padding:** 1.1–1.3rem en tarjetas; `clamp(1.4rem, 3vw, 2.6rem)` en la zona de Mis proyectos.
- **Tarjeta de obra:** inicial de la historia en círculo de 3rem (Literata 600, color del ciclo lila/menta), título en Literata 600, datos en Texto 3 separados por «·», y acciones a la derecha (botón «Escribir» con borde lila, enlaces Renombrar y Eliminar). En hover el fondo sube a Panel 4.

### Inputs / Fields
- **Style:** fondo Noche (más oscuro que el panel, como un pozo), borde de 1.5px Borde de campo, radio 12px, altura mínima 2.9rem, relleno 0.6rem × 0.9rem. Placeholder en Texto 3.
- **Hover:** el borde pasa a lila claro.
- **Focus:** borde lila más halo lila translúcido de 3px; sin contorno del navegador.
- **Error:** la lista de errores va arriba del campo en coral legible, 650, 0.9rem. Los textos de ayuda van abajo en Texto 3 a 0.85rem.

### Navigation
- **Riel:** panel de 250px en Panel con la marca arriba (icono de nodo lila y durazno + «PlotNode» en Figtree 800), enlaces con icono de trazo de 18px, una etiqueta de grupo opcional y la cuenta al fondo (tarjeta Panel 3 con avatar durazno y «Cerrar sesión» como enlace subrayado).
- **Enlace del riel:** Texto 2, 550, radio 12px; hover en Panel 3 con Texto; actual (`aria-current`) en Panel 3 con Texto, peso 750 y un filo lila de 2px a la izquierda (sombra interior); en el índice de capítulos, un punto lila antes del título. Así el manuscrito sigue siendo lo más luminoso de la pantalla.
- **Barra pública:** marca a la izquierda, «Iniciar sesión» como texto y «Crear cuenta» como botón primario a la derecha.
- **Móvil:** el riel se vuelve una barra horizontal de iconos (ver Layout).

### Mensajes y avisos
- **Mensaje:** tarjeta Panel 4 de 16px con un punto de 0.55rem a la izquierda: menta para éxito, coral para error. El texto se queda en Texto; el color vive solo en el punto.
- **Aviso de continuidad:** tarjeta Panel 4 de 14px con punto coral y el motivo en negrita coral legible, seguido de la explicación en Texto.

### Editor (firma)
- **Barra de formato:** botones cuadrados redondeados de 2.3rem en Panel 4 (radio 10px), iconos en Texto; activo o en hover pasan a Borde 2 y el icono activo se pinta lila claro. El selector de estilo dice «Párrafo / Título / Subtítulo».
- **Estado de guardado:** texto Texto 3 a 0.9rem con un punto de 0.5rem: menta guardado, durazno pendiente o guardando, coral (y texto coral legible, 650) si falla.
- **Hoja:** título del capítulo en Literata, manuscrito a 40rem con cursor lila. Las citas llevan una línea izquierda fina de 1px en Texto 3 y texto en Texto 2.
- **Contador:** tarjeta Panel 3 en el riel con «En este capítulo», la cifra en Figtree 800 y «palabras» en Texto 3. Cada capítulo del índice muestra sus palabras a la derecha.
- **Panel:** panel derecho deslizable con pestañas (Fichas, Glosario, Muletillas), título de panel, el estado vacío y, al pie, el atajo de teclado con teclas (`kbd`: borde Borde 2 con base de 2px, fondo Panel 3, radio 6px).

### Nombre de personaje (firma)

En el editor, los nombres y alias que ya tienen ficha se subrayan con la API de resaltados de CSS (`::highlight(nombre-lila|menta|durazno)`, ondulado de 1.5px): el subrayado no se guarda en el texto y se omite en navegadores sin esa API.
Cada personaje se marca en el texto con subrayado ondulado de su color (lila, menta o durazno), se representa con su inicial en un círculo de ese color y su ficha es una píldora con esa inicial. Lo que contradice una ficha se resalta con fondo coral al 22%, radio 4px y una línea coral inferior.

### Estado vacío
Contenedor con borde punteado de 1.5px en Borde 2 y radio 16px, encabezado por tres puntos superpuestos (lila, durazno, menta) de 1.9rem con aro del color del panel, un título en Figtree 800 y una explicación en Texto 2 que dice qué pasará y cómo empezar.

### Herramientas de la obra (iteración 3)
Relaciones, línea de tiempo y tablón comparten el riel «Herramientas» (solo escritorio), un formulario de alta arriba y la vista debajo. El mapa de relaciones es un SVG con un nodo por personaje en su color y aristas rotuladas; la línea de tiempo es una cuadrícula de carriles (uno por personaje, más «Sin personaje») por etapas; el tablón es una pizarra de notas arrastrables que también se mueven con las flechas del teclado. El tutorial es una guía de pasos sobre un proyecto de muestra creado al registrarse, y se puede repetir desde «Ver tutorial».

### Named Rules
**La regla del estado vacío honesto.** Lo que todavía no existe se dibuja con borde punteado y se explica en texto; nunca se simula con datos falsos ni con controles que no hacen nada.

**La regla del punto de color.** El estado (guardado, pendiente, éxito, error, aviso) se comunica con un punto de color junto a un texto que lo dice en palabras; el color nunca es la única señal.

## Do's and Don'ts

### Do:
- **Do** construir cada pantalla como paneles redondeados (22px) sobre la noche (`noche`), separados por 18px.
- **Do** subir de Panel a Panel 4 para indicar capas: tarjeta sobre panel, aviso sobre tarjeta.
- **Do** asignar a cada personaje un color del ciclo lila, menta, durazno (y a cada historia lila o menta), y repetir ese color en su inicial, su subrayado ondulado y su ficha.
- **Do** usar Literata solo para la obra (manuscrito a 1.19rem / 1.9 y 40rem de medida, títulos de capítulo e historia) y Figtree para toda la interfaz.
- **Do** acompañar cada color de estado con texto que diga lo mismo (punto menta + «Guardado»).
- **Do** limitar el movimiento a transiciones de color de 0.15s (y al deslizamiento del panel) y respetar `prefers-reduced-motion`.
- **Do** mantener un solo tema oscuro (`color-scheme: dark`).

### Don't:
- **Don't** volver a la barra lateral grafito ni a la mesa gris de software de oficina.
- **Don't** usar coral para nada que no sea alerta, error o borrar.
- **Don't** cambiar el oficio de un color de personaje (lila no marca éxito; menta no es acción principal).
- **Don't** separar regiones de la app con líneas divisorias ni levantar paneles de trabajo con sombras.
- **Don't** usar Literata en botones, navegación o etiquetas.
- **Don't** añadir animaciones decorativas (entradas, rebotes, parallax).
- **Don't** mostrar funciones que todavía no existen como si funcionaran; usa el estado vacío honesto.
