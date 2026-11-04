from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Proyecto

User = get_user_model()


class CuentasTests(TestCase):
    def test_registro_crea_usuario_inicia_sesion_y_redirige(self):
        r = self.client.post(reverse("registro"), {
            "username": "lia", "email": "lia@ejemplo.com",
            "password1": "una-clave-larga-42", "password2": "una-clave-larga-42",
        })
        self.assertRedirects(r, reverse("proyectos"))
        self.assertTrue(User.objects.filter(username="lia").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="lia").pk)

    def test_registro_rechaza_correo_repetido(self):
        User.objects.create_user("ana", email="ana@ejemplo.com", password="x-clave-segura-1")
        r = self.client.post(reverse("registro"), {
            "username": "ana2", "email": "ANA@ejemplo.com",
            "password1": "una-clave-larga-42", "password2": "una-clave-larga-42",
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ya existe una cuenta con este correo")

    def test_vistas_privadas_piden_sesion(self):
        r = self.client.get(reverse("proyectos"))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('proyectos')}")

    def test_login_y_logout(self):
        User.objects.create_user("ana", password="x-clave-segura-1")
        r = self.client.post(reverse("login"), {"username": "ana", "password": "x-clave-segura-1"})
        self.assertRedirects(r, reverse("proyectos"))
        r = self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProyectosTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.beto = User.objects.create_user("beto", password="x-clave-segura-2")
        self.client.force_login(self.ana)

    def test_crear_proyecto_con_primer_capitulo(self):
        r = self.client.post(reverse("proyectos"), {"titulo": "La torre", "genero": "novela"})
        self.assertRedirects(r, reverse("proyectos"))
        p = Proyecto.objects.get(titulo="La torre")
        self.assertEqual(p.dueno, self.ana)
        self.assertEqual(p.capitulos.count(), 1)

    def test_lista_solo_muestra_proyectos_propios(self):
        Proyecto.objects.create(dueno=self.ana, titulo="Mío")
        Proyecto.objects.create(dueno=self.beto, titulo="Ajeno")
        r = self.client.get(reverse("proyectos"))
        self.assertContains(r, "Mío")
        self.assertNotContains(r, "Ajeno")

    def test_renombrar_y_eliminar_propio(self):
        p = Proyecto.objects.create(dueno=self.ana, titulo="Viejo")
        self.client.post(reverse("proyecto_editar", args=[p.pk]), {"titulo": "Nuevo", "genero": "fanfic"})
        p.refresh_from_db()
        self.assertEqual((p.titulo, p.genero), ("Nuevo", "fanfic"))
        self.client.post(reverse("proyecto_eliminar", args=[p.pk]))
        self.assertFalse(Proyecto.objects.filter(pk=p.pk).exists())

    def test_no_puede_tocar_proyectos_ajenos(self):
        ajeno = Proyecto.objects.create(dueno=self.beto, titulo="Ajeno")
        for nombre in ("proyecto_editar", "proyecto_eliminar"):
            self.assertEqual(self.client.get(reverse(nombre, args=[ajeno.pk])).status_code, 404)
            self.assertEqual(self.client.post(reverse(nombre, args=[ajeno.pk]), {"titulo": "Hackeado"}).status_code, 404)
        ajeno.refresh_from_db()
        self.assertEqual(ajeno.titulo, "Ajeno")
