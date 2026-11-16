/* PlotNode — subraya en el texto los nombres que ya tienen ficha (con el color de cada ficha) */
(function () {
  "use strict";

  const P = window.plotnode;
  if (!P || !P.quill || !P.obtenerFichas) return;
  if (!(window.CSS && CSS.highlights && typeof Highlight !== "undefined")) return;   // sin la API: el texto queda tal cual
  const quill = P.quill;
  const COLORES = ["lila", "menta", "durazno"];
  const LETRA = /[\p{L}\p{N}]/u;

  // Minúsculas y sin acentos, carácter por carácter: así la posición en el texto normalizado
  // es la misma que en el documento (normalizar() de toda la cadena podría desplazarla).
  function plano(c) {
    const base = c.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    return base.length === 1 ? base : (base[0] || c);
  }
  const planoTexto = (t) => Array.from(t, plano).join("");

  function textoDelDocumento() {
    let texto = "";
    quill.getContents().ops.forEach(function (op) { texto += typeof op.insert === "string" ? op.insert : "￼"; });
    return texto;
  }

  function rangoDom(inicio, largo) {
    const a = quill.getLeaf(inicio);
    const b = quill.getLeaf(inicio + largo - 1);
    if (!a[0] || !b[0] || a[0].domNode.nodeType !== 3 || b[0].domNode.nodeType !== 3) return null;
    const r = document.createRange();
    r.setStart(a[0].domNode, a[1]);
    r.setEnd(b[0].domNode, b[1] + 1);
    return r;
  }

  function subrayar() {
    COLORES.forEach((c) => CSS.highlights.delete("nombre-" + c));
    const terminos = [];
    P.obtenerFichas().forEach(function (f) {
      [f.nombre, ...(f.alias || [])].forEach(function (n) {
        const t = planoTexto((n || "").trim().replace(/\s+/g, " "));
        if (t.length >= 3) terminos.push({ t: t, color: COLORES.includes(f.color) ? f.color : "lila" });
      });
    });
    if (!terminos.length) return;
    terminos.sort((a, b) => b.t.length - a.t.length);          // primero los largos: «Elena Marrón» antes que «Elena»
    const texto = textoDelDocumento();
    const hay = planoTexto(texto);
    const ocupado = new Uint8Array(hay.length);
    const porColor = { lila: [], menta: [], durazno: [] };
    terminos.forEach(function (x) {
      let desde = 0;
      for (;;) {
        const i = hay.indexOf(x.t, desde);
        if (i < 0) break;
        desde = i + 1;
        const fin = i + x.t.length;
        if (i > 0 && LETRA.test(hay[i - 1])) continue;          // palabra completa: «Ana» no marca «banana»
        if (fin < hay.length && LETRA.test(hay[fin])) continue;
        let libre = true;
        for (let k = i; k < fin; k++) if (ocupado[k]) { libre = false; break; }
        if (!libre) continue;
        ocupado.fill(1, i, fin);
        const r = rangoDom(i, x.t.length);
        if (r) porColor[x.color].push(r);
      }
    });
    COLORES.forEach(function (c) {
      if (porColor[c].length) CSS.highlights.set("nombre-" + c, new Highlight(...porColor[c]));
    });
  }

  let temporizador = null;
  function programar() {
    clearTimeout(temporizador);
    temporizador = setTimeout(subrayar, 400);
  }
  quill.on("text-change", programar);
  document.addEventListener("plotnode:fichas", programar);
  programar();
})();
