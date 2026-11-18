/* Barra de formato rápida, flotante sobre el área de escritura. Usa el mismo Quill del editor. */
(function () {
  "use strict";
  var barra = document.getElementById("barra-rapida");
  var P = window.plotnode;
  if (!barra || !P || !P.quill) return;
  var quill = P.quill;
  var ALINEACIONES = [["", "izquierda"], ["center", "centro"], ["right", "derecha"], ["justify", "justificada"]];

  // Los botones no le quitan la selección al texto.
  barra.addEventListener("mousedown", function (e) { if (e.target.closest("button")) e.preventDefault(); });

  function alternar(nombre, valor) {
    var f = quill.getFormat();
    var actual = f[nombre];
    var nuevo = valor === undefined ? !actual : (actual === valor ? false : valor);
    quill.format(nombre, nuevo, "user");
  }

  barra.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b || !quill.hasFocus() && !quill.getSelection()) { if (b) quill.focus(); }
    if (!b) return;
    var formato = b.getAttribute("data-formato"), accion = b.getAttribute("data-accion");
    if (formato) { alternar(formato, b.getAttribute("data-valor") || undefined); }
    else if (accion === "undo") quill.history.undo();
    else if (accion === "redo") quill.history.redo();
    else if (accion === "link") {
      var r = quill.getSelection(true);
      if (!r || !r.length) return;
      var url = window.prompt("Dirección del enlace (https://…)");
      if (url && /^https?:\/\//i.test(url.trim())) quill.format("link", url.trim(), "user");
    } else if (accion === "image") {
      var d = window.prompt("Dirección web de la imagen (https://…)");
      if (!d || !/^https?:\/\//i.test(d.trim())) return;
      var rg = quill.getSelection(true);
      quill.insertEmbed(rg.index, "image", d.trim(), "user");
    } else if (accion === "align") {
      var actual = quill.getFormat().align || "";
      var i = 0; ALINEACIONES.forEach(function (a, k) { if (a[0] === actual) i = k; });
      var sig = ALINEACIONES[(i + 1) % ALINEACIONES.length];
      quill.format("align", sig[0] || false, "user");
    }
    actualizar();
  });

  barra.querySelector("select[data-accion=header]").addEventListener("change", function (e) {
    quill.focus();
    quill.format("header", e.target.value ? parseInt(e.target.value, 10) : false, "user");
    actualizar();
  });

  function actualizar() {
    var f = quill.getFormat();
    barra.querySelectorAll("button[data-formato]").forEach(function (b) {
      var n = b.getAttribute("data-formato"), v = b.getAttribute("data-valor");
      b.setAttribute("aria-pressed", String(v ? f[n] === v : !!f[n]));
    });
    var h = barra.querySelector("select[data-accion=header]");
    h.value = f.header ? String(f.header) : "";
    var al = barra.querySelector("button[data-accion=align]");
    var etiqueta = "izquierda"; ALINEACIONES.forEach(function (a) { if (a[0] === (f.align || "")) etiqueta = a[1]; });
    al.setAttribute("aria-label", "Alineación: " + etiqueta + " (pulsa para cambiar)");
  }
  quill.on("editor-change", actualizar);
  actualizar();
})();
