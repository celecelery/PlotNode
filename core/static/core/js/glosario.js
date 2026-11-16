/* PlotNode — glosario en el editor: lista, marcado de palabras y definición al pasar el cursor (HU-29, HU-30) */
(function () {
  "use strict";

  const P = window.plotnode;
  if (!P || !P.util || !P.panel) return;
  const quill = P.quill;
  const { el, normalizar, csrf, $ } = P.util;
  const raiz = $("reparto");
  const urlApi = raiz.dataset.urlGlosarioApi;
  const urlBorrar = (id) => raiz.dataset.urlGlosarioBorrar.replace(/\/0\/borrar\/$/, "/" + id + "/borrar/");
  const MAX_CARACTERES = 80;
  const MAX_PALABRAS = 6;

  let terminos = JSON.parse($("terminos-inicial").textContent || "[]");
  let pendiente = null;      // selección del texto que se marcará al guardar el término nuevo
  let editando = null;       // término que se está editando (o null si es nuevo)

  const lista = $("glosario-lista");
  const vacio = $("glosario-vacio");
  const buscador = $("glosario-buscar");
  const formulario = $("glosario-form");
  const aviso = $("glosario-aviso");
  const porId = () => new Map(terminos.map((t) => [String(t.id), t]));

  function decir(texto) {
    aviso.textContent = texto;
    aviso.hidden = !texto;
  }

  // --- Marcas en el texto ---------------------------------------------------------
  function marcar(rango, id) {
    quill.formatText(rango.index, rango.length, "termino", String(id), "user");
  }
  function recorrerMarcas(callback) {
    let posicion = 0;
    quill.getContents().ops.forEach(function (op) {
      const largo = typeof op.insert === "string" ? op.insert.length : 1;
      if (op.attributes && op.attributes.termino) callback(String(op.attributes.termino), posicion, largo);
      posicion += largo;
    });
  }
  function quitarMarcas(id) {
    recorrerMarcas(function (valor, inicio, largo) {
      if (valor === String(id)) quill.formatText(inicio, largo, "termino", false, "user");
    });
  }
  // Marcas de términos que ya no existen: se limpian al abrir el capítulo.
  (function limpiarHuerfanas() {
    const conocidos = porId();
    recorrerMarcas(function (valor, inicio, largo) {
      if (!conocidos.has(valor)) quill.formatText(inicio, largo, "termino", false, "silent");
    });
  })();

  // --- Lista del panel ----------------------------------------------------------------
  function render() {
    const q = normalizar(buscador.value);
    const visibles = terminos.filter((t) => !q || normalizar(t.nombre).includes(q) || normalizar(t.definicion).includes(q));
    lista.replaceChildren(...visibles.map(function (t) {
      const editar = el("button", { type: "button", class: "boton-texto", texto: "Editar" });
      const eliminar = el("button", { type: "button", class: "boton-texto boton-texto-coral", texto: "Eliminar" });
      const acciones = el("div", { class: "ficha-acciones" }, editar, eliminar);
      editar.addEventListener("click", () => abrirFormulario(t));
      eliminar.addEventListener("click", () => confirmarEliminar(t, acciones));
      return el("li", { class: "termino-item" },
        el("h4", { texto: t.nombre }),
        t.categoria ? el("p", { class: "ficha-meta", texto: t.categoria }) : null,
        el("p", { class: "termino-definicion", texto: t.definicion }),
        acciones);
    }));
    vacio.hidden = terminos.length > 0;
    vacio.textContent = "Aún no hay términos.";
    if (terminos.length > 0 && visibles.length === 0) { vacio.hidden = false; vacio.textContent = "Ningún término coincide con tu búsqueda."; }
  }
  buscador.addEventListener("input", render);

  function confirmarEliminar(t, acciones) {
    const si = el("button", { type: "button", class: "boton boton-coral boton-chico", texto: "Sí, eliminar" });
    const no = el("button", { type: "button", class: "boton boton-borde boton-chico", texto: "Cancelar" });
    acciones.replaceChildren(el("span", { class: "ficha-confirmar", texto: "¿Eliminar «" + t.nombre + "»?" }), si, no);
    no.addEventListener("click", render);
    si.addEventListener("click", async function () {
      si.disabled = true;
      try {
        const resp = await fetch(urlBorrar(t.id), { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrf } });
        if (!resp.ok) throw new Error();
        quitarMarcas(t.id);
        terminos = terminos.filter((x) => x.id !== t.id);
        render();
        decir("Término «" + t.nombre + "» eliminado.");
      } catch (err) {
        si.disabled = false;
        decir("No se pudo eliminar. Inténtalo de nuevo.");
      }
    });
  }

  // --- Formulario -----------------------------------------------------------------------
  function errores(lista) {
    const caja = $("glosario-errores");
    caja.textContent = lista.join(" ");
    caja.hidden = lista.length === 0;
  }
  function abrirFormulario(termino, nombreInicial) {
    editando = termino && termino.id ? termino : null;
    $("glosario-form-titulo").textContent = editando ? "Editar «" + editando.nombre + "»" : "Nuevo término";
    $("g-nombre").value = editando ? editando.nombre : (nombreInicial || "");
    $("g-definicion").value = editando ? editando.definicion : "";
    $("g-categoria").value = editando ? editando.categoria : "";
    errores([]);
    formulario.hidden = false;
    $("glosario-nuevo").hidden = true;
    (nombreInicial ? $("g-definicion") : $("g-nombre")).focus();
  }
  function cerrarFormulario() {
    formulario.hidden = true;
    $("glosario-nuevo").hidden = false;
    pendiente = null;
    editando = null;
  }
  $("glosario-nuevo").addEventListener("click", () => { decir(""); abrirFormulario(null); });
  $("glosario-cancelar").addEventListener("click", cerrarFormulario);

  formulario.addEventListener("submit", async function (e) {
    e.preventDefault();
    const boton = formulario.querySelector('button[type="submit"]');
    boton.disabled = true;
    try {
      const resp = await fetch(urlApi, {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({
          id: editando ? editando.id : null,
          nombre: $("g-nombre").value, definicion: $("g-definicion").value, categoria: $("g-categoria").value,
        }),
      });
      const datos = await resp.json().catch(() => ({}));
      if (resp.status === 400 && datos.errores) {
        errores(Object.values(datos.errores).flat());
        return;
      }
      if (!resp.ok) throw new Error();
      const guardado = datos.termino;
      const i = terminos.findIndex((x) => x.id === guardado.id);
      if (i >= 0) terminos[i] = guardado; else terminos.push(guardado);
      terminos.sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
      if (pendiente && !editando) {
        const mismoTexto = normalizar(quill.getText(pendiente.index, pendiente.length)) === normalizar(guardado.nombre);
        if (mismoTexto) { marcar(pendiente, guardado.id); decir("«" + guardado.nombre + "» quedó en el glosario y marcada en el texto."); }
        else decir("«" + guardado.nombre + "» quedó en el glosario. El texto cambió: vuelve a seleccionar la palabra para marcarla.");
      } else {
        decir("Término guardado.");
      }
      cerrarFormulario();
      render();
    } catch (err) {
      errores(["No se pudo guardar. Revisa tu conexión e inténtalo de nuevo."]);
    } finally {
      boton.disabled = false;
    }
  });

  // --- Botón «Añadir al glosario» de la barra (HU-30) -----------------------------------
  P.accionGlosario = function () {
    const rango = quill.getSelection();
    P.panel.abrir("glosario");
    if (!rango || rango.length === 0) { decir("Selecciona primero una palabra o frase del texto."); return; }
    const texto = quill.getText(rango.index, rango.length).replace(/\s+/g, " ").trim();
    if (!texto || texto.length > MAX_CARACTERES || texto.split(" ").length > MAX_PALABRAS) {
      decir("Selecciona solo una palabra o una frase corta (hasta 6 palabras).");
      return;
    }
    const existente = terminos.find((t) => normalizar(t.nombre) === normalizar(texto));
    if (existente) {
      marcar({ index: rango.index, length: rango.length }, existente.id);
      decir("«" + texto + "» ya estaba en el glosario: quedó marcada en el texto.");
      return;
    }
    decir("");
    pendiente = { index: rango.index, length: rango.length };
    abrirFormulario(null, texto);
  };

  // --- Definición al pasar el cursor --------------------------------------------------------
  const tooltip = $("tooltip-glosario");
  function mostrar(marca) {
    const t = porId().get(marca.getAttribute("data-termino"));
    if (!t) return;
    tooltip.replaceChildren(
      el("strong", { texto: t.nombre }),
      t.categoria ? el("span", { class: "tooltip-categoria", texto: t.categoria }) : null,
      el("span", { class: "tooltip-definicion", texto: t.definicion }));
    tooltip.hidden = false;
    const caja = marca.getBoundingClientRect();
    const ancho = tooltip.offsetWidth;
    const izquierda = Math.max(12, Math.min(window.innerWidth - ancho - 12, caja.left));
    const abajo = caja.bottom + 8;
    const arriba = caja.top - tooltip.offsetHeight - 8;
    tooltip.style.left = izquierda + "px";
    tooltip.style.top = (abajo + tooltip.offsetHeight > window.innerHeight && arriba > 8 ? arriba : abajo) + "px";
  }
  quill.root.addEventListener("mouseover", function (e) {
    const marca = e.target.closest && e.target.closest(".glosario");
    if (marca) mostrar(marca);
  });
  quill.root.addEventListener("mouseout", function (e) {
    if (e.target.closest && e.target.closest(".glosario")) tooltip.hidden = true;
  });
  quill.root.addEventListener("scroll", () => { tooltip.hidden = true; }, true);

  render();
})();
