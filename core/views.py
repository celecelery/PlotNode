import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import ProyectoForm, RegistroForm
from .models import Capitulo, Proyecto


def inicio(request):
    if request.user.is_authenticated:
        return redirect("proyectos")
    return render(request, "core/inicio.html")


@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("proyectos")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, f"¡Bienvenida/o a PlotNode, {usuario.username}!")
        return redirect("proyectos")
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
    """Abre el proyecto en su primer capítulo (lo crea si no hay ninguno)."""
    proyecto = _proyecto_del_usuario(request, pk)
    capitulo = proyecto.capitulos.first()
    if capitulo is None:
        capitulo = Capitulo.objects.create(proyecto=proyecto, titulo="Capítulo 1", orden=1)
    return redirect(capitulo)


@login_required
def editor(request, pk):
    capitulo = _capitulo_del_usuario(request, pk)
    return render(request, "core/editor.html", {
        "capitulo": capitulo,
        "proyecto": capitulo.proyecto,
        "capitulos": capitulo.proyecto.capitulos.all(),
    })


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
    capitulo.contenido = contenido
    capitulo.save()
    Proyecto.objects.filter(pk=capitulo.proyecto_id).update(actualizado=timezone.now())
    return JsonResponse({"ok": True, "palabras": capitulo.palabras,
                         "guardado": timezone.localtime(capitulo.actualizado).strftime("%H:%M")})
