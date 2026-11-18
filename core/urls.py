from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views
from .forms import LoginForm, NuevaContrasenaForm, RecuperarForm

urlpatterns = [
    path("", views.inicio, name="inicio"),
    # Cuentas (HU-02): login, logout y recuperación de contraseña vienen de Django.
    path("cuentas/registro/", views.registro, name="registro"),
    path("cuentas/login/", auth_views.LoginView.as_view(authentication_form=LoginForm), name="login"),
    path("cuentas/password_reset/", views.RecuperarContrasenaView.as_view(form_class=RecuperarForm), name="password_reset"),
    path("cuentas/password_reset/done/", views.RecuperarContrasenaEnviadaView.as_view(), name="password_reset_done"),
    path("cuentas/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(form_class=NuevaContrasenaForm),
         name="password_reset_confirm"),
    path("cuentas/tutorial/terminar/", views.tutorial_terminar, name="tutorial_terminar"),
    path("cuentas/", include("django.contrib.auth.urls")),
    # Proyectos (HU-04)
    path("proyectos/", views.proyectos, name="proyectos"),
    path("proyectos/<int:pk>/", views.proyecto_abrir, name="proyecto_abrir"),
    path("proyectos/<int:pk>/editar/", views.proyecto_editar, name="proyecto_editar"),
    path("proyectos/<int:pk>/eliminar/", views.proyecto_eliminar, name="proyecto_eliminar"),
    # Capítulos (HU-05)
    path("proyectos/<int:pk>/capitulos/", views.capitulos_gestion, name="capitulos_gestion"),
    path("proyectos/<int:pk>/capitulos/nuevo/", views.capitulo_nuevo, name="capitulo_nuevo"),
    path("capitulos/<int:pk>/renombrar/", views.capitulo_renombrar, name="capitulo_renombrar"),
    path("capitulos/<int:pk>/mover/", views.capitulo_mover, name="capitulo_mover"),
    path("capitulos/<int:pk>/eliminar/", views.capitulo_eliminar, name="capitulo_eliminar"),
    # Fichas (HU-07) y panel del editor (HU-09, HU-10)
    path("proyectos/<int:pk>/fichas/", views.fichas_lista, name="fichas_lista"),
    path("proyectos/<int:pk>/fichas/nueva/", views.ficha_form, name="ficha_nueva"),
    path("proyectos/<int:pk>/fichas/consulta/", views.ficha_consulta, name="ficha_consulta"),
    path("proyectos/<int:pk>/fichas/rapida/", views.ficha_rapida, name="ficha_rapida"),
    path("proyectos/<int:pk>/fichas/<int:ficha_pk>/", views.ficha_form, name="ficha_editar"),
    path("proyectos/<int:pk>/fichas/<int:ficha_pk>/eliminar/", views.ficha_eliminar, name="ficha_eliminar"),
    # Glosario (HU-29, HU-30)
    path("proyectos/<int:pk>/glosario/", views.glosario, name="glosario"),
    path("proyectos/<int:pk>/glosario/api/", views.termino_api, name="termino_api"),
    path("proyectos/<int:pk>/glosario/<int:termino_pk>/", views.termino_editar, name="termino_editar"),
    path("proyectos/<int:pk>/glosario/<int:termino_pk>/eliminar/", views.termino_eliminar, name="termino_eliminar"),
    path("proyectos/<int:pk>/glosario/<int:termino_pk>/borrar/", views.termino_api_eliminar, name="termino_api_eliminar"),
    # Relaciones, línea de tiempo y tablón de ideas (iteración 3)
    path("proyectos/<int:pk>/relaciones/", views.relaciones, name="relaciones"),
    path("proyectos/<int:pk>/relaciones/<int:relacion_pk>/", views.relacion_editar, name="relacion_editar"),
    path("proyectos/<int:pk>/relaciones/<int:relacion_pk>/eliminar/", views.relacion_eliminar, name="relacion_eliminar"),
    path("proyectos/<int:pk>/linea-de-tiempo/", views.linea_tiempo, name="linea_tiempo"),
    path("proyectos/<int:pk>/linea-de-tiempo/<int:evento_pk>/", views.evento_editar, name="evento_editar"),
    path("proyectos/<int:pk>/linea-de-tiempo/<int:evento_pk>/eliminar/", views.evento_eliminar, name="evento_eliminar"),
    path("proyectos/<int:pk>/tablon/", views.tablon, name="tablon"),
    path("proyectos/<int:pk>/tablon/desde-texto/", views.nota_desde_texto, name="nota_desde_texto"),
    path("proyectos/<int:pk>/tablon/<int:nota_pk>/", views.nota_editar, name="nota_editar"),
    path("proyectos/<int:pk>/tablon/<int:nota_pk>/eliminar/", views.nota_eliminar, name="nota_eliminar"),
    path("proyectos/<int:pk>/tablon/<int:nota_pk>/mover/", views.nota_mover, name="nota_mover"),
    # Editor (HU-06)
    path("capitulos/<int:pk>/", views.editor, name="editor"),
    path("capitulos/<int:pk>/guardar/", views.guardar_capitulo, name="guardar_capitulo"),
]
