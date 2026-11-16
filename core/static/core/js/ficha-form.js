/* PlotNode — comportamiento del formulario de ficha (página completa y panel del editor) */
(function () {
  "use strict";

  function preparar(form) {
    const entrada = form.querySelector('input[type="file"]');
    const vista = form.querySelector("[data-foto-vista]");
    if (!entrada || !vista) return;
    let url = null;
    entrada.addEventListener("change", function () {
      const archivo = entrada.files && entrada.files[0];
      if (!archivo) return;
      if (url) URL.revokeObjectURL(url);
      url = URL.createObjectURL(archivo);
      const img = document.createElement("img");
      img.src = url;
      img.alt = "Vista previa de la foto";
      vista.replaceChildren(img);
      const quitar = form.querySelector('input[name="quitar_foto"]');
      if (quitar) quitar.checked = false;
    });
  }

  window.PlotNodeFichaForm = { preparar: preparar };
  document.querySelectorAll("[data-form-ficha]").forEach(preparar);
})();
