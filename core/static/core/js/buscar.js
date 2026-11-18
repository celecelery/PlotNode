/* PlotNode — Buscar y reemplazar en el capítulo (Ctrl+H), aparte de las muletillas (HU-31).
   Los cambios entran como ediciones normales del editor, así que el autoguardado los guarda. */
(function () {
  "use strict";
  const P = window.plotnode;
  const dlg = document.getElementById("dlg-buscar");
  if (!P || !P.quill || !dlg || typeof dlg.showModal !== "function") return;
  const quill = P.quill;
  const $ = (id) => document.getElementById(id);
  const campoBuscar = $("bus-texto"), campoReempl = $("bus-reemplazo"), casilla = $("bus-mayusculas");
  const cuenta = $("bus-cuenta"), aviso = $("bus-aviso");
  const escapar = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  function coincidencias() {
    const q = campoBuscar.value;
    if (!q) return [];
    const re = new RegExp(escapar(q), casilla.checked ? "g" : "gi");
    const texto = quill.getText();
    const lista = [];
    let m;
    while ((m = re.exec(texto)) !== null) { lista.push({ i: m.index, n: m[0].length }); if (!m[0].length) re.lastIndex++; }
    return lista;
  }
  function actualizar() {
    const n = coincidencias().length;
    cuenta.textContent = campoBuscar.value ? (n === 1 ? "1 coincidencia" : n + " coincidencias") : "";
    $("bus-siguiente").disabled = $("bus-reemplazar").disabled = $("bus-todo").disabled = n === 0;
  }
  function decir(t) { aviso.textContent = t; }

  let ultimo = 0;   // dónde buscar la siguiente
  function siguiente() {
    const lista = coincidencias();
    if (!lista.length) return null;
    const m = lista.find((x) => x.i >= ultimo) || lista[0];
    ultimo = m.i + m.n;
    quill.setSelection(m.i, m.n, "silent");
    return m;
  }
  function reemplazarUna() {
    const sel = quill.getSelection();
    let m = null;
    if (sel && sel.length) {
      const tomado = quill.getText(sel.index, sel.length);
      const igual = casilla.checked ? tomado === campoBuscar.value : tomado.toLowerCase() === campoBuscar.value.toLowerCase();
      if (igual) m = { i: sel.index, n: sel.length };
    }
    if (!m) { m = siguiente(); if (!m) return; }
    cambiar(m);
    ultimo = m.i + campoReempl.value.length;
    decir("Reemplazada 1 coincidencia.");
    siguiente();
  }
  function cambiar(m) {
    const formato = quill.getFormat(m.i, Math.max(1, m.n));
    quill.deleteText(m.i, m.n, "user");
    if (campoReempl.value) quill.insertText(m.i, campoReempl.value, formato, "user");
  }
  function reemplazarTodas() {
    const lista = coincidencias();
    for (let k = lista.length - 1; k >= 0; k--) cambiar(lista[k]);   // de atrás hacia adelante: los índices no se mueven
    decir(lista.length === 1 ? "Reemplazada 1 coincidencia." : "Reemplazadas " + lista.length + " coincidencias.");
    ultimo = 0;
  }

  function abrir() {
    const sel = quill.getSelection();
    if (sel && sel.length && sel.length < 80) campoBuscar.value = quill.getText(sel.index, sel.length);
    decir("");
    ultimo = sel ? sel.index : 0;
    if (!dlg.open) dlg.showModal();
    actualizar();
    campoBuscar.focus();
    campoBuscar.select();
  }
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === "h") { e.preventDefault(); e.stopPropagation(); abrir(); }
  }, true);   // en captura: Quill asocia Ctrl+H a «borrar»
  const abrirBoton = $("btn-buscar");
  if (abrirBoton) abrirBoton.addEventListener("click", abrir);
  $("bus-cerrar").addEventListener("click", () => dlg.close());
  $("bus-siguiente").addEventListener("click", () => { decir(""); siguiente(); });
  $("bus-reemplazar").addEventListener("click", reemplazarUna);
  $("bus-todo").addEventListener("click", reemplazarTodas);
  campoBuscar.addEventListener("input", function () { decir(""); ultimo = 0; actualizar(); });
  casilla.addEventListener("change", function () { ultimo = 0; actualizar(); });
  campoBuscar.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); decir(""); siguiente(); } });
  quill.on("text-change", function () { if (dlg.open) actualizar(); });
})();
