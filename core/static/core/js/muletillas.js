/* PlotNode — muletillas: palabras repetidas, resaltado, sinónimos y reemplazo (HU-28) */
(function () {
  "use strict";

  const P = window.plotnode;
  if (!P || !P.util || !P.panel || !window.PlotNodeSinonimos) return;
  const quill = P.quill;
  const { el, normalizar, $ } = P.util;
  const Delta = Quill.import("delta");

  const PALABRA = /[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu;
  const MAX_LISTA = 25;
  const STOP = new Set(("el la los las un una unos unas lo al del de a en y e o u ni que se no si me te nos os le les mi tu su mis tus sus " +
    "yo tu el ella ello ellos ellas usted ustedes nosotros nosotras vosotros por para con sin sobre entre hasta desde hacia contra " +
    "es era eras eran fue fueron son soy eres ser sido siendo esta estaba estaban estar estoy estan estado esto eso ese esa esos esas este estos estas " +
    "aquel aquella aquello aquellos aquellas ha han he has hemos habia habian haber hay hubo mas menos ya tan tanto tanta cual cuales quien quienes " +
    "cuando donde como porque aunque otro otra otros otras cada todo toda todos todas algun alguna algunos algunas ningun ninguna mismo misma " +
    "tiene tienen tener tengo puede pueden poder podia va van ir voy iba ver").split(" "));

  const lista = $("muletillas-lista");
  const detalle = $("muletillas-detalle");
  const vacio = $("muletillas-vacio");
  const umbralEntrada = $("muletillas-umbral");
  const guardado = parseInt(P.util.leerLocal("muletillas-umbral") || "", 10);
  if (guardado >= 2 && guardado <= 50) umbralEntrada.value = String(guardado);

  let datos = [];            // [{clave, etiqueta, apariciones:[{index,length}]}]
  let elegida = null;        // clave de la palabra elegida
  let actual = 0;            // aparición actual de la palabra elegida
  let sucio = true;          // el texto cambió desde la última revisión

  const umbral = () => Math.max(2, Math.min(50, parseInt(umbralEntrada.value, 10) || 4));

  // quill.getText() omite imágenes y separadores: sus posiciones no coincidirían con las del documento.
  // Aquí cada elemento incrustado cuenta como un carácter, igual que en el documento.
  function textoDelDocumento() {
    let texto = "";
    quill.getContents().ops.forEach(function (op) { texto += typeof op.insert === "string" ? op.insert : "\uFFFC"; });
    return texto;
  }

  function analizar() {
    const texto = textoDelDocumento();
    const palabras = new Map();
    for (const m of texto.matchAll(PALABRA)) {
      const clave = normalizar(m[0]);
      if (clave.length < 3 || /^\d+$/.test(clave) || STOP.has(clave)) continue;
      if (!palabras.has(clave)) palabras.set(clave, { clave: clave, etiqueta: m[0].toLowerCase(), apariciones: [] });
      palabras.get(clave).apariciones.push({ index: m.index, length: m[0].length });
    }
    datos = [...palabras.values()]
      .filter((p) => p.apariciones.length >= umbral())
      .sort((a, b) => b.apariciones.length - a.apariciones.length || a.clave.localeCompare(b.clave))
      .slice(0, MAX_LISTA);
    sucio = false;
  }

  // --- Resaltado sin tocar el texto (API de resaltados de CSS) ---------------------------
  const puedeResaltar = !!(window.CSS && CSS.highlights && typeof Highlight !== "undefined");
  function rangoDom(inicio, largo) {
    const a = quill.getLeaf(inicio);
    const b = quill.getLeaf(inicio + largo - 1);
    if (!a[0] || !b[0] || a[0].domNode.nodeType !== 3 || b[0].domNode.nodeType !== 3) return null;
    const r = document.createRange();
    r.setStart(a[0].domNode, a[1]);
    r.setEnd(b[0].domNode, b[1] + 1);
    return r;
  }
  function resaltar() {
    if (!puedeResaltar) return;
    CSS.highlights.delete("muletilla");
    CSS.highlights.delete("muletilla-actual");
    const palabra = datos.find((p) => p.clave === elegida);
    if (!palabra) return;
    const todos = palabra.apariciones.map((a) => rangoDom(a.index, a.length)).filter(Boolean);
    if (todos.length) CSS.highlights.set("muletilla", new Highlight(...todos));
    const ahora = palabra.apariciones[actual] && rangoDom(palabra.apariciones[actual].index, palabra.apariciones[actual].length);
    if (ahora) CSS.highlights.set("muletilla-actual", new Highlight(ahora));
  }
  function mostrarEnPantalla(aparicion) {
    const caja = quill.getBounds(aparicion.index, aparicion.length);
    const contenedor = quill.container.closest(".hoja-texto");
    if (!contenedor) return;
    const y = quill.container.getBoundingClientRect().top + caja.top;
    const marco = contenedor.getBoundingClientRect();
    if (y < marco.top + 40 || y > marco.bottom - 90) contenedor.scrollTop += y - (marco.top + marco.height / 3);
  }

  // --- Lista -------------------------------------------------------------------------------
  function dibujarLista() {
    lista.replaceChildren(...datos.map(function (p) {
      const boton = el("button", { type: "button", class: "muletilla-chip", "aria-pressed": String(p.clave === elegida) },
        el("span", { class: "muletilla-palabra", texto: p.etiqueta }),
        el("span", { class: "muletilla-cuenta", texto: "× " + p.apariciones.length }));
      boton.addEventListener("click", function () { elegir(p.clave); });
      return el("li", {}, boton);
    }));
    if (datos.length === 0) {
      vacio.hidden = false;
      vacio.textContent = quill.getText().trim().length < 40
        ? "Escribe un poco más y aquí aparecerán las palabras que se repiten."
        : "Ninguna palabra se repite " + umbral() + " veces o más. Baja el número para ver más.";
    } else {
      vacio.hidden = true;
    }
  }

  function elegir(clave) {
    elegida = clave === elegida ? null : clave;
    actual = 0;
    refrescar(true);
  }

  // --- Detalle: aparición, sinónimos y reemplazo ----------------------------------------------
  function dibujarDetalle() {
    const palabra = datos.find((p) => p.clave === elegida);
    if (!palabra) { detalle.hidden = true; detalle.replaceChildren(); return; }
    actual = Math.min(actual, palabra.apariciones.length - 1);
    const total = palabra.apariciones.length;
    const anterior = el("button", { type: "button", class: "boton boton-borde boton-chico", "aria-label": "Aparición anterior", texto: "←" });
    const siguiente = el("button", { type: "button", class: "boton boton-borde boton-chico", "aria-label": "Aparición siguiente", texto: "→" });
    anterior.addEventListener("click", () => ir((actual + total - 1) % total));
    siguiente.addEventListener("click", () => ir((actual + 1) % total));

    const sugerencias = window.PlotNodeSinonimos.de(palabra.clave);
    const entrada = el("input", { type: "text", id: "muletillas-reemplazo", maxlength: "60", autocomplete: "off", placeholder: "Escribe o elige una alternativa" });
    const esta = el("button", { type: "button", class: "boton boton-lila-borde boton-chico", texto: "Reemplazar esta", disabled: "" });
    const todas = el("button", { type: "button", class: "boton boton-borde boton-chico", texto: "Reemplazar las " + total, disabled: "" });
    entrada.addEventListener("input", function () {
      const vacia = !entrada.value.trim();
      esta.disabled = vacia; todas.disabled = vacia;
    });
    esta.addEventListener("click", () => reemplazar([palabra.apariciones[actual]], entrada.value.trim()));
    todas.addEventListener("click", () => reemplazar(palabra.apariciones, entrada.value.trim()));

    const chips = sugerencias.length
      ? el("div", { class: "sinonimos", role: "group", "aria-label": "Alternativas sugeridas" },
          ...sugerencias.map(function (s) {
            const chip = el("button", { type: "button", class: "sinonimo", texto: s });
            chip.addEventListener("click", function () { entrada.value = s; entrada.dispatchEvent(new Event("input")); entrada.focus(); });
            return chip;
          }))
      : el("p", { class: "reparto-nota", texto: "No tengo alternativas guardadas para esta palabra. Escribe la que prefieras." });

    detalle.replaceChildren(
      el("p", { class: "muletillas-titulo" }, el("strong", { texto: "«" + palabra.etiqueta + "»" }), document.createTextNode(" aparece " + total + " veces")),
      el("div", { class: "muletillas-nav" }, anterior,
        el("span", { class: "muletillas-posicion", "aria-live": "polite", texto: "Aparición " + (actual + 1) + " de " + total }), siguiente),
      chips,
      el("div", { class: "campo" }, el("label", { for: "muletillas-reemplazo", texto: "Reemplazar por" }), entrada),
      el("div", { class: "muletillas-acciones" }, esta, todas),
      el("p", { class: "reparto-nota", texto: "Revisa el género y el número antes de reemplazar." }));
    detalle.hidden = false;
  }

  function ir(i) {
    actual = i;
    const palabra = datos.find((p) => p.clave === elegida);
    if (!palabra) return;
    dibujarDetalle();
    resaltar();
    mostrarEnPantalla(palabra.apariciones[actual]);
  }

  // --- Reemplazo (se guarda con el autoguardado) -------------------------------------------------
  function igualarMayusculas(original, nuevo) {
    return original[0] !== original[0].toLowerCase() ? nuevo.charAt(0).toUpperCase() + nuevo.slice(1) : nuevo;
  }
  function reemplazar(apariciones, texto) {
    if (!texto) return;
    // De la última a la primera: los índices de las anteriores no cambian.
    [...apariciones].sort((a, b) => b.index - a.index).forEach(function (a) {
      const original = quill.getText(a.index, a.length);
      const formatos = quill.getFormat(a.index, a.length);
      quill.updateContents(new Delta().retain(a.index).delete(a.length).insert(igualarMayusculas(original, texto), formatos), "user");
    });
    refrescar(true);
  }

  function refrescar(conservarEleccion) {
    analizar();
    if (conservarEleccion && !datos.some((p) => p.clave === elegida)) elegida = null;
    dibujarLista();
    dibujarDetalle();
    resaltar();
    const palabra = datos.find((p) => p.clave === elegida);
    if (palabra && palabra.apariciones[actual]) mostrarEnPantalla(palabra.apariciones[actual]);
  }

  // --- Cuándo se recalcula --------------------------------------------------------------------------
  let temporizador = null;
  quill.on("text-change", function () {
    sucio = true;
    if (P.panel.pestana !== "muletillas") return;
    clearTimeout(temporizador);
    temporizador = setTimeout(() => refrescar(true), 600);
  });
  document.addEventListener("plotnode:pestana", function (e) {
    if (e.detail === "muletillas") { if (sucio) refrescar(true); else resaltar(); }
    else if (puedeResaltar) { CSS.highlights.delete("muletilla"); CSS.highlights.delete("muletilla-actual"); }
  });
  // El número se aplica mientras se escribe; al salir del campo no se vuelve a dibujar la lista
  // (si no, el primer clic sobre una palabra se perdería porque la lista cambia justo en ese momento).
  let umbralAplicado = umbral();
  let esperaUmbral = null;
  function aplicarUmbral() {
    const nuevo = umbral();
    if (nuevo === umbralAplicado) return;
    umbralAplicado = nuevo;
    P.util.guardarLocal("muletillas-umbral", String(nuevo));
    refrescar(true);
  }
  umbralEntrada.addEventListener("input", function () { clearTimeout(esperaUmbral); esperaUmbral = setTimeout(aplicarUmbral, 350); });
  umbralEntrada.addEventListener("change", aplicarUmbral);
})();
