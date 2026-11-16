/* PlotNode — lista fija de sinónimos para las muletillas (HU-28). No usa IA.
   Cada grupo: [formas que activan la sugerencia (sin acentos ni mayúsculas), sugerencias]. */
(function () {
  "use strict";

  const GRUPOS = [
    // Conectores y muletillas del habla
    [["entonces"], ["así que", "por eso", "en ese caso", "de modo que"]],
    [["pues"], ["así que", "por tanto", "en consecuencia", "de modo que"]],
    [["pero"], ["sin embargo", "aunque", "no obstante", "mas"]],
    [["ademas"], ["asimismo", "por si fuera poco", "también", "igualmente"]],
    [["tambien"], ["asimismo", "además", "igualmente", "del mismo modo"]],
    [["despues"], ["luego", "más tarde", "a continuación", "acto seguido"]],
    [["luego"], ["después", "más tarde", "a continuación", "acto seguido"]],
    [["ahora"], ["en este momento", "en este instante", "por ahora", "hoy"]],
    [["siempre"], ["constantemente", "en todo momento", "invariablemente", "a todas horas"]],
    [["nunca"], ["jamás", "en ningún momento", "en absoluto", "ni una sola vez"]],
    [["quiza", "quizas", "acaso"], ["tal vez", "posiblemente", "a lo mejor", "acaso"]],
    [["casi"], ["apenas", "por poco", "prácticamente", "cerca de"]],
    // Adverbios en -mente y de intensidad
    [["muy"], ["sumamente", "extremadamente", "tremendamente", "enormemente"]],
    [["realmente"], ["verdaderamente", "en verdad", "de veras", "auténticamente"]],
    [["simplemente"], ["sencillamente", "llanamente", "tan solo", "únicamente"]],
    [["basicamente"], ["fundamentalmente", "esencialmente", "en esencia", "en el fondo"]],
    [["finalmente"], ["por fin", "al final", "en última instancia", "al cabo"]],
    [["obviamente"], ["evidentemente", "por supuesto", "claramente", "desde luego"]],
    [["totalmente"], ["completamente", "por completo", "enteramente", "absolutamente"]],
    [["rapidamente"], ["velozmente", "con rapidez", "a toda prisa", "enseguida"]],
    [["lentamente"], ["despacio", "con calma", "pausadamente", "poco a poco"]],
    [["inmediatamente"], ["al instante", "de inmediato", "enseguida", "acto seguido"]],
    [["bien"], ["correctamente", "adecuadamente", "con acierto", "favorablemente"]],
    // Cantidades
    [["mucho"], ["bastante", "en abundancia", "enormemente", "a menudo"]],
    [["mucha"], ["bastante", "abundante", "enorme", "gran cantidad de"]],
    [["muchos"], ["numerosos", "incontables", "bastantes", "una multitud de"]],
    [["muchas"], ["numerosas", "incontables", "bastantes", "una multitud de"]],
    // Sustantivos comodín
    [["cosa"], ["asunto", "objeto", "detalle", "elemento"]],
    [["cosas"], ["asuntos", "objetos", "detalles", "elementos"]],
    [["algo"], ["cierta cosa", "un detalle", "un asunto", "un no sé qué"]],
    [["gente"], ["personas", "multitud", "habitantes", "ciudadanos"]],
    [["persona"], ["individuo", "sujeto", "alguien", "figura"]],
    [["lugar"], ["sitio", "paraje", "espacio", "rincón"]],
    [["momento"], ["instante", "segundo", "rato", "ocasión"]],
    // Adjetivos de uso frecuente
    [["bueno"], ["excelente", "magnífico", "admirable", "estupendo"]],
    [["buena"], ["excelente", "magnífica", "admirable", "estupenda"]],
    [["buenos"], ["excelentes", "magníficos", "admirables", "estupendos"]],
    [["buenas"], ["excelentes", "magníficas", "admirables", "estupendas"]],
    [["malo"], ["terrible", "pésimo", "desagradable", "nefasto"]],
    [["mala"], ["terrible", "pésima", "desagradable", "nefasta"]],
    [["grande"], ["enorme", "inmenso", "imponente", "gigantesco"]],
    [["grandes"], ["enormes", "inmensos", "imponentes", "gigantescos"]],
    [["pequeno"], ["diminuto", "minúsculo", "menudo", "reducido"]],
    [["pequena"], ["diminuta", "minúscula", "menuda", "reducida"]],
    [["bonito"], ["hermoso", "precioso", "encantador", "lindo"]],
    [["bonita"], ["hermosa", "preciosa", "encantadora", "linda"]],
    [["hermoso"], ["bello", "precioso", "esplendoroso", "encantador"]],
    [["hermosa"], ["bella", "preciosa", "esplendorosa", "encantadora"]],
    [["rapido"], ["veloz", "ágil", "presuroso", "fugaz"]],
    [["rapida"], ["veloz", "ágil", "presurosa", "fugaz"]],
    [["lento"], ["pausado", "pesado", "cansino", "parsimonioso"]],
    [["lenta"], ["pausada", "pesada", "cansina", "parsimoniosa"]],
    [["importante"], ["relevante", "esencial", "fundamental", "crucial"]],
    [["dificil"], ["complicado", "arduo", "complejo", "penoso"]],
    [["facil"], ["sencillo", "simple", "llano", "accesible"]],
    [["feliz"], ["contento", "dichoso", "alegre", "radiante"]],
    [["triste"], ["afligido", "apenado", "melancólico", "abatido"]],
    [["extrano"], ["raro", "peculiar", "singular", "inusual"]],
    [["extrana"], ["rara", "peculiar", "singular", "inusual"]],
    // Verbos (formas más repetidas en narrativa)
    [["dijo"], ["comentó", "murmuró", "susurró", "afirmó", "replicó", "exclamó"]],
    [["dije"], ["comenté", "murmuré", "susurré", "afirmé", "repliqué", "exclamé"]],
    [["dijeron"], ["comentaron", "murmuraron", "susurraron", "afirmaron", "replicaron", "exclamaron"]],
    [["dice"], ["comenta", "murmura", "susurra", "afirma", "replica", "exclama"]],
    [["decia"], ["comentaba", "murmuraba", "susurraba", "afirmaba", "replicaba"]],
    [["respondio"], ["contestó", "replicó", "repuso", "dijo"]],
    [["pregunto"], ["inquirió", "interrogó", "indagó", "quiso saber"]],
    [["miro"], ["observó", "contempló", "examinó", "fijó la vista en"]],
    [["miraba"], ["observaba", "contemplaba", "examinaba", "vigilaba"]],
    [["mira"], ["observa", "contempla", "examina", "vigila"]],
    [["miraron"], ["observaron", "contemplaron", "examinaron", "vigilaron"]],
    [["vio"], ["divisó", "distinguió", "advirtió", "notó"]],
    [["hizo"], ["realizó", "ejecutó", "llevó a cabo", "efectuó"]],
    [["hacia"], ["realizaba", "ejecutaba", "llevaba a cabo", "efectuaba"]],
    [["tenia"], ["poseía", "contaba con", "guardaba", "disponía de"]],
    [["tiene"], ["posee", "cuenta con", "dispone de", "guarda"]],
    [["tuvo"], ["poseyó", "contó con", "dispuso de", "guardó"]],
    [["puso"], ["colocó", "dejó", "situó", "depositó"]],
    [["empezo"], ["comenzó", "inició", "arrancó", "se puso a"]],
    [["comenzo"], ["empezó", "inició", "arrancó", "se puso a"]],
    [["salio"], ["abandonó", "partió", "se marchó", "se alejó"]],
    [["entro"], ["ingresó", "accedió", "penetró", "pasó"]],
    [["llego"], ["arribó", "alcanzó", "apareció", "se presentó"]],
  ];

  const mapa = new Map();
  GRUPOS.forEach(function (grupo) { grupo[0].forEach(function (forma) { mapa.set(forma, grupo[1]); }); });

  window.PlotNodeSinonimos = {
    de: function (formaNormalizada) { return mapa.get(formaNormalizada) || []; },
  };
})();
