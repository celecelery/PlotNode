---
name: PlotNode
description: Galeradas sobre la mesa del corrector — el manuscrito en la hoja, el contexto al margen.
colors:
  mesa: "#e9eaec"
  hoja: "#ffffff"
  tinta: "#16181b"
  tinta-2: "#565c66"
  tinta-3: "#646a73"
  grafito: "#24272b"
  grafito-2: "#34383e"
  sobre-grafito: "#f4f4f2"
  sobre-grafito-2: "#b8bcc2"
  rojo: "#c8102e"
  rojo-fondo: "#fbe7ea"
  azul: "#2148c0"
  azul-np: "#cdebf5"
  azul-fondo: "#eaf1fd"
  linea: "#d3d6db"
  linea-hoja: "#e6e8eb"
  campo-borde: "#8a9099"
  marca-nodo: "#e0394e"
  mesa-noche: "#17191c"
  hoja-noche: "#212428"
  tinta-noche: "#e8e6e1"
  tinta-2-noche: "#aeb2b8"
  tinta-3-noche: "#8b9097"
  grafito-noche: "#0e1012"
  grafito-2-noche: "#1d2024"
  sobre-grafito-noche: "#ecebe7"
  sobre-grafito-2-noche: "#9ca1a8"
  rojo-noche: "#ff6b78"
  rojo-fondo-noche: "#3a1e23"
  azul-noche: "#93b2ff"
  azul-np-noche: "rgba(147, 178, 255, .26)"
  azul-fondo-noche: "#1f2a42"
  linea-noche: "#33373d"
  linea-hoja-noche: "#2e3237"
  campo-borde-noche: "#6b717a"
typography:
  display:
    fontFamily: "Literata, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "clamp(2.2rem, 3.7vw, 3.15rem)"
    fontWeight: 620
    lineHeight: 1.08
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Literata, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "clamp(1.9rem, 3vw, 2.4rem)"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Literata, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "1.35rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  manuscrito:
    fontFamily: "Literata, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "1.16rem"
    fontWeight: 400
    lineHeight: 1.85
    fontFeature: "\"kern\", \"liga\", \"onum\""
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "\"tnum\""
  label:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.92rem"
    fontWeight: 600
    lineHeight: 1.4
    fontFeature: "\"tnum\""
  nota:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.86rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "\"tnum\""
rounded:
  hoja: "3px"
  tecla: "4px"
  control: "6px"
spacing:
  riel-ancho: "240px"
  margen-ancho: "15rem"
  medida-texto: "40rem"
  hoja-max: "68rem"
  contenido-max: "60rem"
  portada-max: "76rem"
  mesa-gutter: "clamp(1rem, 4vw, 3rem)"
  hoja-texto: "clamp(2rem, 5vw, 3.6rem) clamp(1.5rem, 5vw, 4.2rem)"
components:
  boton:
    backgroundColor: "{colors.grafito}"
    textColor: "{colors.sobre-grafito}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0.5rem 1.05rem"
    height: "2.5rem"
  boton-hover:
    backgroundColor: "{colors.grafito-2}"
  boton-grande:
    padding: "0.7rem 1.4rem"
    height: "3rem"
  boton-noche:
    backgroundColor: "{colors.sobre-grafito-noche}"
    textColor: "{colors.tinta}"
  boton-borde:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0.5rem 1.05rem"
    height: "2.5rem"
  boton-borde-hover:
    backgroundColor: "{colors.hoja}"
  boton-claro:
    backgroundColor: "{colors.sobre-grafito}"
    textColor: "{colors.grafito}"
    rounded: "{rounded.control}"
  boton-rojo:
    backgroundColor: "{colors.rojo}"
    textColor: "{colors.hoja}"
    rounded: "{rounded.control}"
  boton-rojo-hover:
    backgroundColor: "#a50d26"
  campo:
    backgroundColor: "{colors.hoja}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0.5rem 0.75rem"
    height: "2.6rem"
  hoja:
    backgroundColor: "{colors.hoja}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.hoja}"
  riel:
    backgroundColor: "{colors.grafito}"
    textColor: "{colors.sobre-grafito-2}"
    width: "{spacing.riel-ancho}"
    padding: "1.1rem 0.8rem 1rem"
  riel-enlace:
    textColor: "{colors.sobre-grafito-2}"
    rounded: "{rounded.control}"
    padding: "0.5rem 0.55rem"
  riel-enlace-activo:
    backgroundColor: "rgba(255, 255, 255, .1)"
    textColor: "{colors.sobre-grafito}"
  mensaje:
    backgroundColor: "{colors.hoja}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0.6rem 0.9rem"
  margen:
    textColor: "{colors.tinta-2}"
    typography: "{typography.nota}"
    width: "{spacing.margen-ancho}"
  marca-nota-azul:
    textColor: "{colors.azul}"
    typography: "{typography.nota}"
  marca-nota-roja:
    textColor: "{colors.rojo}"
    typography: "{typography.nota}"
---

# Design System: PlotNode

## Overview

**Creative North Star: "La galera sobre la mesa del corrector"**

La pantalla de PlotNode es una galera de imprenta puesta sobre una mesa gris fría. El texto del autor ocupa la hoja blanca y manda; todo lo que PlotNode aporta (fichas consultadas, alertas del auditor, estados vacíos, avisos) llega como marcas de lápiz en el margen de esa misma hoja. Alrededor, el mobiliario de la mesa es grafito: el riel de navegación y la barra pública son la única masa oscura, y se quedan quietos mientras el autor escribe.

El sistema es sobrio y de densidad media: una sola superficie elevada (la hoja), tinta casi negra, dos lápices con trabajos fijos (rojo corrector y azul de editor) y ningún otro color con tono. El manuscrito se compone en Literata con interlineado amplio y cifras antiguas; la interfaz habla en la sans del sistema con cifras tabulares, como las anotaciones de un corrector junto a una página impresa. La firma visual son las marcas al margen: una palabra subrayada o encerrada a mano en el texto, unida por un trazo de lápiz a su nota en la columna del margen.

El mundo rechaza explícitamente el editor flotante sobre gris neutro con barra de herramientas y tarjetas genéricas. Debe sentirse serio para alguien que escribe una novela: nada infantil, caricaturesco ni con apariencia de plantilla.

**Key Characteristics:**
- Mesa gris fría, hoja blanca pura, tinta casi negra; el grafito solo para el mobiliario (riel, barra, botón principal).
- Dos lápices con trabajos fijos: rojo para corregir, azul para todo lo que PlotNode aporta.
- El margen vive dentro de la hoja, a la derecha del texto, separado por un filete de 1px.
- Literata para la voz del autor y los títulos; sans del sistema para la voz de PlotNode.
- Marcas, iconos y la marca de la casa dibujados como trazos de lápiz en SVG.
- Un solo movimiento: el trazo de la marca se dibuja una vez al aparecer.
- Modo nocturno con la misma lógica: mesa y hoja grafito, lápices aclarados.

## Colors

Una paleta de papel y grafito, casi acromática, en la que solo dos lápices tienen permiso para llevar color.

### Primary
- **Azul de editor** (`azul`): el lápiz de PlotNode. Enlaces, anillo de foco, nombres con ficha (subrayado de 2px), títulos de las notas de ficha, el estado «Guardado», el cursor del manuscrito y los iconos de pasos que no son alerta. En modo nocturno se aclara (`azul-noche`).
- **Azul no reproducible** (`azul-np`): el resaltador de imprenta. Fondo de la selección de texto y halo de 3px del campo enfocado. Nunca como relleno de superficie.
- **Fondo azul** (`azul-fondo`): tinte muy pálido reservado para fondos de notas azules; disponible en el sistema, todavía sin uso amplio en las pantallas construidas.

### Secondary
- **Rojo corrector** (`rojo`): el lápiz que corrige. Solo alertas del auditor, errores de formulario, borde de campo con error, mensaje de error, el enlace «Eliminar» y el botón destructivo. El círculo a mano alrededor de una contradicción usa este color. En modo nocturno se aclara (`rojo-noche`).
- **Fondo rojo** (`rojo-fondo`): tinte pálido para fondos de alertas; disponible, de uso mínimo.

### Neutral
- **Mesa gris fría** (`mesa`): el fondo de toda la aplicación, la mesa sobre la que descansa la hoja. También el fondo de la barra pegajosa del editor, para que se lea como parte de la mesa y no como una barra flotante.
- **Hoja blanca pura** (`hoja`): la única superficie de lectura y escritura: manuscrito, formularios de cuenta, lista de obras, galera de ejemplo, mensajes.
- **Tinta casi negra** (`tinta`): texto principal, títulos y manuscrito.
- **Tinta gris** (`tinta-2`): texto secundario, subtítulos, metadatos de obras, cuerpo de las notas al margen, migas.
- **Tinta tenue** (`tinta-3`): marcadores de posición, pies de figura, atajos; el gris más claro que todavía alcanza 4.5:1 sobre la mesa.
- **Grafito** (`grafito`) y **grafito claro** (`grafito-2`): riel, barra pública y botón principal en reposo y en hover.
- **Sobre grafito** (`sobre-grafito`) y **sobre grafito tenue** (`sobre-grafito-2`): texto y enlaces sobre el riel y la barra; el tenue para enlaces en reposo y títulos de grupo del riel.
- **Filete de mesa** (`linea`) y **filete de hoja** (`linea-hoja`): bordes de mensajes y teclas, y el filete vertical que separa texto y margen dentro de la hoja; separadores entre obras.
- **Borde de campo** (`campo-borde`): contorno de campos y del botón con borde. Mide 3.2:1 contra la hoja (3.1:1 en modo nocturno), sobre el mínimo de 3:1 para componentes; no debe aclararse.
- **Nodo de la marca** (`marca-nodo`): solo el punto rojo del logotipo de PlotNode. No es un color de interfaz.

### Named Rules
**La Regla de los Dos Lápices.** El rojo corrector es solo para lo que hay que corregir o borrar; el azul de editor es para todo lo que PlotNode aporta o permite activar. Ningún tercer color con tono entra en la interfaz, y ninguno de los dos lápices se usa como decoración.

**La Regla del Grafito.** El grafito es mobiliario: riel, barra pública y botón principal. Nunca es fondo del texto del autor en modo claro, y nunca se usa para tarjetas o paneles dentro de la mesa.

## Typography

**Display Font:** Literata, autoalojada en woff2 variable 200–900 (con Iowan Old Style, Charter, Georgia, serif)
**Body Font:** sans del sistema (system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif)

**Character:** Literata es el libro: una serif de lectura larga para el manuscrito y para todo título, que hace que la pantalla se lea como una página compuesta. La sans del sistema es la mano del corrector: neutra, compacta y con cifras tabulares, para la interfaz y las notas al margen.

### Hierarchy
- **Display** (Literata 620, clamp 2.2–3.15rem, 1.08): solo el titular de la portada; tracking ligeramente cerrado.
- **Headline** (Literata 600, clamp 1.9–2.4rem, 1.15): título de página («Mis proyectos») y título del capítulo en la hoja. Las páginas de cuenta usan el mismo rol a 1.85rem.
- **Title** (Literata 600, 1.25–1.6rem, 1.15): títulos de obra en la lista, títulos de sección de la portada, título de la galera de ejemplo.
- **Manuscrito** (Literata 400, 1.16rem, 1.85): el texto del autor, con kerning, ligaduras y cifras antiguas, a una medida máxima de 40rem (unos 72 caracteres). La galera de ejemplo usa 1.08rem con el mismo interlineado.
- **Body** (sans 400, 1rem, 1.5): interfaz, descripciones y párrafos de apoyo; subtítulo de portada a 1.13rem.
- **Label** (sans 600, 0.92rem): etiquetas de campo y botones (0.95rem). Los títulos de grupo del riel y el encabezado «Al margen» usan sans 600–650 a 0.8–0.82rem en tinta gris, en altas y bajas.
- **Nota** (sans 400, 0.86–0.88rem, 1.4): cuerpo de notas al margen, metadatos de obra, estado de guardado; el título de una nota va en 600–650 del color de su lápiz.

### Named Rules
**La Regla de las Dos Manos.** Literata es la voz del autor y de los títulos; la sans del sistema es la voz de PlotNode. Una nota al margen nunca se compone en Literata, y el manuscrito nunca en sans.

**La Regla de las Cifras.** La interfaz usa cifras tabulares (contadores de palabras, fechas, metadatos); el manuscrito usa cifras antiguas.

## Layout

El modelo espacial es una mesa con una hoja encima. En la aplicación, un riel grafito fijo de 240px a la izquierda (200px por debajo de 1100px) y, a la derecha, la mesa con su propio margen fluido (clamp de 1–3rem a los lados). El editor centra una hoja de hasta 68rem dividida en dos columnas: el texto (medida de 40rem centrada, con relleno clamp de 2–3.6rem arriba y 1.5–4.2rem a los lados) y el margen de 15rem (12.5rem por debajo de 1100px) dentro de la misma hoja, separado por un filete de `linea-hoja`. Sobre la hoja, una barra pegajosa del color de la mesa con migas, formato y estado de guardado en una sola fila.

La lista de obras repite la galera: cada obra es una fila con título y acciones a la izquierda y metadatos en una columna de 15rem a la derecha, con el mismo filete vertical. Las páginas de cuenta son una hoja angosta de 27rem centrada sobre la mesa. La portada es una rejilla de dos columnas (titular a la izquierda, galera de ejemplo a la derecha) con máximo de 76rem.

Responsivo: a 900px la portada pasa a una columna; a 760px el riel se convierte en barra superior horizontal (solo marca, icono de Mis proyectos y Cerrar sesión), la hoja del editor ocupa todo el ancho sin radio y el margen baja debajo del texto con un filete superior; las notas de la galera se apilan bajo su párrafo con un filete izquierdo y los trazos desaparecen. A 480px la barra pública deja solo el botón «Crear cuenta».

### Named Rules
**La Regla del Margen Interior.** Las notas de PlotNode viven en la columna de margen dentro de la hoja, a la derecha del texto y alineadas con el párrafo que comentan. Nunca en un panel flotante, una tarjeta aparte ni una ventana modal.

## Elevation & Depth

Sistema plano con una sola elevación: la hoja. Todo lo demás se separa por tono (mesa contra hoja, grafito contra mesa) y por filetes de 1px. En el riel, el hover y la página actual se marcan con velos blancos translúcidos (6% y 10%), no con sombras.

### Shadow Vocabulary
- **Sombra de hoja** (`box-shadow: 0 1px 2px rgba(22, 24, 27, .08), 0 8px 24px -6px rgba(22, 24, 27, .12)`): toda hoja sobre la mesa y el desplegable de estilo de párrafo, que es un recorte de hoja. En modo nocturno: `0 1px 2px rgba(0, 0, 0, .4), 0 10px 28px -8px rgba(0, 0, 0, .55)`.
- **Halo de foco de campo** (`box-shadow: 0 0 0 3px` en azul no reproducible): solo en campos enfocados, junto con el borde azul.

### Named Rules
**La Regla de la Hoja Única.** Solo el papel se levanta de la mesa. Botones, mensajes, notas y el riel no llevan sombra.

## Shapes

Esquinas casi rectas de papel para las hojas (3px) y un redondeo discreto y único para controles: botones, campos, mensajes, enlaces del riel y botones de formato (6px); las teclas `kbd` usan 4px con borde inferior de 2px. Los filetes son de 1px. Las únicas formas irregulares son las del lápiz: el óvalo a mano alrededor de una contradicción (radio asimétrico y rotación de -2°), los trazos de unión con curvas de 8px de radio y los iconos SVG dibujados con trazos redondeados (marca, ficha, alerta, insertar, visto).

### Named Rules
**La Regla del Lápiz.** Lo geométrico es de la imprenta (hoja, controles, filetes); lo orgánico es del lápiz (marcas, trazos, iconos). Nunca se mezclan: no hay botones con forma de mano ni marcas con esquinas rectas.

## Components

### Buttons
Firmes y compactos, sin adornos: un bloque de grafito con texto claro.
- **Shape:** redondeo discreto de control (6px), altura mínima 2.5rem; variante grande de 3rem.
- **Primary:** fondo grafito, texto sobre grafito, sans 600 a 0.95rem. En modo nocturno se invierte: fondo claro y texto tinta.
- **Hover / Focus:** hover a grafito claro con transición de 0.15s en fondo y borde; al pulsar baja 1px. Foco con contorno azul de 2px separado 2px.
- **Con borde:** transparente con borde de campo y texto tinta; en hover toma fondo de hoja. Acción secundaria junto a la principal («Ya tengo cuenta»).
- **Claro:** fondo sobre grafito y texto grafito; solo sobre la barra pública («Crear cuenta»).
- **Rojo:** fondo rojo corrector y texto blanco; solo para la confirmación destructiva («Sí, eliminar proyecto»).

### Cards / Containers
La hoja es el único contenedor.
- **Corner Style:** esquina de papel (3px).
- **Background:** hoja.
- **Shadow Strategy:** sombra de hoja (ver Elevation & Depth).
- **Border:** ninguno; las divisiones internas son filetes de `linea-hoja`.
- **Internal Padding:** 1.1–2.4rem según el uso; en la lista de obras, 1.25rem × 1.6rem por fila.

### Inputs / Fields
- **Style:** fondo de hoja, borde de 1px en borde de campo, 6px de radio, altura mínima 2.6rem, relleno 0.5rem × 0.75rem. Etiqueta encima en sans 600 a 0.92rem; ayuda debajo en tinta gris a 0.82rem.
- **Focus:** borde azul y halo de 3px en azul no reproducible; sin contorno del navegador.
- **Error:** mensaje en rojo corrector, sans 600 a 0.88rem, encima del campo, y borde del campo en rojo.

### Navigation
- **Riel (aplicación):** columna grafito pegajosa. Arriba la marca (Literata 650, 1.2rem); enlaces sans 0.95rem en sobre grafito tenue con icono de trazo de 18px; hover con velo blanco del 6%, página actual con velo del 10% y texto claro. En el editor, el título de la obra y el índice de capítulos con su conteo de palabras alineado a la derecha. Abajo, el usuario y «Cerrar sesión» como texto subrayado, separados por un filete translúcido. El foco dentro del riel usa un azul aclarado.
- **Barra pública (portada y cuentas):** franja grafito con la marca a la izquierda y «Iniciar sesión» + botón claro a la derecha.
- **Migas del editor:** sans 0.9rem en tinta gris, separadas por «/», con el capítulo actual en tinta y 600.

### Mensajes
Notas de lápiz sobre la mesa: hoja con filete de 1px, 6px de radio, precedidas por una palomita a mano de 1rem en azul. La variante de error cambia el filete y la palomita a rojo corrector.

### Estado de guardado
Sans 0.88rem junto al contador de palabras. «Guardado a las HH:MM» en azul con la palomita a mano; «Cambios sin guardar» y «Guardando…» en tinta gris con un punto de 0.5rem; error en rojo y 600.

### Marcas al margen (componente firma)
Cada nota de PlotNode se compone de tres partes. En el texto, la palabra señalada: subrayado azul de 2px separado 0.22em para un nombre con ficha, u óvalo rojo dibujado a mano (1.6px, radio irregular, rotado -2°) para una contradicción. En el margen, la nota: título sans 600 del color de su lápiz con un icono de trazo de 28px, y cuerpo en sans 0.86rem (tinta gris para fichas, tinta para alertas). Entre ambas, el trazo: una guía punteada tenue que sale bajo la palabra y corre por el interlineado hasta el canal del margen, y un tramo sólido de 1.4px con curvas de 8px que sube o baja hasta la nota. Las notas se alinean verticalmente con su palabra sin encimarse (16px mínimo entre ellas). El tramo sólido se dibuja una sola vez al aparecer (700ms, curva de salida suave, escalonado 350ms entre marcas) y no se anima con `prefers-reduced-motion`. En pantallas angostas los trazos desaparecen y la nota se apila bajo su párrafo con un filete izquierdo. La nota vacía del margen («Fichas de personajes», «Un capítulo para empezar») usa la misma composición sin trazo.

## Do's and Don'ts

### Do:
- **Do** poner todo texto del autor sobre la hoja blanca (`hoja`) con sombra de hoja, sobre la mesa gris fría (`mesa`).
- **Do** reservar el rojo corrector (`rojo`) para alertas, errores y borrar, y el azul de editor (`azul`) para enlaces, foco, nombres con ficha y estado guardado.
- **Do** componer el manuscrito en Literata 1.16rem con interlineado 1.85 y medida máxima de 40rem.
- **Do** colocar cada nota de PlotNode en la columna de margen de 15rem dentro de la hoja, alineada con su párrafo y unida a la palabra por un trazo de lápiz.
- **Do** dibujar iconos y marcas como trazos SVG con extremos redondeados (1.6–2.4px), heredando `currentColor`.
- **Do** usar 6px de radio para controles y 3px para hojas, y filetes de 1px para separar.
- **Do** redefinir los mismos tokens para el modo nocturno en lugar de crear colores nuevos: mesa y hoja grafito, lápices aclarados.
- **Do** desactivar transiciones y animaciones con `prefers-reduced-motion: reduce`.

### Don't:
- **Don't** construir el editor como una tarjeta flotante sobre gris neutro con barra de herramientas encima; la barra de formato vive sobre la mesa, sin caja.
- **Don't** introducir un tercer color con tono ni usar el rojo o el azul como decoración, fondo de sección o acento de marca (el nodo rojo del logotipo es la única excepción).
- **Don't** abrir paneles flotantes, tarjetas aparte o modales para mostrar fichas o alertas; van al margen.
- **Don't** dar sombra a botones, mensajes, notas o al riel; solo la hoja se levanta.
- **Don't** componer notas al margen o etiquetas de interfaz en Literata, ni el manuscrito en sans.
- **Don't** animar nada salvo el trazo de la marca al aparecer.
- **Don't** usar iconos de fuente, emoji ni ilustraciones caricaturescas; el registro es el de una mesa de corrección, no el de una app infantil.
