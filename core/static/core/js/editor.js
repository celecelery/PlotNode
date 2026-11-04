/* PlotNode — editor con autoguardado (HU-06) */
(function () {
  "use strict";

  const ESPERA_MS = 3000;      // guardar 3 s después de dejar de escribir
  const REINTENTO_MS = 5000;   // si falla, reintentar a los 5 s

  const contenedor = document.getElementById("editor");
  const urlGuardar = contenedor.dataset.urlGuardar;
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const elEstado = document.getElementById("estado-guardado");

  const quill = new Quill(contenedor, {
    theme: "snow",
    placeholder: "Empieza a escribir tu capítulo…",
    modules: {
      toolbar: "#barra-formato",   // barra propia en la parte superior de la mesa
    },
  });

  // Cargar el contenido guardado. clipboard.convert pasa el HTML por los formatos
  // permitidos de Quill, así que no se ejecuta ningún script incrustado.
  const inicial = JSON.parse(document.getElementById("contenido-inicial").textContent || '""');
  if (inicial) {
    quill.setContents(quill.clipboard.convert({ html: inicial }), "silent");
  }
  quill.focus();

  // --- Contador de palabras -------------------------------------------------
  const PALABRA = /[\p{L}\p{N}_'’-]+/gu;
  function contarPalabras() {
    const coincidencias = quill.getText().match(PALABRA);
    return coincidencias ? coincidencias.length : 0;
  }
  function actualizarContador() {
    const n = contarPalabras().toLocaleString("es-MX");
    document.querySelectorAll("[data-palabras]").forEach(function (el) { el.textContent = n; });
  }

  // --- Estado de guardado ---------------------------------------------------
  function mostrarEstado(estado, texto) {
    elEstado.dataset.estado = estado;
    elEstado.textContent = texto;
  }

  let temporizador = null;
  let hayCambios = false;
  let guardando = false;

  async function guardar() {
    clearTimeout(temporizador);
    if (!hayCambios) return;
    if (guardando) {                       // ya hay un guardado en curso: volver a intentar al terminar
      temporizador = setTimeout(guardar, 500);
      return;
    }
    guardando = true;
    hayCambios = false;
    mostrarEstado("guardando", "Guardando…");
    try {
      const resp = await fetch(urlGuardar, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({ contenido: quill.root.innerHTML }),
        credentials: "same-origin",
      });
      const datos = await resp.json().catch(() => ({}));
      if (!resp.ok || !datos.ok) throw new Error(datos.error || `Error ${resp.status}`);
      const enIndice = document.querySelector('.riel-capitulos [aria-current="page"] .cap-palabras');
      if (enIndice) enIndice.textContent = datos.palabras.toLocaleString("es-MX");
      mostrarEstado(hayCambios ? "pendiente" : "guardado",
                    hayCambios ? "Cambios sin guardar" : `Guardado a las ${datos.guardado}`);
    } catch (err) {
      hayCambios = true;
      mostrarEstado("error", "No se pudo guardar. Reintentando…");
      temporizador = setTimeout(guardar, REINTENTO_MS);
    } finally {
      guardando = false;
    }
  }

  quill.on("text-change", function (_delta, _anterior, fuente) {
    actualizarContador();
    if (fuente !== "user") return;
    hayCambios = true;
    mostrarEstado("pendiente", "Cambios sin guardar");
    clearTimeout(temporizador);
    temporizador = setTimeout(guardar, ESPERA_MS);
  });

  // Ctrl/Cmd + S guarda de inmediato.
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      guardar();
    }
  });

  // Al salir de la página con cambios pendientes, enviar un último guardado.
  window.addEventListener("beforeunload", function (e) {
    if (!hayCambios) return;
    fetch(urlGuardar, {
      method: "POST",
      keepalive: true,
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ contenido: quill.root.innerHTML }),
      credentials: "same-origin",
    });
    e.preventDefault();
    e.returnValue = "";
  });

  actualizarContador();
})();
