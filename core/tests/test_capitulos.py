from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Capitulo, Proyecto

User = get_user_model()


class CapitulosTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.beto = User.objects.create_user("beto", password="x-clave-segura-2")
        self.proyecto = Proyecto.objects.create(dueno=self.ana, titulo="La torre")
        self.c1 = Capitulo.objects.create(proyecto=self.proyecto, titulo="Uno", orden=1, contenido="<p>Hola mundo</p>")
        self.c2 = Capitulo.objects.create(proyecto=self.proyecto, titulo="Dos", orden=2)
        self.c3 = Capitulo.objects.create(proyecto=self.proyecto, titulo="Tres", orden=3)
        self.client.force_login(self.ana)

    def titulos(self):
        return list(self.proyecto.capitulos.values_list("titulo", flat=True))

    def test_pagina_de_gestion_lista_los_capitulos(self):
        r = self.client.get(reverse("capitulos_gestion", args=[self.proyecto.pk]))
        for t in ("Uno", "Dos", "Tres"):
            self.assertContains(r, t)

    def test_crear_capitulo_va_al_final_y_abre_el_editor(self):
        r = self.client.post(reverse("capitulo_nuevo", args=[self.proyecto.pk]))
        nuevo = self.proyecto.capitulos.last()
        self.assertEqual((nuevo.titulo, nuevo.orden), ("Capítulo 4", 4))
        self.assertRedirects(r, reverse("editor", args=[nuevo.pk]))

    def test_renombrar(self):
        self.client.post(reverse("capitulo_renombrar", args=[self.c1.pk]), {"titulo": "  El comienzo "})
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.titulo, "El comienzo")
        self.assertEqual(self.c1.palabras, 2)  # renombrar no pierde el texto

    def test_renombrar_con_titulo_vacio_no_cambia(self):
        self.client.post(reverse("capitulo_renombrar", args=[self.c1.pk]), {"titulo": "   "})
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.titulo, "Uno")

    def test_mover_arriba_y_abajo(self):
        self.client.post(reverse("capitulo_mover", args=[self.c3.pk]), {"direccion": "arriba"})
        self.assertEqual(self.titulos(), ["Uno", "Tres", "Dos"])
        self.client.post(reverse("capitulo_mover", args=[self.c1.pk]), {"direccion": "abajo"})
        self.assertEqual(self.titulos(), ["Tres", "Uno", "Dos"])

    def test_mover_el_primero_hacia_arriba_no_hace_nada(self):
        self.client.post(reverse("capitulo_mover", args=[self.c1.pk]), {"direccion": "arriba"})
        self.assertEqual(self.titulos(), ["Uno", "Dos", "Tres"])

    def test_eliminar_pide_confirmacion_y_reordena(self):
        url = reverse("capitulo_eliminar", args=[self.c2.pk])
        self.assertContains(self.client.get(url), "¿Eliminar «Dos»?")
        self.assertEqual(self.proyecto.capitulos.count(), 3)  # el GET no borra
        self.client.post(url)
        self.assertEqual(self.titulos(), ["Uno", "Tres"])
        self.assertEqual(list(self.proyecto.capitulos.values_list("orden", flat=True)), [1, 2])

    def test_no_se_elimina_el_ultimo_capitulo(self):
        self.c2.delete()
        self.c3.delete()
        self.client.post(reverse("capitulo_eliminar", args=[self.c1.pk]))
        self.assertEqual(self.proyecto.capitulos.count(), 1)

    def test_el_editor_ofrece_nuevo_capitulo_y_gestion(self):
        r = self.client.get(reverse("editor", args=[self.c1.pk]))
        self.assertContains(r, reverse("capitulo_nuevo", args=[self.proyecto.pk]))
        self.assertContains(r, reverse("capitulos_gestion", args=[self.proyecto.pk]))

    def test_acciones_exigen_post(self):
        for nombre, pk in (("capitulo_nuevo", self.proyecto.pk), ("capitulo_renombrar", self.c1.pk), ("capitulo_mover", self.c1.pk)):
            self.assertEqual(self.client.get(reverse(nombre, args=[pk])).status_code, 405, nombre)

    def test_otra_cuenta_recibe_404(self):
        self.client.force_login(self.beto)
        self.assertEqual(self.client.get(reverse("capitulos_gestion", args=[self.proyecto.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("capitulo_nuevo", args=[self.proyecto.pk])).status_code, 404)
        for nombre in ("capitulo_renombrar", "capitulo_mover"):
            self.assertEqual(self.client.post(reverse(nombre, args=[self.c1.pk]), {"titulo": "x"}).status_code, 404, nombre)
        self.assertEqual(self.client.post(reverse("capitulo_eliminar", args=[self.c1.pk])).status_code, 404)
        self.assertEqual(self.proyecto.capitulos.count(), 3)

    def test_requiere_sesion(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("capitulos_gestion", args=[self.proyecto.pk])).status_code, 302)
