/* PlotNode — tablón de ideas: arrastrar notas (ratón, táctil o flechas) y guardar su posición */
(function () {
  "use strict";
  const tablon = document.getElementById("tablon");
  if (!tablon) return;
  const estado = document.getElementById("tablon-estado");
  const csrf = () => (document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/) || [])[1] || "";
  const urlMover = (id) => tablon.dataset.urlMover.replace(/\/0\/mover\/$/, "/" + id + "/mover/");
  const guardando = new Map();

  function guardar(nota) {
    clearTimeout(guardando.get(nota));
    guardando.set(nota, setTimeout(async function () {
      try {
        const r = await fetch(urlMover(nota.dataset.id), {
          method: "POST", credentials: "same-origin",
          headers: { "Content-Type": "application/json", "X-CSRFToken": decodeURIComponent(csrf()) },
          body: JSON.stringify({ x: Number(nota.dataset.x), y: Number(nota.dataset.y) }),
        });
        if (!r.ok) throw new Error();
        if (estado) estado.textContent = "Posición guardada.";
      } catch (e) {
        if (estado) estado.textContent = "No se pudo guardar la posición. Revisa tu conexión.";
      }
    }, 250));
  }
  function poner(nota, x, y) {
    x = Math.max(0, Math.round(x)); y = Math.max(0, Math.round(y));
    nota.dataset.x = x; nota.dataset.y = y;
    nota.style.left = x + "px"; nota.style.top = y + "px";
    tablon.style.minWidth = Math.max(tablon.scrollWidth, x + 340) + "px";
    tablon.style.minHeight = Math.max(tablon.scrollHeight, y + 260) + "px";
  }

  tablon.querySelectorAll(".nota").forEach(function (nota) {
    let ini = null;
    nota.addEventListener("pointerdown", function (e) {
      if (e.target.closest("a, button") || e.button > 0) return;
      ini = { px: e.clientX, py: e.clientY, x: Number(nota.dataset.x), y: Number(nota.dataset.y) };
      nota.setPointerCapture(e.pointerId);
      nota.classList.add("arrastrando");
    });
    nota.addEventListener("pointermove", function (e) {
      if (!ini) return;
      poner(nota, ini.x + e.clientX - ini.px, ini.y + e.clientY - ini.py);
    });
    function soltar() {
      if (!ini) return;
      ini = null;
      nota.classList.remove("arrastrando");
      guardar(nota);
    }
    nota.addEventListener("pointerup", soltar);
    nota.addEventListener("pointercancel", soltar);
    nota.addEventListener("keydown", function (e) {
      if (e.target !== nota) return;
      const paso = e.shiftKey ? 50 : 10;
      const d = { ArrowLeft: [-paso, 0], ArrowRight: [paso, 0], ArrowUp: [0, -paso], ArrowDown: [0, paso] }[e.key];
      if (!d) return;
      e.preventDefault();
      poner(nota, Number(nota.dataset.x) + d[0], Number(nota.dataset.y) + d[1]);
      guardar(nota);
    });
  });
})();
