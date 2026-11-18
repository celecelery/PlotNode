import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .fichas_schema import TIPO_PLURAL, TIPOS
from .forms import (AtributoFormSet, CapituloForm, EventoTramaForm, FichaForm, NotaForm, ProyectoForm, RegistroForm,
                    RelacionForm, TerminoForm, secciones_del_formulario)
from .models import Capitulo, EventoTrama, EventoUso, Ficha, Nota, Perfil, Proyecto, Relacion, Termino
from .services.plantilla import crear_proyecto_de_muestra
from .services.fichas import RELACIONES_PRECARGA, buscar_ficha, ficha_a_dict
from .utils import normalizar


def inicio(request):
    if request.user.is_authenticated:
        return redirect("proyectos")
    return render(request, "core/inicio.html", {"lista_espera_url": settings.MAILERLITE_FORM_URL})


@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("proyectos")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, f"¡Bienvenida/o a PlotNode, {usuario.username}!")
        capitulo = crear_proyecto_de_muestra(usuario)   # algo con qué probar el panel desde el primer minuto
        return redirect("editor", pk=capitulo.pk)
    return render(request, "registration/registro.html", {"form": form})


# --- Proyectos (HU-04) -------------------------------------------------------
# Regla de acceso: toda consulta parte de request.user. Si el proyecto es de otra
# persona, get_object_or_404 responde 404 sin revelar que existe.

def _proyecto_del_usuario(request, pk):
    return get_object_or_404(Proyecto, pk=pk, dueno=request.user)


@login_required
@require_http_methods(["GET", "POST"])
def proyectos(request):
    form = ProyectoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        proyecto = form.save(commit=False)
        proyecto.dueno = request.user
        proyecto.save()
        Capitulo.objects.create(proyecto=proyecto, titulo="Capítulo 1", orden=1)
        messages.success(request, f"Proyecto «{proyecto.titulo}» creado.")
        return redirect("proyectos")
    lista = request.user.proyectos.prefetch_related("capitulos")
    return render(request, "core/proyectos.html", {"form": form, "proyectos": lista, "seccion": "proyectos"})


@login_required
@require_http_methods(["GET", "POST"])
def proyecto_editar(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    form = ProyectoForm(request.POST or None, instance=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyecto actualizado.")
        return redirect("proyectos")
    return render(request, "core/proyecto_form.html", {"form": form, "proyecto": proyecto, "seccion": "proyectos"})


@login_required
@require_http_methods(["GET", "POST"])
def proyecto_eliminar(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    if request.method == "POST":
        titulo = proyecto.titulo
        proyecto.delete()
        messages.success(request, f"Proyecto «{titulo}» eliminado.")
        return redirect("proyectos")
    return render(request, "core/proyecto_eliminar.html", {"proyecto": proyecto, "seccion": "proyectos"})


# --- Editor (HU-06) ----------------------------------------------------------

MAX_CONTENIDO = 2_000_000  # ~2 MB de HTML por capítulo


def _capitulo_del_usuario(request, pk):
    return get_object_or_404(Capitulo.objects.select_related("proyecto"), pk=pk, proyecto__dueno=request.user)


@login_required
def proyecto_abrir(request, pk):
    """Abre el proyecto en el capítulo que se editó por última vez (lo crea si no hay ninguno)."""
    proyecto = _proyecto_del_usuario(request, pk)
    capitulo = proyecto.capitulos.order_by("-actualizado", "orden").first()
    if capitulo is None:
        capitulo = Capitulo.objects.create(proyecto=proyecto, titulo="Capítulo 1", orden=1)
    return redirect(capitulo)


@login_required
def editor(request, pk):
    capitulo = _capitulo_del_usuario(request, pk)
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    return render(request, "core/editor.html", {
        "tutorial": request.GET.get("tutorial") == "1" or not perfil.onboarding_completado,
        "capitulo": capitulo,
        "version": _version(capitulo),
        "proyecto": capitulo.proyecto,
        "capitulos": capitulo.proyecto.capitulos.all(),
        "fichas": [ficha_a_dict(f) for f in capitulo.proyecto.fichas.prefetch_related(*RELACIONES_PRECARGA)],
        "terminos": [_termino_a_dict(t) for t in capitulo.proyecto.terminos.all()],
    })


SESION_MINUTOS = 30  # una pausa mayor abre una sesión de escritura nueva


def _registrar_escritura(usuario, proyecto, palabras_nuevas):
    """HU-18: acumula en un evento `sesion_escritura` las palabras netas escritas (valor)."""
    if palabras_nuevas <= 0:
        return
    desde = timezone.now() - timedelta(minutes=SESION_MINUTOS)
    sesion = EventoUso.objects.filter(usuario=usuario, proyecto=proyecto,
                                   tipo=EventoUso.Tipo.SESION_ESCRITURA, fecha__gte=desde).first()
    if sesion:
        EventoUso.objects.filter(pk=sesion.pk).update(valor=sesion.valor + palabras_nuevas)
    else:
        EventoUso.objects.create(usuario=usuario, proyecto=proyecto,
                              tipo=EventoUso.Tipo.SESION_ESCRITURA, valor=palabras_nuevas)


def _correo_real():
    """True si la app puede enviar correos de verdad (en la demo con consola, no)."""
    from django.conf import settings
    return not settings.EMAIL_BACKEND.endswith(("console.EmailBackend", "locmem.EmailBackend", "dummy.EmailBackend"))


class RecuperarContrasenaView(auth_views.PasswordResetView):
    """Igual que la de Django, pero avisa con honestidad si el correo no sale de verdad."""

    def get_context_data(self, **kwargs):
        return super().get_context_data(correo_real=_correo_real(), **kwargs)


class RecuperarContrasenaEnviadaView(auth_views.PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(correo_real=_correo_real(), **kwargs)


def _version(capitulo):
    """Marca de la última escritura (microsegundos): el editor la devuelve para detectar guardados cruzados."""
    return int(capitulo.actualizado.timestamp() * 1_000_000)


def _version(capitulo):
    """Marca de la última escritura (microsegundos): el editor la devuelve para detectar guardados cruzados."""
    return int(capitulo.actualizado.timestamp() * 1_000_000)


@login_required
@require_POST
def guardar_capitulo(request, pk):
    """Autoguardado: recibe JSON {"contenido": "<p>...</p>"} y responde con las palabras."""
    capitulo = _capitulo_del_usuario(request, pk)
    try:
        datos = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)
    contenido = datos.get("contenido")
    if not isinstance(contenido, str):
        return JsonResponse({"ok": False, "error": "Falta el contenido"}, status=400)
    if len(contenido) > MAX_CONTENIDO:
        return JsonResponse({"ok": False, "error": "El capítulo es demasiado largo"}, status=413)
    version = datos.get("version")
    if version is not None and version != _version(capitulo):
        # Otra pestaña o dispositivo guardó después: no pisamos su texto en silencio.
        return JsonResponse({"ok": False, "conflicto": True,
                             "error": "Este capítulo cambió en otra ventana. Recarga la página para ver la última versión."},
                            status=409)
    palabras_antes = capitulo.palabras
    capitulo.contenido = contenido
    capitulo.save()
    Proyecto.objects.filter(pk=capitulo.proyecto_id).update(actualizado=timezone.now())
    _registrar_escritura(request.user, capitulo.proyecto, capitulo.palabras - palabras_antes)
    return JsonResponse({"ok": True, "palabras": capitulo.palabras, "version": _version(capitulo),
                         "guardado": timezone.localtime(capitulo.actualizado).strftime("%H:%M")})


# --- Capítulos (HU-05) -------------------------------------------------------

def _renumerar(proyecto):
    """Deja el orden de los capítulos en 1..n sin huecos ni repetidos."""
    for i, c in enumerate(proyecto.capitulos.all(), start=1):
        if c.orden != i:
            Capitulo.objects.filter(pk=c.pk).update(orden=i)  # update: no toca palabras ni «actualizado»


@login_required
def capitulos_gestion(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    return render(request, "core/capitulos.html", {
        "proyecto": proyecto, "capitulos": proyecto.capitulos.all(), "seccion": "proyectos",
    })


@login_required
@require_POST
def capitulo_nuevo(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    siguiente = (proyecto.capitulos.aggregate(m=Max("orden"))["m"] or 0) + 1
    capitulo = Capitulo.objects.create(proyecto=proyecto, titulo=f"Capítulo {siguiente}", orden=siguiente)
    messages.success(request, f"Creaste «{capitulo.titulo}». Puedes cambiarle el nombre en «Gestionar capítulos».")
    return redirect(capitulo)


@login_required
@require_POST
def capitulo_renombrar(request, pk):
    capitulo = _capitulo_del_usuario(request, pk)
    form = CapituloForm(request.POST, instance=capitulo)
    if form.is_valid():
        form.save()
        messages.success(request, "Capítulo renombrado.")
    else:
        messages.error(request, "El capítulo necesita un título (máximo 150 caracteres).")
    return redirect("capitulos_gestion", pk=capitulo.proyecto_id)


@login_required
@require_POST
def capitulo_mover(request, pk):
    capitulo = _capitulo_del_usuario(request, pk)
    proyecto = capitulo.proyecto
    _renumerar(proyecto)
    capitulo.refresh_from_db(fields=["orden"])
    delta = -1 if request.POST.get("direccion") == "arriba" else 1
    vecino = proyecto.capitulos.filter(orden=capitulo.orden + delta).first()
    if vecino:
        Capitulo.objects.filter(pk=capitulo.pk).update(orden=vecino.orden)
        Capitulo.objects.filter(pk=vecino.pk).update(orden=capitulo.orden)
    return redirect("capitulos_gestion", pk=proyecto.pk)


@login_required
@require_http_methods(["GET", "POST"])
def capitulo_eliminar(request, pk):
    capitulo = _capitulo_del_usuario(request, pk)
    proyecto = capitulo.proyecto
    if proyecto.capitulos.count() <= 1:
        messages.error(request, "Un proyecto necesita al menos un capítulo.")
        return redirect("capitulos_gestion", pk=proyecto.pk)
    if request.method == "POST":
        titulo = capitulo.titulo
        capitulo.delete()
        _renumerar(proyecto)
        messages.success(request, f"Capítulo «{titulo}» eliminado.")
        return redirect("capitulos_gestion", pk=proyecto.pk)
    return render(request, "core/capitulo_eliminar.html",
                  {"capitulo": capitulo, "proyecto": proyecto, "seccion": "proyectos"})


# --- Fichas (HU-07, HU-25, HU-08) ----------------------------------------------

def _es_panel(request):
    """El panel del editor pide fragmentos y respuestas JSON con esta cabecera."""
    return request.headers.get("X-Requested-With") == "fetch"


@login_required
def fichas_lista(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    tipo = request.GET.get("tipo", "")
    fichas = proyecto.fichas.prefetch_related("atributos")
    if tipo in TIPOS:
        fichas = fichas.filter(tipo=tipo)
    return render(request, "core/fichas.html", {
        "proyecto": proyecto, "fichas": fichas, "seccion": "proyectos", "tipo": tipo, "herramienta": "fichas",
        "tipos": [(t, TIPO_PLURAL[t]) for t in TIPOS],
    })


@login_required
@require_http_methods(["GET", "POST"])
def ficha_form(request, pk, ficha_pk=None):
    """Crear o editar una ficha. Como página completa o, con la cabecera del panel, como fragmento."""
    proyecto = _proyecto_del_usuario(request, pk)
    if ficha_pk:
        ficha = get_object_or_404(Ficha, pk=ficha_pk, proyecto=proyecto)
    else:
        tipo = request.GET.get("tipo", "personaje")
        ficha = Ficha(proyecto=proyecto, tipo=tipo if tipo in TIPOS else "personaje")
        if request.method == "GET" and request.GET.get("nombre"):
            ficha.nombre = " ".join(request.GET["nombre"].split())[:120]
    form = FichaForm(ficha.tipo, request.POST or None, request.FILES or None, instance=ficha, proyecto=proyecto)
    formset = AtributoFormSet(request.POST or None, instance=ficha)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            ficha = form.save()
            formset.instance = ficha
            formset.save()
        if _es_panel(request):
            ficha = Ficha.objects.prefetch_related(*RELACIONES_PRECARGA).get(pk=ficha.pk)
            return JsonResponse({"ok": True, "ficha": ficha_a_dict(ficha)})
        messages.success(request, f"Ficha de {ficha.nombre} guardada.")
        return redirect("fichas_lista", pk=proyecto.pk)
    contexto = {
        "proyecto": proyecto, "ficha": ficha, "form": form, "formset": formset, "seccion": "proyectos",
        "secciones": secciones_del_formulario(form), "tipo_nombre": ficha.get_tipo_display(),
    }
    if _es_panel(request):
        return render(request, "core/partials/ficha_form.html", contexto, status=422 if request.method == "POST" else 200)
    return render(request, "core/ficha_form.html", contexto)


@login_required
@require_http_methods(["GET", "POST"])
def ficha_eliminar(request, pk, ficha_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    ficha = get_object_or_404(Ficha, pk=ficha_pk, proyecto=proyecto)
    if request.method == "POST":
        nombre = ficha.nombre
        if ficha.foto:
            ficha.foto.storage.delete(ficha.foto.name)
        ficha.delete()
        if _es_panel(request):
            return JsonResponse({"ok": True})
        messages.success(request, f"Ficha de {nombre} eliminada.")
        return redirect("fichas_lista", pk=proyecto.pk)
    return render(request, "core/ficha_eliminar.html", {"proyecto": proyecto, "ficha": ficha, "seccion": "proyectos"})


# --- Glosario (HU-29, HU-30) -----------------------------------------------------

def _termino_a_dict(t):
    return {"id": t.pk, "nombre": t.nombre, "definicion": t.definicion, "categoria": t.categoria}


@login_required
@require_http_methods(["GET", "POST"])
def glosario(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    form = TerminoForm(request.POST or None, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        termino = form.save(commit=False)
        termino.proyecto = proyecto
        termino.save()
        messages.success(request, f"Término «{termino.nombre}» agregado.")
        return redirect("glosario", pk=proyecto.pk)
    q = normalizar(request.GET.get("q", ""))
    terminos = [t for t in proyecto.terminos.all() if not q or q in t.clave or q in normalizar(t.definicion)]
    return render(request, "core/glosario.html", {
        "proyecto": proyecto, "terminos": terminos, "form": form, "q": request.GET.get("q", ""), "seccion": "proyectos",
        "herramienta": "glosario",
    })


@login_required
@require_http_methods(["GET", "POST"])
def termino_editar(request, pk, termino_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    termino = get_object_or_404(Termino, pk=termino_pk, proyecto=proyecto)
    form = TerminoForm(request.POST or None, instance=termino, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Término actualizado.")
        return redirect("glosario", pk=proyecto.pk)
    return render(request, "core/termino_form.html", {"proyecto": proyecto, "termino": termino, "form": form, "seccion": "proyectos"})


@login_required
@require_http_methods(["GET", "POST"])
def termino_eliminar(request, pk, termino_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    termino = get_object_or_404(Termino, pk=termino_pk, proyecto=proyecto)
    if request.method == "POST":
        nombre = termino.nombre
        termino.delete()
        messages.success(request, f"Término «{nombre}» eliminado.")
        return redirect("glosario", pk=proyecto.pk)
    return render(request, "core/termino_eliminar.html", {"proyecto": proyecto, "termino": termino, "seccion": "proyectos"})


@login_required
@require_POST
def termino_api(request, pk):
    """Crear o editar un término desde el panel del editor. JSON: {id?, nombre, definicion, categoria}."""
    proyecto = _proyecto_del_usuario(request, pk)
    try:
        datos = json.loads(request.body or b"{}")
        if not isinstance(datos, dict):
            raise ValueError
    except ValueError:
        return JsonResponse({"error": "Solicitud inválida"}, status=400)
    termino = None
    if datos.get("id"):
        termino = get_object_or_404(Termino, pk=datos["id"], proyecto=proyecto)
    form = TerminoForm({k: datos.get(k, "") for k in ("nombre", "definicion", "categoria")},
                       instance=termino, proyecto=proyecto)
    if not form.is_valid():
        return JsonResponse({"errores": {c: [e for e in errs] for c, errs in form.errors.items()}}, status=400)
    nuevo = form.save(commit=False)
    nuevo.proyecto = proyecto
    nuevo.save()
    return JsonResponse({"ok": True, "termino": _termino_a_dict(nuevo)}, status=200 if termino else 201)


@login_required
@require_POST
def termino_api_eliminar(request, pk, termino_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    get_object_or_404(Termino, pk=termino_pk, proyecto=proyecto).delete()
    return JsonResponse({"ok": True})


# --- Panel del editor: endpoints JSON (HU-09, HU-10) ---------------------------

MAX_SELECCION = 80  # una selección más larga no es un nombre


@login_required
@require_GET
def ficha_consulta(request, pk):
    """HU-10: ficha que coincide con el texto seleccionado (nombre o alias). Registra el evento."""
    proyecto = _proyecto_del_usuario(request, pk)
    texto = " ".join(request.GET.get("nombre", "").split())[:MAX_SELECCION]
    ficha = buscar_ficha(proyecto, texto)
    if ficha is None:
        return JsonResponse({"encontrada": False, "nombre": texto})
    if request.GET.get("registrar") != "0":  # «0»: abrir una ficha desde la lista no cuenta como consulta
        # Con el nombre subrayado en el texto, un clic repetido no debe inflar la métrica: una por ficha cada 5 s.
        reciente = EventoUso.objects.filter(
            usuario=request.user, proyecto=proyecto, tipo=EventoUso.Tipo.CONSULTA_FICHA,
            fecha__gte=timezone.now() - timedelta(seconds=5)).exists()
        if not reciente:
            EventoUso.objects.create(usuario=request.user, proyecto=proyecto, tipo=EventoUso.Tipo.CONSULTA_FICHA)
    return JsonResponse({"encontrada": True, "ficha": ficha_a_dict(ficha)})


@login_required
@require_POST
def ficha_rapida(request, pk):
    """«Crear ficha con este nombre»: crea un personaje solo con el nombre."""
    proyecto = _proyecto_del_usuario(request, pk)
    try:
        nombre = " ".join(str(json.loads(request.body or b"{}").get("nombre", "")).split())[:120]
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Solicitud inválida"}, status=400)
    if not nombre:
        return JsonResponse({"error": "Escribe un nombre"}, status=400)
    if buscar_ficha(proyecto, nombre):
        return JsonResponse({"error": "Ya existe una ficha con ese nombre"}, status=409)
    ficha = Ficha.objects.create(proyecto=proyecto, nombre=nombre)
    return JsonResponse({"ficha": ficha_a_dict(ficha)}, status=201)


# --- Relaciones entre fichas ---------------------------------------------------------------

def _ficha_json(f):
    return {"id": f.pk, "nombre": f.nombre, "color": f.color, "inicial": f.inicial}


@login_required
@require_http_methods(["GET", "POST"])
def relaciones(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    inicial = {}
    de = request.GET.get("de", "")
    if de.isdigit() and proyecto.fichas.filter(pk=int(de)).exists():
        inicial["origen"] = int(de)
    form = RelacionForm(request.POST or None, proyecto=proyecto, initial=inicial)
    if request.method == "POST" and form.is_valid():
        r = form.save(commit=False)
        r.proyecto = proyecto
        r.save()
        messages.success(request, "Relación guardada.")
        return redirect("relaciones", pk=proyecto.pk)
    categoria = request.GET.get("categoria", "")
    lista = proyecto.relaciones.select_related("origen", "destino")
    if categoria in Relacion.Categoria.values:
        lista = lista.filter(categoria=categoria)
    lista = list(lista)
    nodos = {}
    for r in lista:
        nodos[r.origen_id] = r.origen
        nodos[r.destino_id] = r.destino
    mapa = {
        "nodos": [_ficha_json(f) for f in nodos.values()],
        "aristas": [{"origen": r.origen_id, "destino": r.destino_id, "texto": r.texto} for r in lista],
    }
    return render(request, "core/relaciones.html", {
        "proyecto": proyecto, "form": form, "relaciones": lista, "mapa": mapa, "categoria": categoria,
        "categorias": Relacion.Categoria.choices, "herramienta": "relaciones", "hay_fichas": proyecto.fichas.count() >= 2,
    })


@login_required
@require_http_methods(["GET", "POST"])
def relacion_editar(request, pk, relacion_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    relacion = get_object_or_404(Relacion, pk=relacion_pk, proyecto=proyecto)
    form = RelacionForm(request.POST or None, instance=relacion, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Relación actualizada.")
        return redirect("relaciones", pk=proyecto.pk)
    return render(request, "core/relacion_form.html", {"proyecto": proyecto, "form": form, "relacion": relacion,
                                                       "herramienta": "relaciones"})


@login_required
@require_http_methods(["GET", "POST"])
def relacion_eliminar(request, pk, relacion_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    relacion = get_object_or_404(Relacion, pk=relacion_pk, proyecto=proyecto)
    if request.method == "POST":
        relacion.delete()
        messages.success(request, "Relación eliminada.")
        return redirect("relaciones", pk=proyecto.pk)
    return render(request, "core/relacion_eliminar.html", {"proyecto": proyecto, "relacion": relacion,
                                                           "herramienta": "relaciones"})


# --- Línea de tiempo -------------------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def linea_tiempo(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    form = EventoTramaForm(request.POST or None, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Evento agregado a la línea de tiempo.")
        return redirect("linea_tiempo", pk=proyecto.pk)
    eventos = list(proyecto.eventos_trama.select_related("capitulo").prefetch_related("participantes"))
    etapas = []
    for e in eventos:
        if e.etapa.lower() not in [x.lower() for x in etapas]:
            etapas.append(e.etapa)
    carriles = {}
    sin_personaje = []
    for e in eventos:
        quienes = list(e.participantes.all())
        for f in quienes:
            carriles.setdefault(f.pk, {"ficha": f, "eventos": []})["eventos"].append(e)
        if not quienes:
            sin_personaje.append(e)
    columnas = {e.pk: [x.lower() for x in etapas].index(e.etapa.lower()) for e in eventos}
    lista_carriles = sorted(carriles.values(), key=lambda c: c["ficha"].nombre.lower())
    for c in lista_carriles:
        c["celdas"] = [{"evento": e, "col": columnas[e.pk]} for e in c["eventos"]]
    if sin_personaje:
        lista_carriles.append({"ficha": None, "celdas": [{"evento": e, "col": columnas[e.pk]} for e in sin_personaje]})
    return render(request, "core/linea_tiempo.html", {
        "proyecto": proyecto, "form": form, "etapas": etapas, "carriles": lista_carriles, "total": len(eventos),
        "herramienta": "linea", "ancho": max(len(etapas), 1),
    })


@login_required
@require_http_methods(["GET", "POST"])
def evento_editar(request, pk, evento_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    evento = get_object_or_404(EventoTrama, pk=evento_pk, proyecto=proyecto)
    form = EventoTramaForm(request.POST or None, instance=evento, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Evento actualizado.")
        return redirect("linea_tiempo", pk=proyecto.pk)
    return render(request, "core/evento_form.html", {
        "proyecto": proyecto, "form": form, "evento": evento, "herramienta": "linea",
        "etapas": sorted({e.etapa for e in proyecto.eventos_trama.all()}, key=str.lower)})


@login_required
@require_http_methods(["GET", "POST"])
def evento_eliminar(request, pk, evento_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    evento = get_object_or_404(EventoTrama, pk=evento_pk, proyecto=proyecto)
    if request.method == "POST":
        evento.delete()
        messages.success(request, "Evento eliminado.")
        return redirect("linea_tiempo", pk=proyecto.pk)
    return render(request, "core/evento_eliminar.html", {"proyecto": proyecto, "evento": evento, "herramienta": "linea"})


# --- Tablón de ideas ---------------------------------------------------------------------------

def _posicion_libre(proyecto):
    """Siguiente hueco de una cuadrícula de notas, para que las nuevas no se amontonen."""
    n = proyecto.notas.count()
    return 24 + (n % 4) * 300, 24 + (n // 4) * 190


@login_required
@require_http_methods(["GET", "POST"])
def tablon(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    form = NotaForm(request.POST or None, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        nota = form.save(commit=False)
        nota.proyecto = proyecto
        nota.tipo = Nota.Tipo.IDEA
        nota.x, nota.y = _posicion_libre(proyecto)
        nota.save()
        messages.success(request, "Idea agregada al tablón.")
        return redirect("tablon", pk=proyecto.pk)
    tipo = request.GET.get("tipo", "")
    notas = proyecto.notas.select_related("ficha", "capitulo")
    if tipo in Nota.Tipo.values:
        notas = notas.filter(tipo=tipo)
    q = normalizar(request.GET.get("q", ""))
    notas = [n for n in notas if not q or q in normalizar(n.contenido)]
    return render(request, "core/tablon.html", {
        "proyecto": proyecto, "form": form, "notas": notas, "tipo": tipo, "q": request.GET.get("q", ""),
        "total": proyecto.notas.count(), "n_ideas": proyecto.notas.filter(tipo="idea").count(),
        "n_texto": proyecto.notas.filter(tipo="texto").count(), "herramienta": "tablon",
        "alto": max([n.y for n in notas] + [0]) + 260, "ancho": max([n.x for n in notas] + [0]) + 340,
    })


@login_required
@require_http_methods(["GET", "POST"])
def nota_editar(request, pk, nota_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    nota = get_object_or_404(Nota, pk=nota_pk, proyecto=proyecto)
    form = NotaForm(request.POST or None, instance=nota, proyecto=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Nota actualizada.")
        return redirect("tablon", pk=proyecto.pk)
    return render(request, "core/nota_form.html", {"proyecto": proyecto, "form": form, "nota": nota, "herramienta": "tablon"})


@login_required
@require_http_methods(["GET", "POST"])
def nota_eliminar(request, pk, nota_pk):
    proyecto = _proyecto_del_usuario(request, pk)
    nota = get_object_or_404(Nota, pk=nota_pk, proyecto=proyecto)
    if request.method == "POST":
        nota.delete()
        messages.success(request, "Nota eliminada.")
        return redirect("tablon", pk=proyecto.pk)
    return render(request, "core/nota_eliminar.html", {"proyecto": proyecto, "nota": nota, "herramienta": "tablon"})


@login_required
@require_POST
def nota_mover(request, pk, nota_pk):
    """Guarda la posición de una nota tras arrastrarla. JSON: {x, y}."""
    proyecto = _proyecto_del_usuario(request, pk)
    nota = get_object_or_404(Nota, pk=nota_pk, proyecto=proyecto)
    try:
        datos = json.loads(request.body or b"{}")
        x, y = int(datos["x"]), int(datos["y"])
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"ok": False, "error": "Posición no válida."}, status=400)
    nota.x, nota.y = max(0, min(x, 5000)), max(0, min(y, 5000))
    nota.save(update_fields=["x", "y"])
    return JsonResponse({"ok": True})


@login_required
@require_POST
def nota_desde_texto(request, pk):
    """Envía al tablón un pasaje seleccionado en el editor. JSON: {texto, capitulo}."""
    proyecto = _proyecto_del_usuario(request, pk)
    try:
        datos = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"ok": False, "error": "Datos no válidos."}, status=400)
    texto = " ".join(str(datos.get("texto", "")).split())
    if not texto:
        return JsonResponse({"ok": False, "error": "Selecciona un pasaje primero."}, status=400)
    capitulo = None
    if str(datos.get("capitulo", "")).isdigit():
        capitulo = proyecto.capitulos.filter(pk=int(datos["capitulo"])).first()
    ficha = buscar_ficha(proyecto, texto) if len(texto.split()) <= 6 else None
    x, y = _posicion_libre(proyecto)
    Nota.objects.create(proyecto=proyecto, tipo=Nota.Tipo.TEXTO, contenido=texto[:1000], capitulo=capitulo,
                        ficha=ficha, x=x, y=y)
    return JsonResponse({"ok": True, "total": proyecto.notas.count()})


@login_required
@require_POST
def tutorial_terminar(request):
    """El tutorial se completó u omitió: no vuelve a salir solo (se puede repetir con «Ver tutorial»)."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    perfil.onboarding_completado = True
    perfil.save(update_fields=["onboarding_completado"])
    return JsonResponse({"ok": True})
