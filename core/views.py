from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

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
    return render(request, "core/proyectos.html", {"form": form, "proyectos": lista})


@login_required
@require_http_methods(["GET", "POST"])
def proyecto_editar(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    form = ProyectoForm(request.POST or None, instance=proyecto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyecto actualizado.")
        return redirect("proyectos")
    return render(request, "core/proyecto_form.html", {"form": form, "proyecto": proyecto})


@login_required
@require_http_methods(["GET", "POST"])
def proyecto_eliminar(request, pk):
    proyecto = _proyecto_del_usuario(request, pk)
    if request.method == "POST":
        titulo = proyecto.titulo
        proyecto.delete()
        messages.success(request, f"Proyecto «{titulo}» eliminado.")
        return redirect("proyectos")
    return render(request, "core/proyecto_eliminar.html", {"proyecto": proyecto})
