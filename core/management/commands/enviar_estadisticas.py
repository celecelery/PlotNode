"""HU-17: sube a MailerLite las estadísticas de la semana de cada escritora.

El comando solo actualiza los campos del suscriptor (palabras_semana y consultas_semana);
la campaña semanal con la invitación para compartir el acceso anticipado la envía el equipo desde MailerLite.

    python manage.py enviar_estadisticas            # envía
    python manage.py enviar_estadisticas --dry-run  # solo muestra lo que enviaría

Necesita MAILERLITE_API_KEY (variable de entorno). Los campos palabras_semana y consultas_semana
deben existir en MailerLite (Subscribers > Fields).
"""
import json
import urllib.error
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum
from django.utils import timezone

from core.models import EventoUso

URL = "https://connect.mailerlite.com/api/subscribers"


def estadisticas_de_la_semana(dias=7):
    """{usuario: (palabras, consultas)} de quienes tienen correo, aunque no hayan escrito nada."""
    desde = timezone.now() - timedelta(days=dias)
    eventos = EventoUso.objects.filter(fecha__gte=desde)
    palabras = dict(eventos.filter(tipo=EventoUso.Tipo.SESION_ESCRITURA).values_list("usuario").annotate(t=Sum("valor")))
    consultas = dict(eventos.filter(tipo=EventoUso.Tipo.CONSULTA_FICHA).values_list("usuario").annotate(t=Count("id")))
    usuarios = get_user_model().objects.exclude(email="").filter(is_active=True)
    return [(u, palabras.get(u.pk, 0), consultas.get(u.pk, 0)) for u in usuarios]


def subir(clave, correo, palabras, consultas, abrir=urllib.request.urlopen):
    cuerpo = json.dumps({"email": correo, "fields": {"palabras_semana": palabras, "consultas_semana": consultas}}).encode()
    peticion = urllib.request.Request(URL, data=cuerpo, method="POST", headers={
        "Authorization": f"Bearer {clave}", "Content-Type": "application/json", "Accept": "application/json"})
    with abrir(peticion, timeout=15) as r:
        return r.status


class Command(BaseCommand):
    help = "Actualiza en MailerLite las palabras escritas y las fichas consultadas de la última semana."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Muestra los datos sin enviarlos.")
        parser.add_argument("--dias", type=int, default=7, help="Ventana de días (7 por defecto).")

    def handle(self, *args, dry_run=False, dias=7, **opciones):
        filas = estadisticas_de_la_semana(dias)
        if dry_run:
            for u, palabras, consultas in filas:
                self.stdout.write(f"{u.email}: palabras_semana={palabras} consultas_semana={consultas}")
            self.stdout.write(f"{len(filas)} suscriptoras (no se envió nada).")
            return
        clave = settings.MAILERLITE_API_KEY
        if not clave:
            raise CommandError("Falta MAILERLITE_API_KEY. Defínela como variable de entorno (o usa --dry-run).")
        enviadas = errores = 0
        for u, palabras, consultas in filas:
            try:
                subir(clave, u.email, palabras, consultas)
                enviadas += 1
            except (urllib.error.URLError, OSError) as e:
                errores += 1
                self.stderr.write(f"No se pudo actualizar a {u.email}: {e}")
        self.stdout.write(f"Actualizadas: {enviadas}. Con error: {errores}.")
        if errores:
            raise CommandError("Algunas suscriptoras no se actualizaron.")
