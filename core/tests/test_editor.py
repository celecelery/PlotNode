import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Capitulo, Proyecto

User = get_user_model()


class EditorTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.beto = User.objects.create_user("beto", password="x-clave-segura-2")
        self.proyecto = Proyecto.objects.create(dueno=self.ana, titulo="La torre")
        self.cap = Capitulo.objects.create(proyecto=self.proyecto, titulo="Capítulo 1")
        self.client.force_login(self.ana)

    def guardar(self, cap, contenido, cliente=None):
        cliente = cliente or self.client
        return cliente.post(reverse("guardar_capitulo", args=[cap.pk]),
                            data=json.dumps({"contenido": contenido}), content_type="application/json")

    def test_abrir_proyecto_lleva_al_primer_capitulo(self):
        r = self.client.get(reverse("proyecto_abrir", args=[self.proyecto.pk]))
        self.assertRedirects(r, reverse("editor", args=[self.cap.pk]))

    def test_abrir_proyecto_sin_capitulos_crea_uno(self):
        vacio = Proyecto.objects.create(dueno=self.ana, titulo="Vacío")
        self.client.get(reverse("proyecto_abrir", args=[vacio.pk]))
        self.assertEqual(vacio.capitulos.count(), 1)

    def test_editor_muestra_capitulo_y_contenido_escapado(self):
        self.cap.contenido = "<p>Hola</p><script>alert(1)</script>"
        self.cap.save()
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        self.assertContains(r, "Capítulo 1")
        # El contenido viaja dentro de json_script, con < escapado: nunca como <script> ejecutable.
        self.assertNotContains(r, "<script>alert(1)</script>")

    def test_autoguardado_guarda_y_cuenta_palabras(self):
        r = self.guardar(self.cap, "<p>Ana&nbsp;parpadeó; sus <em>ojos</em> cafés.</p>")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.assertEqual(r.json()["palabras"], 5)
        self.cap.refresh_from_db()
        self.assertIn("ojos", self.cap.contenido)

    def test_autoguardado_rechaza_datos_invalidos(self):
        url = reverse("guardar_capitulo", args=[self.cap.pk])
        self.assertEqual(self.client.post(url, data="no es json", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, data=json.dumps({"contenido": 5}), content_type="application/json").status_code, 400)
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_no_puede_ver_ni_guardar_capitulos_ajenos(self):
        self.client.force_login(self.beto)
        self.assertEqual(self.client.get(reverse("editor", args=[self.cap.pk])).status_code, 404)
        self.assertEqual(self.guardar(self.cap, "<p>Hackeado</p>").status_code, 404)
        self.assertEqual(self.client.get(reverse("proyecto_abrir", args=[self.proyecto.pk])).status_code, 404)
        self.cap.refresh_from_db()
        self.assertNotIn("Hackeado", self.cap.contenido)

    def test_autoguardado_sin_sesion_no_guarda(self):
        self.client.logout()
        r = self.guardar(self.cap, "<p>Anónimo</p>")
        self.assertEqual(r.status_code, 302)
        self.cap.refresh_from_db()
        self.assertEqual(self.cap.contenido, "")

    def test_autoguardado_exige_csrf(self):
        from django.test import Client
        estricto = Client(enforce_csrf_checks=True)
        estricto.force_login(self.ana)
        self.assertEqual(self.guardar(self.cap, "<p>Sin token</p>", cliente=estricto).status_code, 403)
