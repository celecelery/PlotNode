/* Diálogos de «+ Nuevo…» y filtros que se aplican al cambiar. */
(function () {
  "use strict";
  document.querySelectorAll("[data-abrir-dialogo]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      var d = document.getElementById(boton.getAttribute("data-abrir-dialogo"));
      if (d && d.showModal) { d.showModal(); var c = d.querySelector("input:not([type=hidden]), select, textarea"); if (c) c.focus(); }
    });
  });
  document.querySelectorAll("dialog[data-abrir]").forEach(function (d) { if (d.showModal && !d.open) d.showModal(); });
  document.querySelectorAll("[data-cerrar-dialogo]").forEach(function (b) {
    b.addEventListener("click", function () { var d = b.closest("dialog"); if (d) d.close(); });
  });
  document.querySelectorAll("dialog.dialogo").forEach(function (d) {
    d.addEventListener("click", function (e) { if (e.target === d) d.close(); });
  });
  document.querySelectorAll("select[data-autoenviar]").forEach(function (s) {
    s.addEventListener("change", function () { if (s.form) s.form.submit(); });
  });
})();
