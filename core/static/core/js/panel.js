/* PlotNode — panel lateral deslizable: pestañas, ancho ajustable y fichas (HU-09, HU-10, HU-25, HU-26) */
(function () {
  "use strict";

  const P = window.plotnode;
  const raiz = document.getElementById("reparto");
  if (!raiz || !P || !P.quill) return;

  const quill = P.quill;
  const area = document.getElementById("area-editor");
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const $ = (id) => document.getElementById(id);

  // Todo el texto de la usuaria entra por textContent: nada se interpreta como HTML.
  function el(etiqueta, atributos, ...hijos) {
    const nodo = document.createElement(etiqueta);
    Object.entries(atributos || {}).forEach(([k, v]) => {
      if (k === "texto") nodo.textContent = v;
      else nodo.setAttribute(k, v);
    });
    hijos.forEach((h) => h && nodo.appendChild(h));
    return nodo;
  }
  const normalizar = (t) =>
    t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, " ").trim();
  function guardarLocal(clave, valor) { try { localStorage.setItem("plotnode." + clave, valor); } catch (e) { /* sin almacenamiento */ } }
  function leerLocal(clave) { try { return localStorage.getItem("plotnode." + clave); } catch (e) { return null; } }
  P.util = { el: el, normalizar: normalizar, csrf: csrf, $: $, guardarLocal: guardarLocal, leerLocal: leerLocal };

  // =====================================================================================
  // Mostrar u ocultar la barra de herramientas vertical (HU-27)
  // =====================================================================================
  const panelTexto = $("panel-texto");
  const botonBarra = $("btn-barra");
  function fijarBarra(visible, recordar) {
    panelTexto.dataset.barra = visible ? "visible" : "oculta";
    botonBarra.setAttribute("aria-pressed", String(visible));
    if (recordar) guardarLocal("barra", visible ? "visible" : "oculta");
  }
  botonBarra.addEventListener("click", () => fijarBarra(panelTexto.dataset.barra !== "visible", true));
  if (leerLocal("barra") !== "visible") fijarBarra(false, false);

  // =====================================================================================
  // Abrir, cerrar y ajustar el ancho del panel (HU-26)
  // =====================================================================================
  const estrecho = window.matchMedia("(max-width: 1000px)");
  const botonReparto = $("btn-reparto");
  const MIN_ANCHO = 300;

  function abrir(pestana) {
    area.dataset.reparto = "abierto";
    raiz.removeAttribute("inert");
    botonReparto.setAttribute("aria-expanded", "true");
    if (pestana) activarPestana(pestana);
    if (!estrecho.matches) guardarLocal("reparto", "abierto");
    else $("tab-btn-" + P.panel.pestana).focus({ preventScroll: true });   // el cajón recibe el foco
  }
  function cerrar() {
    if (raiz.contains(document.activeElement)) botonReparto.focus();
    area.dataset.reparto = "plegado";
    raiz.setAttribute("inert", "");
    botonReparto.setAttribute("aria-expanded", "false");
    if (!estrecho.matches) guardarLocal("reparto", "plegado");
  }
  botonReparto.addEventListener("click", () => (area.dataset.reparto === "abierto" ? cerrar() : abrir()));
  $("reparto-plegar").addEventListener("click", cerrar);
  $("reparto-fondo").addEventListener("click", cerrar);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && estrecho.matches && area.dataset.reparto === "abierto") cerrar();
  });

  const maximo = () => Math.min(720, Math.floor(window.innerWidth * 0.6));
  function fijarAncho(px, recordar) {
    const ancho = Math.max(MIN_ANCHO, Math.min(maximo(), Math.round(px)));
    area.style.setProperty("--reparto-ancho", ancho + "px");
    $("reparto-asa").setAttribute("aria-valuenow", String(ancho));
    if (recordar) guardarLocal("reparto-ancho", String(ancho));
    return ancho;
  }
  const asa = $("reparto-asa");
  asa.setAttribute("aria-valuemin", String(MIN_ANCHO));
  asa.addEventListener("pointerdown", function (e) {
    e.preventDefault();
    asa.setPointerCapture(e.pointerId);
    area.classList.add("arrastrando");
  });
  asa.addEventListener("pointermove", function (e) {
    if (!area.classList.contains("arrastrando")) return;
    fijarAncho(window.innerWidth - 18 - e.clientX, false);
  });
  function soltarAsa(e) {
    if (!area.classList.contains("arrastrando")) return;
    area.classList.remove("arrastrando");
    fijarAncho(raiz.getBoundingClientRect().width, true);
    try { asa.releasePointerCapture(e.pointerId); } catch (err) { /* ya liberado */ }
  }
  asa.addEventListener("pointerup", soltarAsa);
  asa.addEventListener("pointercancel", soltarAsa);
  asa.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    e.preventDefault();
    const actual = raiz.getBoundingClientRect().width;
    fijarAncho(actual + (e.key === "ArrowLeft" ? 24 : -24), true);
  });
  const anchoGuardado = parseInt(leerLocal("reparto-ancho") || "", 10);
  if (anchoGuardado) fijarAncho(anchoGuardado, false);
  if (estrecho.matches || leerLocal("reparto") === "plegado") cerrar(); else raiz.removeAttribute("inert");
  estrecho.addEventListener("change", function () { if (estrecho.matches) cerrar(); else if (leerLocal("reparto") !== "plegado") abrir(); });

  // =====================================================================================
  // Pestañas: Fichas | Glosario | Notas | Muletillas
  // =====================================================================================
  const PESTANAS = ["fichas", "glosario", "notas", "muletillas"];
  function activarPestana(nombre) {
    PESTANAS.forEach(function (n) {
      const activa = n === nombre;
      const boton = $("tab-btn-" + n);
      boton.setAttribute("aria-selected", String(activa));
      boton.tabIndex = activa ? 0 : -1;
      $("tab-" + n).hidden = !activa;
    });
    P.panel.pestana = nombre;
    document.dispatchEvent(new CustomEvent("plotnode:pestana", { detail: nombre }));
  }
  PESTANAS.forEach(function (n, i) {
    const boton = $("tab-btn-" + n);
    boton.addEventListener("click", () => activarPestana(n));
    boton.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      const siguiente = PESTANAS[(i + (e.key === "ArrowRight" ? 1 : PESTANAS.length - 1)) % PESTANAS.length];
      activarPestana(siguiente);
      $("tab-btn-" + siguiente).focus();
    });
  });
  P.panel = { abrir: abrir, cerrar: cerrar, activarPestana: activarPestana, pestana: "fichas" };

  // =====================================================================================
  // Fichas: lista, detalle y formulario dentro del panel (HU-09, HU-25, HU-26, HU-08)
  // =====================================================================================
  const urls = {
    consulta: raiz.dataset.urlConsulta,
    nueva: raiz.dataset.urlFichaNueva,
    editar: (id) => raiz.dataset.urlFichaEditar.replace(/\/0\/$/, "/" + id + "/"),
    eliminar: (id) => raiz.dataset.urlFichaEliminar.replace(/\/0\/eliminar\/$/, "/" + id + "/eliminar/"),
  };
  const MAX_CARACTERES = 80;
  const MAX_PALABRAS = 6;
  const ESPERA_MS = 300;

  let fichas = JSON.parse($("fichas-inicial").textContent || "[]");
  const lista = $("reparto-lista");
  const detalle = $("reparto-detalle");
  const vacio = $("reparto-vacio");
  const sinResultados = $("reparto-sin-resultados");
  const buscador = $("reparto-buscar");
  const filtro = $("filtro-tipo");
  const vistaLista = $("fichas-lista-vista");
  const vistaForm = $("ficha-form-vista");

  function avatar(f, clase) {
    if (f.foto) return el("img", { class: "foto-ficha " + (clase || ""), src: f.foto, alt: "" });
    return el("span", { class: "inicial p-" + f.color + " " + (clase || ""), "aria-hidden": "true", texto: f.inicial });
  }

  function renderLista() {
    const q = normalizar(buscador.value);
    const tipo = filtro.value;
    const visibles = fichas.filter((f) =>
      (!tipo || f.tipo_clave === tipo) && (!q || [f.nombre, ...f.alias].some((n) => normalizar(n).includes(q))));
    lista.replaceChildren(...visibles.map((f) => {
      const boton = el("button", { type: "button", class: "ficha-chip" }, avatar(f), el("span", { texto: f.nombre }));
      boton.addEventListener("click", () => abrirDesdeLista(f));
      return el("li", {}, boton);
    }));
    vacio.hidden = fichas.length > 0;
    sinResultados.hidden = !(fichas.length > 0 && visibles.length === 0);
    document.dispatchEvent(new CustomEvent("plotnode:fichas"));   // nombres.js vuelve a subrayar
  }
  P.obtenerFichas = function () { return fichas; };

  // Personajes que aparecen en el capítulo actual (HU-11): nombre o alias como palabra completa.
  const presentes = $("presentes");
  const presentesLista = $("presentes-lista");
  const esLetra = /[\p{L}\p{N}]/u;
  function apareceEn(texto, nombre) {
    const n = normalizar((nombre || "").trim());
    if (n.length < 3) return false;
    let desde = 0;
    for (;;) {
      const i = texto.indexOf(n, desde);
      if (i < 0) return false;
      desde = i + 1;
      const fin = i + n.length;
      if (i > 0 && esLetra.test(texto[i - 1])) continue;
      if (fin < texto.length && esLetra.test(texto[fin])) continue;
      return true;
    }
  }
  function renderPresentes() {
    const texto = normalizar(P.quill.getText());
    const aparecen = fichas.filter((f) => f.tipo_clave === "personaje" && [f.nombre, ...(f.alias || [])].some((n) => apareceEn(texto, n)));
    presentesLista.replaceChildren(...aparecen.map((f) => {
      const boton = el("button", { type: "button", class: "ficha-chip" }, avatar(f), el("span", { texto: f.nombre }));
      boton.addEventListener("click", () => abrirDesdeLista(f));
      return el("li", {}, boton);
    }));
    presentes.hidden = aparecen.length === 0;
  }
  let temporizadorPresentes = null;
  P.quill.on("text-change", function () { clearTimeout(temporizadorPresentes); temporizadorPresentes = setTimeout(renderPresentes, 600); });
  document.addEventListener("plotnode:fichas", renderPresentes);
  renderPresentes();
  buscador.addEventListener("input", renderLista);
  filtro.addEventListener("change", renderLista);

  function guardarFichaLocal(f) {
    const i = fichas.findIndex((x) => x.id === f.id);
    if (i >= 0) fichas[i] = f; else fichas.push(f);
    fichas.sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
    renderLista();
  }

  function mostrarFicha(f) {
    const meta = [f.tipo, f.alias.length ? "Alias: " + f.alias.join(", ") : ""].filter(Boolean).join(" · ");
    const secciones = f.secciones.map(function (s) {
      const caja = el("details", { class: "ficha-seccion" }, el("summary", { texto: s.titulo }),
        el("dl", { class: "ficha-atributos" }, ...s.campos.flatMap((c) => [el("dt", { texto: c.etiqueta }), el("dd", { texto: c.valor })])));
      if (s.abierta) caja.open = true;
      return caja;
    });
    if (f.atributos.length) {
      secciones.push(el("details", { class: "ficha-seccion" }, el("summary", { texto: "Otros atributos" }),
        el("dl", { class: "ficha-atributos" }, ...f.atributos.flatMap((a) => [el("dt", { texto: a.clave }), el("dd", { texto: a.valor })]))));
    }
    const rels = f.relaciones || [];
    const cajaRel = el("details", { class: "ficha-seccion" },
      el("summary", { texto: "Relaciones" + (rels.length ? " (" + rels.length + ")" : "") }),
      rels.length
        ? el("ul", { class: "ficha-relaciones" }, ...rels.map((r) => el("li", {},
            el("span", { class: "punto-color p-" + r.color, "aria-hidden": "true" }),
            el("strong", { texto: r.con }), el("span", { class: "rel-tipo", texto: r.texto }))))
        : el("p", { class: "reparto-nota", texto: "Aún sin relaciones." }),
      el("a", { class: "enlace-relacion", href: f.url_relaciones, texto: "Añadir o ver relaciones →" }));
    if (rels.length) cajaRel.open = true;
    secciones.push(cajaRel);
    const sinDatos = !secciones.length && !f.notas
      ? el("p", { class: "reparto-nota", texto: "Esta ficha aún no tiene datos. Pulsa «Editar ficha» para completarla." }) : null;
    const editar = el("button", { type: "button", class: "boton boton-lila-borde boton-chico", texto: "Editar ficha" });
    const eliminar = el("button", { type: "button", class: "boton-texto boton-texto-coral", texto: "Eliminar" });
    const acciones = el("div", { class: "ficha-acciones" }, editar, eliminar);
    editar.addEventListener("click", () => abrirFormulario(urls.editar(f.id)));
    eliminar.addEventListener("click", function () { confirmarEliminar(f, acciones); });
    detalle.replaceChildren(
      el("article", { class: "ficha-detalle" },
        el("header", {}, avatar(f, "ficha-avatar"),
          el("div", {}, el("h3", { class: "nombre nombre-" + f.color, texto: f.nombre }), el("p", { class: "ficha-meta", texto: meta }))),
        ...secciones, sinDatos,
        f.notas ? el("p", { class: "ficha-notas", texto: f.notas }) : null,
        acciones));
  }

  function confirmarEliminar(f, acciones) {
    const si = el("button", { type: "button", class: "boton boton-coral boton-chico", texto: "Sí, eliminar" });
    const no = el("button", { type: "button", class: "boton boton-borde boton-chico", texto: "Cancelar" });
    acciones.replaceChildren(el("span", { class: "ficha-confirmar", texto: "¿Eliminar la ficha de " + f.nombre + "?" }), si, no);
    no.addEventListener("click", () => mostrarFicha(f));
    si.addEventListener("click", async function () {
      si.disabled = true;
      try {
        const resp = await fetch(urls.eliminar(f.id), {
          method: "POST", credentials: "same-origin",
          headers: { "X-CSRFToken": csrf, "X-Requested-With": "fetch" },
        });
        if (!resp.ok) throw new Error();
        fichas = fichas.filter((x) => x.id !== f.id);
        renderLista();
        detalle.replaceChildren(el("p", { class: "reparto-nota", texto: "Ficha eliminada." }));
      } catch (err) {
        si.disabled = false;
        acciones.appendChild(el("span", { class: "reparto-nota", texto: "No se pudo eliminar. Inténtalo de nuevo." }));
      }
    });
  }

  // Abrir desde la lista: pide la ficha fresca, pero no cuenta como consulta contextual.
  async function abrirDesdeLista(f) {
    mostrarFicha(f);
    try {
      const resp = await fetch(urls.consulta + "?registrar=0&nombre=" + encodeURIComponent(f.nombre), { credentials: "same-origin" });
      const datos = await resp.json();
      if (datos.encontrada) mostrarFicha(datos.ficha);
    } catch (err) { /* se queda con la copia local */ }
  }

  // --- Formulario dentro del panel (sin cambiar de página) ---
  function verLista() { vistaForm.hidden = true; vistaLista.hidden = false; }
  function verFormulario() { vistaLista.hidden = true; vistaForm.hidden = false; }

  function montarFormulario(html) {
    vistaForm.innerHTML = html; // fragmento HTML de nuestro servidor (Django escapa los datos)
    const form = vistaForm.querySelector("[data-form-ficha]");
    const volver = el("button", { type: "button", class: "reparto-volver", texto: "← Volver a las fichas" });
    volver.addEventListener("click", verLista);
    vistaForm.insertBefore(volver, vistaForm.firstChild);
    if (!form) return;
    window.PlotNodeFichaForm.preparar(form);
    form.addEventListener("submit", enviarFormulario);
    const cancelar = form.querySelector("[data-cancelar]");
    if (cancelar) cancelar.addEventListener("click", verLista);
    const error = form.querySelector(".errorlist");
    (error ? error : form.querySelector("input[type=text]")).scrollIntoView({ block: "center" });
    const primero = form.querySelector(".errorlist ~ input, .errorlist ~ textarea") || form.querySelector("#id_nombre");
    if (primero && !error) primero.focus({ preventScroll: true });
  }

  async function abrirFormulario(url) {
    abrir("fichas");
    activarPestana("fichas");
    vistaForm.replaceChildren(el("p", { class: "reparto-nota", texto: "Cargando el formulario…" }));
    verFormulario();
    try {
      const resp = await fetch(url, { credentials: "same-origin", headers: { "X-Requested-With": "fetch" } });
      if (!resp.ok) throw new Error();
      montarFormulario(await resp.text());
    } catch (err) {
      const volver = el("button", { type: "button", class: "boton boton-borde boton-chico", texto: "Volver a las fichas" });
      volver.addEventListener("click", verLista);
      vistaForm.replaceChildren(el("p", { class: "reparto-nota", texto: "No pude abrir el formulario. Inténtalo de nuevo." }), volver);
    }
  }

  async function enviarFormulario(e) {
    e.preventDefault();
    const form = e.currentTarget;
    const boton = form.querySelector('button[type="submit"]');
    boton.disabled = true;
    boton.textContent = "Guardando…";
    try {
      const resp = await fetch(form.action, {
        method: "POST", body: new FormData(form), credentials: "same-origin",
        headers: { "X-Requested-With": "fetch", "X-CSRFToken": csrf },
      });
      if (resp.ok) {
        const datos = await resp.json();
        guardarFichaLocal(datos.ficha);
        verLista();
        mostrarFicha(datos.ficha);
        detalle.scrollIntoView({ block: "nearest" });
      } else if (resp.status === 422) {
        montarFormulario(await resp.text());
      } else {
        throw new Error();
      }
    } catch (err) {
      boton.disabled = false;
      boton.textContent = "Guardar ficha";
      form.insertBefore(el("p", { class: "errorlist", texto: "No se pudo guardar. Revisa tu conexión e inténtalo de nuevo." }), form.firstChild);
    }
  }

  raiz.querySelectorAll("[data-nueva]").forEach(function (boton) {
    boton.addEventListener("click", () => abrirFormulario(urls.nueva + "?tipo=" + boton.dataset.nueva));
  });

  function mostrarSinFicha(nombre) {
    const crear = el("button", { type: "button", class: "boton boton-lila-borde", texto: "Crear ficha con este nombre" });
    crear.addEventListener("click", () => abrirFormulario(urls.nueva + "?tipo=personaje&nombre=" + encodeURIComponent(nombre)));
    detalle.replaceChildren(
      el("div", { class: "ficha-detalle ficha-detalle-vacia" },
        el("p", {}, el("strong", { texto: "«" + nombre + "»" }), document.createTextNode(" no tiene ficha todavía.")), crear));
  }

  // --- Ficha automática al seleccionar un nombre (HU-10) ---
  let temporizador = null;
  let ultimaSeleccion = "";
  let peticion = 0;

  async function consultar() {
    const rango = quill.getSelection();
    if (!rango || rango.length === 0) return;
    const texto = quill.getText(rango.index, rango.length).replace(/\s+/g, " ").trim();
    if (!texto || texto.length > MAX_CARACTERES || texto.split(" ").length > MAX_PALABRAS) return;
    const clave = rango.index + ":" + rango.length;
    if (clave === ultimaSeleccion) return;     // misma selección: no se cuenta dos veces
    ultimaSeleccion = clave;
    const mia = ++peticion;
    try {
      const resp = await fetch(urls.consulta + "?nombre=" + encodeURIComponent(texto), { credentials: "same-origin" });
      if (!resp.ok) throw new Error();
      const datos = await resp.json();
      if (mia !== peticion) return;            // llegó una selección más nueva
      const enFichas = !vistaLista.hidden && P.panel.pestana === "fichas" && area.dataset.reparto === "abierto";
      if (datos.encontrada) {
        guardarFichaLocal(datos.ficha);
        // Si está llenando un formulario no se lo quitamos; si el panel está cerrado, la ficha queda lista para cuando lo abra.
        if (vistaLista.hidden) return;
        mostrarFicha(datos.ficha);   // sin cambiar de pestaña: quien está en Glosario o Muletillas sigue ahí
      } else if (enFichas && texto.split(" ").length <= 4) {   // frases largas no son nombres: no ofrecer «crear ficha»
        mostrarSinFicha(datos.nombre || texto);
      }
    } catch (err) {
      if (mia === peticion && area.dataset.reparto === "abierto" && P.panel.pestana === "fichas") {
        detalle.replaceChildren(el("p", { class: "reparto-nota", texto: "No pude consultar la ficha. Inténtalo de nuevo." }));
      }
    }
  }

  quill.on("selection-change", function (rango) {
    clearTimeout(temporizador);
    if (!rango || rango.length === 0) { ultimaSeleccion = ""; return; }
    temporizador = setTimeout(consultar, ESPERA_MS);
  });

  renderLista();
})();
