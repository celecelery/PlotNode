from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    # Cuentas (HU-02): login, logout y recuperación de contraseña vienen de Django.
    path("cuentas/registro/", views.registro, name="registro"),
    path("cuentas/", include("django.contrib.auth.urls")),
    # Proyectos (HU-04)
    path("proyectos/", views.proyectos, name="proyectos"),
    path("proyectos/<int:pk>/", views.proyecto_abrir, name="proyecto_abrir"),
    path("proyectos/<int:pk>/editar/", views.proyecto_editar, name="proyecto_editar"),
    path("proyectos/<int:pk>/eliminar/", views.proyecto_eliminar, name="proyecto_eliminar"),
    # Editor (HU-06)
    path("capitulos/<int:pk>/", views.editor, name="editor"),
    path("capitulos/<int:pk>/guardar/", views.guardar_capitulo, name="guardar_capitulo"),
]
