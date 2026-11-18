/* PlotNode — mapa de relaciones: fichas en círculo unidas por líneas con su nombre */
(function () {
  "use strict";
  const datos = document.getElementById("mapa-datos");
  const svg = document.getElementById("mapa-svg");
  if (!datos || !svg) return;
  const { nodos, aristas } = JSON.parse(datos.textContent);
  const NS = "http://www.w3.org/2000/svg";
  const W = 720, H = 460, R = 34;
  const el = function (n, a, texto) {
    const x = document.createElementNS(NS, n);
    Object.entries(a || {}).forEach(([k, v]) => x.setAttribute(k, v));
    if (texto) x.textContent = texto;
    return x;
  };
  const pos = new Map();
  if (nodos.length === 1) pos.set(nodos[0].id, [W / 2, H / 2]);
  else nodos.forEach(function (n, i) {
    const ang = (2 * Math.PI * i) / nodos.length - Math.PI / 2;
    pos.set(n.id, [W / 2 + Math.cos(ang) * (W / 2 - 110), H / 2 + Math.sin(ang) * (H / 2 - 70)]);
  });
  const base = svg.dataset.base || "";
  const capaLineas = el("g"), capaTextos = el("g"), capaNodos = el("g");
  aristas.forEach(function (a) {
    const p = pos.get(a.origen), q = pos.get(a.destino);
    if (!p || !q) return;
    capaLineas.appendChild(el("line", { class: "arista cat-" + a.categoria, "data-o": a.origen, "data-d": a.destino, x1: p[0], y1: p[1], x2: q[0], y2: q[1] }));
    capaTextos.appendChild(el("text", { class: "arista-texto", x: (p[0] + q[0]) / 2, y: (p[1] + q[1]) / 2 + 4 }, a.texto));
  });
  nodos.forEach(function (n) {
    const [x, y] = pos.get(n.id);
    const g = el("g");
    g.appendChild(el("circle", { class: "c-" + n.color, cx: x, cy: y, r: R }));
    g.appendChild(el("text", { class: "nodo-inicial t-" + n.color, x: x, y: y }, n.inicial));
    g.appendChild(el("text", { class: "nodo-nombre", x: x, y: y + R + 18 }, n.nombre));
    const a = el("a", { href: "../fichas/" + n.id + "/", "aria-label": "Resaltar las relaciones de " + n.nombre, "data-id": n.id });
    a.addEventListener("click", function (e) { e.preventDefault(); elegir(n.id); });
    a.appendChild(g);
    capaNodos.appendChild(a);
  });
  svg.append(capaLineas, capaTextos, capaNodos);

  // Al elegir un nodo se resaltan sus relaciones y se muestra un resumen con enlace a su ficha.
  const caja = document.getElementById("mapa-seleccion");
  const nombreDe = new Map(nodos.map((n) => [n.id, n.nombre]));
  let elegido = null;
  function elegir(id) {
    elegido = elegido === id ? null : id;
    svg.querySelectorAll("line.arista").forEach(function (l) {
      const mia = elegido === null || +l.dataset.o === elegido || +l.dataset.d === elegido;
      l.classList.toggle("tenue", !mia);
    });
    svg.querySelectorAll("a[data-id]").forEach(function (a) {
      a.querySelector("circle").classList.toggle("elegido", +a.dataset.id === elegido);
    });
    caja.replaceChildren();
    caja.hidden = elegido === null;
    if (elegido === null) return;
    const mias = aristas.filter((x) => x.origen === elegido || x.destino === elegido);
    const t = document.createElement("strong"); t.textContent = nombreDe.get(elegido);
    const ul = document.createElement("ul");
    mias.forEach(function (x) {
      const otro = x.origen === elegido ? x.destino : x.origen;
      const li = document.createElement("li");
      li.textContent = x.texto + " · " + nombreDe.get(otro);
      ul.appendChild(li);
    });
    const enlace = document.createElement("a");
    enlace.href = "../fichas/" + elegido + "/"; enlace.textContent = "Abrir su ficha →";
    caja.append(t, ul, enlace);
  }
})();
