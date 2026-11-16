/* PlotNode — editor con autoguardado (HU-06) */
(function () {
  "use strict";

  const ESPERA_MS = 3000;      // guardar 3 s después de dejar de escribir
  const REINTENTO_MS = 5000;   // si falla, reintentar a los 5 s

  const contenedor = document.getElementById("editor");
  const urlGuardar = contenedor.dataset.urlGuardar;
  // El token se lee al enviar: si Django lo rota (login en otra pestaña), el valor viejo del formulario ya no sirve.
  function leerCsrf() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : document.querySelector("[name=csrfmiddlewaretoken]").value;
  }
  let version = contenedor.dataset.version ? Number(contenedor.dataset.version) : null;
  const LIMITE_KEEPALIVE = 60000;   // los navegadores cortan los fetch keepalive de más de ~64 KB
  const elEstado = document.getElementById("estado-guardado");

  // --- Formatos propios --------------------------------------------------------
  // Tipo y tamaño de letra como estilo en línea, con una lista corta de valores permitidos.
  const Fuente = Quill.import("attributors/style/font");
  Fuente.whitelist = ["Figtree", "Georgia"];
  Quill.register(Fuente, true);
  const Tamano = Quill.import("attributors/style/size");
  Tamano.whitelist = ["14px", "16px", "22px", "28px"];
  Quill.register(Tamano, true);

  // Línea separadora (<hr>).
  const BlockEmbed = Quill.import("blots/block/embed");
  class Separador extends BlockEmbed {}
  Separador.blotName = "divider";
  Separador.tagName = "hr";
  Quill.register(Separador);

  // Palabra del glosario: <span class="glosario" data-termino="12">.
  const Inline = Quill.import("blots/inline");
  class TerminoGlosario extends Inline {
    static create(valor) {
      const nodo = super.create();
      nodo.setAttribute("data-termino", String(valor));
      return nodo;
    }
    static formats(nodo) { return nodo.getAttribute("data-termino"); }
  }
  TerminoGlosario.blotName = "termino";
  TerminoGlosario.tagName = "span";
  TerminoGlosario.className = "glosario";
  Quill.register(TerminoGlosario);

  const quill = new Quill(contenedor, {
    theme: "snow",
    placeholder: "Empieza a escribir tu capítulo…",
    modules: {
      toolbar: {
        container: "#barra-formato",   // barra vertical propia junto al texto
        handlers: {
          divider: function () {
            const rango = this.quill.getSelection(true);
            this.quill.insertEmbed(rango.index, "divider", true, "user");
            this.quill.setSelection(rango.index + 1, 0, "silent");
          },
          image: function () {
            const direccion = window.prompt("Dirección web de la imagen (https://…)");
            if (!direccion || !/^https?:\/\//i.test(direccion.trim())) return;
            const rango = this.quill.getSelection(true);
            this.quill.insertEmbed(rango.index, "image", direccion.trim(), "user");
          },
          termino: function () {
            if (window.plotnode && window.plotnode.accionGlosario) window.plotnode.accionGlosario();
          },
        },
      },
    },
  });

  // Cargar el contenido guardado. clipboard.convert pasa el HTML por los formatos
  // permitidos de Quill, así que no se ejecuta ningún script incrustado.
  const inicial = JSON.parse(document.getElementById("contenido-inicial").textContent || '""');
  if (inicial) {
    quill.setContents(quill.clipboard.convert({ html: inicial }), "silent");
  }
  quill.focus();
  window.plotnode = { quill: quill };   // lo usa el panel de fichas (panel.js)

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
  let detenido = false;   // true cuando reintentar no sirve (sesión vencida, capítulo demasiado largo o conflicto)

  function detener(texto) {
    detenido = true;
    hayCambios = true;
    mostrarEstado("error", texto);
  }

  async function guardar() {
    clearTimeout(temporizador);
    if (!hayCambios || detenido) return;
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
        headers: { "Content-Type": "application/json", "X-CSRFToken": leerCsrf() },
        body: JSON.stringify({ contenido: quill.root.innerHTML, version: version }),
        credentials: "same-origin",
      });
      if (resp.status === 401 || resp.status === 403 || resp.redirected) {
        detener("Tu sesión expiró. Copia tu texto, inicia sesión de nuevo y vuelve a pegarlo.");
        return;
      }
      const datos = await resp.json().catch(() => ({}));
      if (resp.status === 413) {
        detener("El capítulo es demasiado largo para guardarse. Divídelo en dos capítulos.");
        return;
      }
      if (resp.status === 409) {
        detener(datos.error || "Este capítulo cambió en otra ventana. Recarga la página.");
        return;
      }
      if (!resp.ok || !datos.ok) throw new Error(datos.error || `Error ${resp.status}`);
      if (datos.version) version = datos.version;
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
    const cuerpo = JSON.stringify({ contenido: quill.root.innerHTML, version: version });
    if (!detenido && cuerpo.length < LIMITE_KEEPALIVE) {
      fetch(urlGuardar, {
        method: "POST",
        keepalive: true,
        headers: { "Content-Type": "application/json", "X-CSRFToken": leerCsrf() },
        body: cuerpo,
        credentials: "same-origin",
      }).catch(function () {});
    }
    e.preventDefault();
    e.returnValue = "";
  });

  actualizarContador();
})();
