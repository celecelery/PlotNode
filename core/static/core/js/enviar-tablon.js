/* PlotNode — «Enviar al tablón»: guarda el pasaje seleccionado como nota del tablón de ideas */
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
      decir("Enviado al tablón (" + (texto.length > 40 ? texto.slice(0, 40) + "…" : texto) + ").");
    } catch (e) {
      decir("No se pudo enviar. Inténtalo de nuevo.");
    } finally { boton.disabled = false; }
  });
})();
