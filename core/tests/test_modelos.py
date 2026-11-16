from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Capitulo, Ficha, Perfil, Proyecto
from core.utils import contar_palabras, normalizar

User = get_user_model()


class UtilidadesTests(TestCase):
    def test_normalizar_quita_acentos_mayusculas_y_espacios(self):
        self.assertEqual(normalizar("  La Capitána  "), "la capitana")
        self.assertEqual(normalizar("ÑOÑO"), "nono")

    def test_contar_palabras(self):
        self.assertEqual(contar_palabras("Ana parpadeó; sus ojos cafés..."), 5)
        self.assertEqual(contar_palabras(""), 0)


class ModelosTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="clave-segura-123")
        self.proyecto = Proyecto.objects.create(dueno=self.ana, titulo="La torre")

    def test_se_crea_perfil_al_registrar_usuario(self):
        self.assertTrue(Perfil.objects.filter(user=self.ana).exists())

    def test_capitulo_cuenta_palabras_sin_html(self):
        cap = Capitulo.objects.create(proyecto=self.proyecto, titulo="Uno",
                                      contenido="<p>Había una <strong>vez</strong> una torre.</p>")
        self.assertEqual(cap.palabras, 5)

    def test_ficha_normaliza_nombre_y_alias(self):
        ficha = Ficha.objects.create(proyecto=self.proyecto, nombre="Ána", alias=["La Capitana"])
        self.assertEqual(ficha.terminos, "ana|la capitana")
        self.assertTrue(ficha.coincide("la capitána"))
        self.assertFalse(ficha.coincide("Leo"))


class ConteoDePalabrasEntreBloquesTests(TestCase):
    def test_los_bloques_pegados_no_unen_palabras(self):
        ana = User.objects.create_user("ana2", password="clave-segura-123")
        p = Proyecto.objects.create(dueno=ana, titulo="La torre")
        cap = Capitulo.objects.create(proyecto=p, titulo="Uno", contenido="<h2>Capítulo uno</h2><p>Había una torre</p><p>y un faro</p><hr><p>Fin</p>")
        self.assertEqual(cap.palabras, 9)
