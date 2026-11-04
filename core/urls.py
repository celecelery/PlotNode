from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views
from .forms import LoginForm, NuevaContrasenaForm, RecuperarForm

urlpatterns = [
    path("", views.inicio, name="inicio"),
    # Cuentas (HU-02): login, logout y recuperación de contraseña vienen de Django.
    path("cuentas/registro/", views.registro, name="registro"),
    path("cuentas/login/", auth_views.LoginView.as_view(authentication_form=LoginForm), name="login"),
    path("cuentas/password_reset/", auth_views.PasswordResetView.as_view(form_class=RecuperarForm), name="password_reset"),
    path("cuentas/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(form_class=NuevaContrasenaForm),
         name="password_reset_confirm"),
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
