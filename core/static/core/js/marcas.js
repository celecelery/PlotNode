/* PlotNode — trazos de lápiz entre una palabra del texto y su nota al margen.
   Uso: dentro de un contenedor [data-marcas], un <svg class="trazos"> con
   <path data-desde="id-palabra" data-hasta="id-nota">. Se recalcula al cambiar el tamaño. */
(function () {
  "use strict";
  const reducir = window.matchMedia("(prefers-reduced-motion: reduce)");

  // Coloca cada nota del margen a la altura de la palabra que comenta, sin encimarse.
  function alinear(contenedor) {
    contenedor.querySelectorAll("[data-canal]").forEach(function (margen) {
      const notas = margen.querySelectorAll("[data-junto]");
      notas.forEach(function (n) { n.style.marginTop = ""; });
      if (getComputedStyle(contenedor.querySelector(".trazos")).display === "none") return;
      let fondo = margen.getBoundingClientRect().top;
      notas.forEach(function (nota) {
        const palabra = document.getElementById(nota.dataset.junto);
        if (!palabra) return;
        const deseado = palabra.getBoundingClientRect().top - 4;
        const actual = nota.getBoundingClientRect().top;
        const destino = Math.max(deseado, fondo);
        nota.style.marginTop = Math.max(0, destino - actual) + "px";
        fondo = nota.getBoundingClientRect().bottom + 16;
      });
    });
  }

  function trazar(contenedor, animar) {
    alinear(contenedor);
    const base = contenedor.getBoundingClientRect();
    contenedor.querySelectorAll(".trazos path[data-desde]").forEach(function (path, i) {
      const desde = document.getElementById(path.dataset.desde);
      const hasta = document.getElementById(path.dataset.hasta);
      if (!desde || !hasta) return;
      const a = desde.getBoundingClientRect();
      const b = hasta.getBoundingClientRect();
      if (!a.width || !b.width) { path.removeAttribute("d"); return; }
      // Sale bajo la palabra, corre por el interlineado hasta el canal del margen
      // y sube o baja hasta la nota, como la raya que traza un corrector.
      const margen = hasta.closest("[data-canal]") || hasta;
      const canal = margen.getBoundingClientRect().left - base.left - 10;
      const x1 = a.left - base.left + a.width / 2;
      // La raya corre por la frontera entre renglones (el centro del interlineado).
      const lh = parseFloat(getComputedStyle(desde.parentElement).lineHeight) || a.height * 1.6;
      // Centro del hueco entre las descendentes de este renglón y las ascendentes del siguiente.
      const y1 = a.bottom - base.top + (lh - a.height) / 2 + 3;
      const x2 = b.left - base.left - 4;
      const y2 = b.top - base.top + 9;
      const r = Math.min(8, Math.abs(y2 - y1) / 2);
      const dir = y2 > y1 ? 1 : -1;
      // Tramo 1 (punteado, tenue): guía bajo el renglón hasta el canal del margen.
      let guia = path.previousElementSibling;
      if (!guia || !guia.classList.contains("trazo-guia")) {
        guia = document.createElementNS("http://www.w3.org/2000/svg", "path");
        guia.setAttribute("class", "trazo-guia " + path.getAttribute("class"));
        path.parentNode.insertBefore(guia, path);
      }
      guia.setAttribute("d", `M${x1},${a.bottom - base.top + 1} V${y1} H${canal - r}`);
      // Tramo 2 (sólido, se dibuja una vez): del canal a la nota.
      path.setAttribute("d",
        `M${canal - r},${y1} Q${canal},${y1} ${canal},${y1 + dir * r} ` +
        `V${y2 - dir * r} Q${canal},${y2} ${canal + r},${y2} H${x2}`);
      if (animar && !reducir.matches && path.getTotalLength) {
        const largo = path.getTotalLength();
        path.style.strokeDasharray = largo;
        path.style.strokeDashoffset = largo;
        path.animate(
          [{ strokeDashoffset: largo }, { strokeDashoffset: 0 }],
          { duration: 700, delay: 250 + i * 350, easing: "cubic-bezier(.16,1,.3,1)", fill: "forwards" }
        );
      } else {
        path.style.strokeDasharray = "";
        path.style.strokeDashoffset = "";
      }
    });
  }

  function iniciar() {
    const contenedores = document.querySelectorAll("[data-marcas]");
    contenedores.forEach(function (c) { trazar(c, true); });
    let espera;
    window.addEventListener("resize", function () {
      clearTimeout(espera);
      espera = setTimeout(function () { contenedores.forEach(function (c) { trazar(c, false); }); }, 120);
    });
  }

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(iniciar);
  else window.addEventListener("load", iniciar);
})();
