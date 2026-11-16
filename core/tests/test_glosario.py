import json

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from core.models import Capitulo, Proyecto, Termino

User = get_user_model()


class GlosarioBase(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.beto = User.objects.create_user("beto", password="x-clave-segura-2")
        self.p = Proyecto.objects.create(dueno=self.ana, titulo="La torre")
        self.cap = Capitulo.objects.create(proyecto=self.p, titulo="Uno")
        self.orbe = Termino.objects.create(proyecto=self.p, nombre="Orbe de Ilvar", definicion="Muestra el pasado.", categoria="Objeto")
        self.client.force_login(self.ana)

    def api(self, datos, cliente=None):
        return (cliente or self.client).post(reverse("termino_api", args=[self.p.pk]), json.dumps(datos), content_type="application/json")


class GlosarioPaginaTests(GlosarioBase):
    def test_la_clave_normaliza_y_es_unica_por_proyecto(self):
        self.assertEqual(self.orbe.clave, "orbe de ilvar")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Termino.objects.create(proyecto=self.p, nombre="ORBE de Ilvar", definicion="Otra")
        otro = Proyecto.objects.create(dueno=self.ana, titulo="Otro")
        Termino.objects.create(proyecto=otro, nombre="Orbe de Ilvar", definicion="Mismo nombre en otro proyecto")

    def test_la_pagina_lista_los_terminos(self):
        r = self.client.get(reverse("glosario", args=[self.p.pk]))
        self.assertContains(r, "Orbe de Ilvar")
        self.assertContains(r, "Muestra el pasado.")

    def test_agregar_un_termino(self):
        r = self.client.post(reverse("glosario", args=[self.p.pk]), {"nombre": " Faro  gris ", "definicion": "Torre de señales", "categoria": "Lugar"})
        self.assertRedirects(r, reverse("glosario", args=[self.p.pk]))
        t = Termino.objects.get(clave="faro gris")
        self.assertEqual((t.nombre, t.proyecto), ("Faro gris", self.p))

    def test_no_repite_terminos_sin_distinguir_mayusculas_ni_acentos(self):
        r = self.client.post(reverse("glosario", args=[self.p.pk]), {"nombre": "orbe DE ílvar", "definicion": "x"})
        self.assertContains(r, "Ya existe un término con ese nombre")
        self.assertEqual(Termino.objects.count(), 1)

    def test_exige_nombre_y_definicion(self):
        r = self.client.post(reverse("glosario", args=[self.p.pk]), {"nombre": "  ", "definicion": "  "})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Termino.objects.count(), 1)

    def test_busqueda_por_nombre_o_definicion(self):
        Termino.objects.create(proyecto=self.p, nombre="Faro gris", definicion="Torre de señales")
        url = reverse("glosario", args=[self.p.pk])
        r = self.client.get(url, {"q": "SEÑALES"})
        self.assertContains(r, "Faro gris")
        self.assertNotContains(r, "Muestra el pasado.")
        self.assertContains(self.client.get(url, {"q": "zzz"}), "Nada coincide con tu búsqueda")

    def test_editar_y_eliminar_con_confirmacion(self):
        self.client.post(reverse("termino_editar", args=[self.p.pk, self.orbe.pk]), {"nombre": "Orbe", "definicion": "Nueva", "categoria": ""})
        self.orbe.refresh_from_db()
        self.assertEqual((self.orbe.nombre, self.orbe.clave), ("Orbe", "orbe"))
        url = reverse("termino_eliminar", args=[self.p.pk, self.orbe.pk])
        self.assertContains(self.client.get(url), "¿Eliminar «Orbe»?")
        self.assertEqual(Termino.objects.count(), 1)
        self.client.post(url)
        self.assertEqual(Termino.objects.count(), 0)

    def test_editar_un_termino_no_choca_consigo_mismo(self):
        r = self.client.post(reverse("termino_editar", args=[self.p.pk, self.orbe.pk]), {"nombre": "Orbe de Ilvar", "definicion": "Cambia"})
        self.assertEqual(r.status_code, 302)

    def test_otra_cuenta_recibe_404(self):
        self.client.force_login(self.beto)
        for nombre, args in (("glosario", [self.p.pk]), ("termino_editar", [self.p.pk, self.orbe.pk]), ("termino_eliminar", [self.p.pk, self.orbe.pk])):
            self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 404, nombre)
        self.assertEqual(self.client.post(reverse("glosario", args=[self.p.pk]), {"nombre": "x", "definicion": "y"}).status_code, 404)
        self.assertEqual(self.client.post(reverse("termino_eliminar", args=[self.p.pk, self.orbe.pk])).status_code, 404)
        self.assertEqual(Termino.objects.count(), 1)

    def test_requiere_sesion(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("glosario", args=[self.p.pk])).status_code, 302)


class GlosarioApiTests(GlosarioBase):
    def test_crear_desde_el_panel(self):
        r = self.api({"nombre": "Faro gris", "definicion": "Torre de señales", "categoria": "Lugar"})
        self.assertEqual(r.status_code, 201)
        t = r.json()["termino"]
        self.assertEqual((t["nombre"], t["categoria"]), ("Faro gris", "Lugar"))
        self.assertTrue(Termino.objects.filter(pk=t["id"], proyecto=self.p).exists())

    def test_editar_desde_el_panel(self):
        r = self.api({"id": self.orbe.pk, "nombre": "Orbe", "definicion": "Otra definición", "categoria": ""})
        self.assertEqual(r.status_code, 200)
        self.orbe.refresh_from_db()
        self.assertEqual((self.orbe.nombre, self.orbe.definicion), ("Orbe", "Otra definición"))
        self.assertEqual(Termino.objects.count(), 1)

    def test_errores_de_validacion_con_estado_400(self):
        r = self.api({"nombre": "orbe de ilvar", "definicion": "x"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("nombre", r.json()["errores"])
        self.assertEqual(self.api({"nombre": "", "definicion": ""}).status_code, 400)

    def test_json_invalido(self):
        r = self.client.post(reverse("termino_api", args=[self.p.pk]), "no es json", content_type="application/json")
        self.assertEqual(r.status_code, 400)
        r = self.client.post(reverse("termino_api", args=[self.p.pk]), "[1, 2]", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_borrar_desde_el_panel(self):
        r = self.client.post(reverse("termino_api_eliminar", args=[self.p.pk, self.orbe.pk]))
        self.assertEqual(r.json(), {"ok": True})
        self.assertEqual(Termino.objects.count(), 0)

    def test_la_api_exige_post_y_dueno(self):
        self.assertEqual(self.client.get(reverse("termino_api", args=[self.p.pk])).status_code, 405)
        self.client.force_login(self.beto)
        self.assertEqual(self.api({"nombre": "x", "definicion": "y"}).status_code, 404)
        self.assertEqual(self.api({"id": self.orbe.pk, "nombre": "x", "definicion": "y"}).status_code, 404)
        self.assertEqual(self.client.post(reverse("termino_api_eliminar", args=[self.p.pk, self.orbe.pk])).status_code, 404)
        self.assertEqual(Termino.objects.get().nombre, "Orbe de Ilvar")

    def test_no_se_puede_editar_un_termino_de_otro_proyecto_del_mismo_dueno(self):
        otro = Proyecto.objects.create(dueno=self.ana, titulo="Otro")
        ajeno = Termino.objects.create(proyecto=otro, nombre="Ajeno", definicion="x")
        self.assertEqual(self.api({"id": ajeno.pk, "nombre": "Cambio", "definicion": "y"}).status_code, 404)


class GlosarioEnElEditorTests(GlosarioBase):
    def test_el_editor_trae_los_terminos_y_el_boton_de_la_barra(self):
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        self.assertContains(r, 'id="terminos-inicial"')
        self.assertContains(r, "Orbe de Ilvar")
        self.assertContains(r, 'id="btn-glosario"')
        self.assertContains(r, 'id="tooltip-glosario"')

    def test_las_palabras_marcadas_se_guardan_con_el_capitulo(self):
        html = f'<p>Ana tomó el <span class="glosario" data-termino="{self.orbe.pk}">orbe</span> con calma.</p>'
        r = self.client.post(reverse("guardar_capitulo", args=[self.cap.pk]), json.dumps({"contenido": html}), content_type="application/json")
        self.assertEqual(r.json()["palabras"], 6)
        self.cap.refresh_from_db()
        self.assertIn(f'data-termino="{self.orbe.pk}"', self.cap.contenido)

    def test_json_del_editor_escapa_html_de_los_terminos(self):
        Termino.objects.create(proyecto=self.p, nombre="Trampa", definicion="</script><b>x</b>")
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        self.assertNotContains(r, "</script><b>x</b>")


class BarraYPanelTests(GlosarioBase):
    def test_la_barra_vertical_tiene_sus_secciones_y_botones(self):
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        for texto in ("Texto", "Estilo", "Alineación", "Glosario", 'id="btn-barra"', 'class="ql-divider"', 'class="ql-font"',
                      'class="ql-size"', 'class="ql-strike"', 'class="ql-align"', 'class="ql-link"', 'class="ql-image"', 'class="ql-clean"'):
            self.assertContains(r, texto)
        self.assertContains(r, 'aria-label="Negritas"')

    def test_el_panel_tiene_pestanas_asa_y_estado_inicial(self):
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        for texto in ('role="tablist"', "Fichas", "Glosario", "Muletillas", 'id="reparto-asa"', 'role="separator"',
                      'data-reparto="abierto"', 'id="btn-reparto"', 'id="muletillas-umbral"'):
            self.assertContains(r, texto)
        self.assertContains(r, reverse("ficha_nueva", args=[self.p.pk]))

    def test_cargan_todos_los_scripts_del_editor(self):
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        for js in ("editor.js", "panel.js", "glosario.js", "muletillas.js", "sinonimos.js", "ficha-form.js"):
            self.assertContains(r, js)

    def test_el_contenido_con_formato_se_guarda(self):
        html = '<p style="font-size: 22px;" class="ql-align-center">Hola <strong>mundo</strong></p><hr><p>Fin</p>'
        r = self.client.post(reverse("guardar_capitulo", args=[self.cap.pk]), json.dumps({"contenido": html}), content_type="application/json")
        self.assertEqual(r.json()["palabras"], 3)
        self.cap.refresh_from_db()
        self.assertIn("<hr>", self.cap.contenido)
