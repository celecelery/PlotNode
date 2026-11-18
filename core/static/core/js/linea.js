/* PlotNode — línea de tiempo: mostrar u ocultar carriles por personaje */
(function () {
  "use strict";
  document.querySelectorAll("[data-carril]").forEach(function (caja) {
    caja.addEventListener("change", function () {
      const fila = document.querySelector('[data-carril-fila="' + caja.dataset.carril + '"]');
      if (fila) fila.hidden = !caja.checked;
    });
  });
})();
