import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import Capitulo, EventoUso, Proyecto

User = get_user_model()


class EventosTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.proyecto = Proyecto.objects.create(dueno=self.ana, titulo="La torre")
        self.cap = Capitulo.objects.create(proyecto=self.proyecto, titulo="Uno")
        self.client.force_login(self.ana)

    def guardar(self, html):
        return self.client.post(reverse("guardar_capitulo", args=[self.cap.pk]),
                                json.dumps({"contenido": html}), content_type="application/json")

    def sesiones(self):
        return EventoUso.objects.filter(tipo=EventoUso.Tipo.SESION_ESCRITURA, usuario=self.ana)

    def test_guardar_registra_una_sesion_con_las_palabras_escritas(self):
        self.guardar("<p>uno dos tres</p>")
        self.guardar("<p>uno dos tres cuatro cinco</p>")
        self.assertEqual(self.sesiones().count(), 1)
        sesion = self.sesiones().get()
        self.assertEqual((sesion.valor, sesion.proyecto), (5, self.proyecto))

    def test_borrar_texto_no_resta_ni_crea_eventos(self):
        self.guardar("<p>uno dos tres</p>")
        self.guardar("<p>uno</p>")
        self.assertEqual(self.sesiones().get().valor, 3)
        self.cap.refresh_from_db()
        solo_borrar = EventoUso.objects.count()
        self.guardar("")
        self.assertEqual(EventoUso.objects.count(), solo_borrar)

    def test_una_pausa_larga_abre_otra_sesion(self):
        self.guardar("<p>uno dos</p>")
        from datetime import timedelta
        EventoUso.objects.filter(pk=self.sesiones().get().pk).update(fecha=timezone.now() - timedelta(minutes=31))
        self.guardar("<p>uno dos tres cuatro</p>")
        self.assertEqual(sorted(self.sesiones().values_list("valor", flat=True)), [2, 2])

    def test_el_admin_filtra_eventos_por_tipo_y_usuario(self):
        admin = User.objects.create_superuser("root", "r@x.com", "x-clave-segura-9")
        self.guardar("<p>uno dos</p>")
        self.client.force_login(admin)
        r = self.client.get("/admin/core/eventouso/", {"tipo__exact": "sesion_escritura", "usuario__id__exact": self.ana.pk})
        self.assertContains(r, "ana")
        r = self.client.get("/admin/core/eventouso/", {"q": "ana"})
        self.assertEqual(r.status_code, 200)


class PortadaTests(TestCase):
    def test_portada_tiene_el_titular_y_el_registro(self):
        r = self.client.get(reverse("inicio"))
        self.assertContains(r, "Escribe tu novela sin perderte en tus notas ni cometer errores de continuidad")
        self.assertContains(r, reverse("registro"))

    def test_boton_de_lista_de_espera_solo_si_hay_url(self):
        self.assertNotContains(self.client.get(reverse("inicio")), "me avisen de las novedades")
        with override_settings(MAILERLITE_FORM_URL="https://example.com/form"):
            r = self.client.get(reverse("inicio"))
            self.assertContains(r, "https://example.com/form")
            self.assertContains(r, "me avisen de las novedades")
