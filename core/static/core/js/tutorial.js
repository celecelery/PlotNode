/* PlotNode — tutorial de bienvenida: 4 pasos sobre el editor real, sin bloquear la página (RF-11) */
(function () {
  "use strict";
  const area = document.getElementById("area-editor");
  if (!area || !area.dataset.tutorial) return;
  const urlTerminar = area.dataset.tutorial;
  const csrf = () => decodeURIComponent((document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/) || [])[1] || "");

  const PASOS = [
    { objetivo: "#editor", titulo: "Aquí escribes",
      texto: "Escribe o pega tu capítulo. Se guarda solo unos segundos después de que dejas de teclear." },
    { objetivo: "#editor", titulo: "Selecciona un nombre",
      texto: "Prueba ahora: selecciona «Ana» con el cursor. Su ficha aparece al lado, sin salir de la página." },
    { objetivo: "#reparto", titulo: "Tu panel de apoyo",
      texto: "Aquí viven las fichas, el glosario y las muletillas. Si el nombre no tiene ficha, el panel te ofrece crearla." },
    { objetivo: ".riel-herramientas", titulo: "Más herramientas",
      texto: "Relaciones entre personajes, línea de tiempo de la trama y tablón de ideas. Con «Enviar al tablón» guardas pasajes del texto." },
  ];

  const anillo = document.createElement("div");
  anillo.className = "tuto-anillo";
  anillo.setAttribute("aria-hidden", "true");
  const caja = document.createElement("div");
  caja.className = "tuto-caja";
  caja.setAttribute("role", "dialog");
  caja.setAttribute("aria-labelledby", "tuto-titulo");
  caja.innerHTML =
    '<p class="tuto-paso" id="tuto-paso"></p>' +
    '<h2 id="tuto-titulo"></h2><p id="tuto-texto"></p>' +
    '<div class="tuto-puntos" aria-hidden="true"></div>' +
    '<div class="tuto-acciones"><button type="button" class="boton-texto" id="tuto-omitir">Omitir tutorial</button>' +
    '<span><button type="button" class="boton boton-borde boton-chico" id="tuto-atras">Atrás</button> ' +
    '<button type="button" class="boton boton-chico" id="tuto-sig">Siguiente</button></span></div>';
  document.body.append(anillo, caja);
  const $ = (id) => caja.querySelector(id);
  let i = 0, terminado = false;

  function objetivo(p) {
    const n = document.querySelector(p.objetivo);
    return n && n.getClientRects().length ? n : null;
  }
  function colocar() {
    if (terminado) return;
    const n = objetivo(PASOS[i]);
    if (!n) { anillo.style.display = "none"; caja.style.cssText = "left:50%;top:40%;transform:translateX(-50%)"; return; }
    n.scrollIntoView({ block: "nearest" });
    const r = n.getBoundingClientRect();
    anillo.style.cssText = "display:block;left:" + (r.left - 6) + "px;top:" + (r.top - 6) + "px;width:" + (r.width + 12) + "px;height:" + (r.height + 12) + "px";
    const w = caja.offsetWidth, h = caja.offsetHeight, v = 16;
    let x, y;
    if (r.left > w + v + 8) { x = r.left - w - v; y = r.top + 12; }            // a la izquierda (panel de la derecha)
    else if (window.innerWidth - r.right > w + v + 8) { x = r.right + v; y = r.top + 12; }
    else { x = Math.max(v, r.left + 24); y = Math.min(r.top + 80, window.innerHeight - h - v); }
    x = Math.min(Math.max(v, x), window.innerWidth - w - v);
    y = Math.min(Math.max(v, y), window.innerHeight - h - v);
    caja.style.cssText = "left:" + x + "px;top:" + y + "px";
  }
  function mostrar() {
    const p = PASOS[i];
    $("#tuto-paso").textContent = "Paso " + (i + 1) + " de " + PASOS.length;
    $("#tuto-titulo").textContent = p.titulo;
    $("#tuto-texto").textContent = p.texto;
    $("#tuto-atras").hidden = i === 0;
    $("#tuto-sig").textContent = i === PASOS.length - 1 ? "Empezar a escribir" : "Siguiente";
    caja.querySelector(".tuto-puntos").innerHTML = PASOS.map((_, k) => '<span class="' + (k <= i ? "on" : "") + '"></span>').join("");
    colocar();
    $("#tuto-sig").focus({ preventScroll: true });
  }
  function terminar() {
    terminado = true;
    anillo.remove(); caja.remove();
    document.removeEventListener("keydown", teclas);
    window.removeEventListener("resize", colocar);
    fetch(urlTerminar, { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrf() } }).catch(function () {});
    const q = new URL(location.href);
    if (q.searchParams.has("tutorial")) { q.searchParams.delete("tutorial"); history.replaceState(null, "", q.pathname + q.search); }
  }
  function teclas(e) { if (e.key === "Escape") terminar(); }
  $("#tuto-sig").addEventListener("click", function () { if (i === PASOS.length - 1) terminar(); else { i++; mostrar(); } });
  $("#tuto-atras").addEventListener("click", function () { if (i > 0) { i--; mostrar(); } });
  $("#tuto-omitir").addEventListener("click", terminar);
  document.addEventListener("keydown", teclas);
  window.addEventListener("resize", colocar);
  mostrar();
})();
