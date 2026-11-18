/* PlotNode — «Guardar como nota» (pasaje del texto) y pestaña «Notas» del panel: notas recientes y nota en blanco (HU-32) */
(function () {
  "use strict";
  const P = window.plotnode;
  const boton = document.getElementById("btn-tablon");
  const aviso = document.getElementById("tablon-aviso");
  if (!P || !P.quill || !boton) return;
  const quill = P.quill;
  let ultimo = null;   // la selección se pierde al pulsar el botón: se recuerda la última con texto

  quill.on("selection-change", function (rango) {
    if (rango && rango.length > 0) ultimo = rango;
    else if (rango) ultimo = null;
  });
  const csrf = () => decodeURIComponent((document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/) || [])[1] || "");
  function decir(t) { aviso.textContent = t; aviso.hidden = !t; }

  // --- Pestaña «Notas» del panel ---
  const U = P.util;
  const lista = document.getElementById("notas-lista");
  const vacio = document.getElementById("notas-vacio");
  const MAX = 8;
  let notas = JSON.parse((document.getElementById("notas-inicial") || {}).textContent || "[]");
  function renderNotas() {
    notas = notas.slice(0, MAX);
    lista.replaceChildren(...notas.map((n) => U.el("li", { class: "nota-mini" },
      U.el("a", { href: n.url, target: "_blank", rel: "noopener" },
        U.el("span", { class: "nota-mini-tipo", texto: n.tipo_texto }),
        U.el("span", { class: "nota-mini-texto", texto: n.contenido.length > 120 ? n.contenido.slice(0, 120) + "…" : n.contenido })))));
    vacio.hidden = notas.length > 0;
  }
  function agregarNota(n) { notas.unshift(n); renderNotas(); }
  renderNotas();

  const formRapido = document.getElementById("nota-rapida");
  const campoRapido = document.getElementById("nota-rapida-texto");
  const avisoRapido = document.getElementById("nota-rapida-aviso");
  formRapido.addEventListener("submit", async function (e) {
    e.preventDefault();
    const texto = campoRapido.value.trim();
    avisoRapido.hidden = false;
    if (!texto) { avisoRapido.textContent = "Escribe algo para la nota."; return; }
    try {
      const r = await fetch(boton.dataset.url, {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
        body: JSON.stringify({ texto: texto, capitulo: boton.dataset.capitulo, tipo: "idea" }),
      });
      if (!r.ok) throw new Error();
      agregarNota((await r.json()).nota);
      campoRapido.value = "";
      avisoRapido.textContent = "Nota guardada.";
    } catch (err) { avisoRapido.textContent = "No se pudo guardar. Inténtalo de nuevo."; }
  });

  // Arrastrar un fragmento seleccionado hasta el panel lo guarda como nota (HU-32).
  const panel = document.getElementById("reparto");
  async function guardarFragmento(texto) {
    texto = (texto || "").trim();
    if (!texto) return;
    try {
      const r = await fetch(boton.dataset.url, {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
        body: JSON.stringify({ texto: texto, capitulo: boton.dataset.capitulo }),
      });
      if (!r.ok) throw new Error();
      agregarNota((await r.json()).nota);
      if (P.panel && P.panel.activarPestana) P.panel.activarPestana("notas");
    } catch (err) { avisoRapido.hidden = false; avisoRapido.textContent = "No se pudo guardar el fragmento."; }
  }
  if (panel) {
    ["dragenter", "dragover"].forEach((ev) => panel.addEventListener(ev, function (e) {
      if (e.dataTransfer && Array.from(e.dataTransfer.types || []).includes("text/plain")) { e.preventDefault(); panel.classList.add("recibe-nota"); }
    }));
    ["dragleave", "drop"].forEach((ev) => panel.addEventListener(ev, () => panel.classList.remove("recibe-nota")));
    panel.addEventListener("drop", function (e) {
      const texto = e.dataTransfer && e.dataTransfer.getData("text/plain");
      if (!texto) return;
      e.preventDefault();
      guardarFragmento(texto);
    });
  }

  boton.addEventListener("mousedown", (e) => e.preventDefault());   // no robar el foco al editor
  boton.addEventListener("click", async function () {
    const rango = quill.getSelection() && quill.getSelection().length ? quill.getSelection() : ultimo;
    const texto = rango ? quill.getText(rango.index, rango.length).trim() : "";
    if (!texto) { decir("Selecciona primero un pasaje del texto."); return; }
    boton.disabled = true;
    try {
      const r = await fetch(boton.dataset.url, {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
        body: JSON.stringify({ texto: texto, capitulo: boton.dataset.capitulo }),
      });
      if (!r.ok) throw new Error();
      const datos = await r.json();
      if (datos.nota) agregarNota(datos.nota);
      decir("Guardado como nota (" + (texto.length > 40 ? texto.slice(0, 40) + "…" : texto) + ").");
    } catch (e) {
      decir("No se pudo enviar. Inténtalo de nuevo.");
    } finally { boton.disabled = false; }
  });
})();
