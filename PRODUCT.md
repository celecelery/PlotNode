# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Escritores de ficción aficionados y emergentes que escriben en español: novelistas y autores de fanfic (Wattpad, AO3) con proyectos medianos o largos. Hoy escriben en Word o Google Docs y guardan sus datos de personajes en libretas, notas del celular o apps separadas; pierden el hilo, olvidan rasgos o cronologías y llegan a abandonar historias. Gastan $0 en herramientas.

## Product Purpose

PlotNode une el manuscrito y las fichas de personajes y contexto en una sola pantalla. Al seleccionar un nombre, su ficha aparece al lado; al pulsar un botón, un auditor con IA señala si el párrafo contradice lo que el autor ya definió. Éxito del MVP: al menos 4 de 6 escritores de prueba redactan un capítulo completo en la plataforma y consultan o verifican fichas 3 veces o más sin abrir herramientas externas.

## Positioning

La IA no escribe por el autor: solo cuida la coherencia de lo que el autor ya decidió. En español, simple y gratis para empezar, frente a herramientas potentes pero complejas, en inglés y de pago (Scrivener, Novelcrafter, Sudowrite).

## Operating Context

Sesiones largas de escritura en computadora de escritorio o laptop, muchas veces de noche. El escritor alterna entre redactar y consultar datos de su mundo (personajes, lugares, poderes, fechas). Proyecto escolar de Negocios Electrónicos (UAZ, Ingeniería de Software), presentado en una demo el 18 de noviembre de 2026.

## Capabilities and Constraints

- Hecho (iteración 1): cuentas (registro, login, recuperar contraseña), proyectos (crear, renombrar, eliminar), editor de texto enriquecido (Quill) con autoguardado y contador de palabras.
- Planeado: capítulos, fichas de personaje con alias y atributos, panel lateral que muestra la ficha al seleccionar un nombre, auditor de coherencia con la API gratuita de Gemini, tutorial guiado, aviso de privacidad.
- Stack: Django 5.2 + plantillas, JavaScript sin compilar, SQLite, PythonAnywhere gratuito. Costo total $0: sin servicios ni fuentes de pago.
- Interfaz y contenido 100% en español.

## Brand Commitments

- Nombre: PlotNode.
- Titular confirmado de la portada: «Escribe tu novela sin perderte en tus notas ni cometer errores de continuidad».
- Debe sentirse serio para alguien que escribe una novela: ni infantil ni caricaturesco.
- Nada genérico ni con apariencia de plantilla «hecha por IA».

## Evidence on Hand

- 6 entrevistas del segmento (`docs/entregables`): 5 de 6 pierden 3 horas o más por semana; 100% gasta $0; el auditor de continuidad es la función más pedida (4 de 6).
- No existen testimonios, usuarios, métricas de uso ni logos de clientes: no inventarlos.

## Product Principles

1. El texto del autor manda: la interfaz se retira mientras se escribe.
2. El contexto llega al autor, no al revés: fichas a un clic, sin cambiar de ventana.
3. Avisar, nunca escribir: la IA señala; el autor decide.
4. Confianza en la obra: guardado visible, privacidad explícita, la obra es del autor.

## Accessibility & Inclusion

Contraste legible en sesiones largas; navegación con teclado en el editor y los formularios; respetar `prefers-reduced-motion`.
