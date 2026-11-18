"""Quien entra por primera vez con Google recibe lo mismo que quien se registra con correo (MVE: «Iniciar»)."""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from django.utils import timezone

from .models import Perfil
from .services.plantilla import crear_proyecto_de_muestra


class AdaptadorSocial(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        usuario = super().save_user(request, sociallogin, form)
        # Aceptar el aviso de privacidad se muestra junto al botón; continuar equivale a aceptarlo.
        Perfil.objects.update_or_create(user=usuario, defaults={"acepto_privacidad": timezone.now()})
        capitulo = crear_proyecto_de_muestra(usuario)
        request.session["destino_tras_google"] = reverse("editor", args=[capitulo.pk])
        return usuario

    def get_connect_redirect_url(self, request, socialaccount):
        return reverse("proyectos")


class AdaptadorCuenta(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # Tras el primer ingreso con Google se abre el capítulo de muestra (con el tutorial).
        destino = request.session.pop("destino_tras_google", None)
        return destino or super().get_login_redirect_url(request)
