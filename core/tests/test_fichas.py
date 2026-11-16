import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Atributo, Capitulo, EventoUso, Ficha, Proyecto

User = get_user_model()

FORMSET_VACIO = {
    "atributos-TOTAL_FORMS": "3", "atributos-INITIAL_FORMS": "0",
    "atributos-MIN_NUM_FORMS": "0", "atributos-MAX_NUM_FORMS": "1000",
}


def datos_ficha(nombre, alias="", atributos=(), **extra):
    d = {"nombre": nombre, "tipo": "personaje", "alias_texto": alias, "notas": "", **FORMSET_VACIO, **extra}
    for i in range(3):
        clave, valor = atributos[i] if i < len(atributos) else ("", "")
        d[f"atributos-{i}-clave"], d[f"atributos-{i}-valor"] = clave, valor
    return d


class Base(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.beto = User.objects.create_user("beto", password="x-clave-segura-2")
        self.proyecto = Proyecto.objects.create(dueno=self.ana, titulo="La torre")
        self.cap = Capitulo.objects.create(proyecto=self.proyecto, titulo="Uno")
        self.ficha = Ficha.objects.create(proyecto=self.proyecto, nombre="Ana", alias=["la capitana"])
        Atributo.objects.create(ficha=self.ficha, clave="Ojos", valor="verdes")
        self.client.force_login(self.ana)

    def consulta(self, nombre, **extra):
        return self.client.get(reverse("ficha_consulta", args=[self.proyecto.pk]), {"nombre": nombre, **extra})


class FichasCrudTests(Base):
    def test_crear_con_alias_y_atributos(self):
        r = self.client.post(reverse("ficha_nueva", args=[self.proyecto.pk]),
                             datos_ficha("Lía", "Lili, la hermana\nLi", [("Edad", "12"), ("Rol", "hermana")]))
        self.assertRedirects(r, reverse("fichas_lista", args=[self.proyecto.pk]))
        f = Ficha.objects.get(nombre="Lía")
        self.assertEqual(f.alias, ["Lili", "la hermana", "Li"])
        self.assertEqual(f.proyecto, self.proyecto)
        self.assertEqual({a.clave: a.valor for a in f.atributos.all()}, {"Edad": "12", "Rol": "hermana"})
        self.assertEqual(f.terminos, "lia|lili|la hermana|li")

    def test_editar_precarga_alias_y_atributos(self):
        r = self.client.get(reverse("ficha_editar", args=[self.proyecto.pk, self.ficha.pk]))
        self.assertContains(r, "la capitana")
        self.assertContains(r, "verdes")

    def test_editar_actualiza_y_quita_atributo(self):
        attr = self.ficha.atributos.get()
        datos = {"nombre": "Ana", "tipo": "personaje", "alias_texto": "la capitana, Ani", "notas": "Lidera",
                 "atributos-TOTAL_FORMS": "4", "atributos-INITIAL_FORMS": "1",
                 "atributos-MIN_NUM_FORMS": "0", "atributos-MAX_NUM_FORMS": "1000",
                 "atributos-0-id": attr.pk, "atributos-0-ficha": self.ficha.pk,
                 "atributos-0-clave": "Ojos", "atributos-0-valor": "cafés", "atributos-0-DELETE": "",
                 "atributos-1-clave": "", "atributos-1-valor": "", "atributos-2-clave": "", "atributos-2-valor": "",
                 "atributos-3-clave": "", "atributos-3-valor": ""}
        self.client.post(reverse("ficha_editar", args=[self.proyecto.pk, self.ficha.pk]), datos)
        self.ficha.refresh_from_db()
        self.assertEqual(self.ficha.alias, ["la capitana", "Ani"])
        self.assertEqual(self.ficha.notas, "Lidera")
        self.assertEqual(self.ficha.atributos.get().valor, "cafés")
        datos["atributos-0-DELETE"] = "on"
        self.client.post(reverse("ficha_editar", args=[self.proyecto.pk, self.ficha.pk]), datos)
        self.assertEqual(self.ficha.atributos.count(), 0)

    def test_eliminar_con_confirmacion(self):
        url = reverse("ficha_eliminar", args=[self.proyecto.pk, self.ficha.pk])
        self.assertContains(self.client.get(url), "¿Eliminar la ficha de Ana?")
        self.assertTrue(Ficha.objects.filter(pk=self.ficha.pk).exists())
        self.client.post(url)
        self.assertFalse(Ficha.objects.filter(pk=self.ficha.pk).exists())
        self.assertEqual(Atributo.objects.count(), 0)

    def test_nombre_o_alias_repetido_se_rechaza(self):
        url = reverse("ficha_nueva", args=[self.proyecto.pk])
        r = self.client.post(url, datos_ficha("Leo", alias="LA CAPITÁNA"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "ya está en la ficha de Ana")
        self.assertFalse(Ficha.objects.filter(nombre="Leo").exists())
        r = self.client.post(url, datos_ficha("ána"))
        self.assertContains(r, "ya está en la ficha de Ana")

    def test_editar_la_misma_ficha_no_choca_consigo_misma(self):
        datos = datos_ficha("Ana", "la capitana")
        datos.update({"atributos-TOTAL_FORMS": "3", "atributos-INITIAL_FORMS": "0"})
        r = self.client.post(reverse("ficha_editar", args=[self.proyecto.pk, self.ficha.pk]), datos)
        self.assertEqual(r.status_code, 302)

    def test_limite_de_alias(self):
        r = self.client.post(reverse("ficha_nueva", args=[self.proyecto.pk]),
                             datos_ficha("Muchos", ", ".join(f"alias{i}" for i in range(9))))
        self.assertContains(r, "Máximo 8 alias")

    def test_atributo_a_medias_muestra_error(self):
        r = self.client.post(reverse("ficha_nueva", args=[self.proyecto.pk]), datos_ficha("Rex", atributos=[("Edad", "")]))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Ficha.objects.filter(nombre="Rex").exists())

    def test_lista_vacia_y_con_fichas(self):
        self.assertContains(self.client.get(reverse("fichas_lista", args=[self.proyecto.pk])), "la capitana")
        otro = Proyecto.objects.create(dueno=self.ana, titulo="Vacío")
        self.assertContains(self.client.get(reverse("fichas_lista", args=[otro.pk])), "Aún no hay fichas")

    def test_ficha_ajena_o_de_otro_proyecto_da_404(self):
        otro = Proyecto.objects.create(dueno=self.ana, titulo="Otro")
        self.assertEqual(self.client.get(reverse("ficha_editar", args=[otro.pk, self.ficha.pk])).status_code, 404)
        self.client.force_login(self.beto)
        for nombre, args in (("fichas_lista", [self.proyecto.pk]), ("ficha_nueva", [self.proyecto.pk]),
                             ("ficha_editar", [self.proyecto.pk, self.ficha.pk]),
                             ("ficha_eliminar", [self.proyecto.pk, self.ficha.pk])):
            self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 404, nombre)
        self.assertEqual(self.client.post(reverse("ficha_eliminar", args=[self.proyecto.pk, self.ficha.pk])).status_code, 404)
        self.assertTrue(Ficha.objects.filter(pk=self.ficha.pk).exists())


class PanelTests(Base):
    def test_el_editor_incluye_las_fichas_y_el_panel(self):
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        self.assertContains(r, 'id="fichas-inicial"')
        self.assertContains(r, "la capitana")
        self.assertContains(r, reverse("ficha_consulta", args=[self.proyecto.pk]))
        self.assertContains(r, 'id="reparto-buscar"')

    def test_json_de_fichas_escapa_html(self):
        Ficha.objects.create(proyecto=self.proyecto, nombre="</script><b>x")
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        self.assertNotContains(r, "</script><b>x")

    def test_consulta_reconoce_nombre_y_alias_sin_mayusculas_ni_acentos(self):
        for texto in ("Ana", "ANA", "ána", "La Capitána", "  la   capitana "):
            datos = self.consulta(texto).json()
            self.assertTrue(datos["encontrada"], texto)
            self.assertEqual(datos["ficha"]["nombre"], "Ana")
            self.assertEqual(datos["ficha"]["atributos"], [{"clave": "Ojos", "valor": "verdes"}])

    def test_consulta_devuelve_color_e_inicial(self):
        ficha = self.consulta("ana").json()["ficha"]
        self.assertIn(ficha["color"], {"lila", "menta", "durazno"})
        self.assertEqual(ficha["inicial"], "A")

    def test_consulta_se_registra_como_evento(self):
        self.consulta("Ana")
        eventos = EventoUso.objects.filter(usuario=self.ana, tipo=EventoUso.Tipo.CONSULTA_FICHA)
        self.assertEqual(eventos.count(), 1)
        self.assertEqual(eventos.first().proyecto, self.proyecto)

    def test_consultas_seguidas_no_inflan_la_metrica(self):
        from datetime import timedelta
        from django.utils import timezone
        self.consulta("Ana")
        self.consulta("Ana")          # clic repetido en el nombre subrayado: misma consulta
        eventos = EventoUso.objects.filter(usuario=self.ana, tipo=EventoUso.Tipo.CONSULTA_FICHA)
        self.assertEqual(eventos.count(), 1)
        eventos.update(fecha=timezone.now() - timedelta(seconds=30))
        self.consulta("Ana")
        self.assertEqual(eventos.count(), 2)

    def test_busqueda_tolera_comillas_signos_y_nombres_parciales(self):
        for texto in ("«Ana»", "Ana,", '"Ana."', "Ana Torres", "la señora Ana"):
            datos = self.consulta(texto).json()
            self.assertTrue(datos["encontrada"], texto)
            self.assertEqual(datos["ficha"]["nombre"], "Ana")

    def test_busqueda_parcial_ambigua_no_adivina(self):
        Ficha.objects.create(proyecto=self.proyecto, nombre="Beatriz", alias=["Ana"])
        self.assertFalse(self.consulta("Ana Torres").json()["encontrada"])

    def test_busqueda_parcial_prefiere_el_nombre_mas_largo(self):
        Ficha.objects.create(proyecto=self.proyecto, nombre="Ana Luisa")
        self.assertEqual(self.consulta("Ana Luisa Torres").json()["ficha"]["nombre"], "Ana Luisa")

    def test_abrir_desde_la_lista_no_cuenta_como_consulta(self):
        self.consulta("Ana", registrar="0")
        self.assertEqual(EventoUso.objects.count(), 0)

    def test_sin_ficha_ofrece_crearla_y_no_registra_evento(self):
        datos = self.consulta("Luis").json()
        self.assertEqual(datos, {"encontrada": False, "nombre": "Luis"})
        self.assertEqual(EventoUso.objects.count(), 0)

    def test_consulta_ignora_selecciones_vacias_o_enormes(self):
        self.assertFalse(self.consulta("").json()["encontrada"])
        self.assertFalse(self.consulta("Ana " * 100).json()["encontrada"])

    def test_consulta_responde_rapido_con_muchas_fichas(self):
        Ficha.objects.bulk_create([Ficha(proyecto=self.proyecto, nombre=f"Personaje {i}", terminos=f"personaje {i}") for i in range(200)])
        import time
        t = time.perf_counter()
        self.assertTrue(self.consulta("la capitana").json()["encontrada"])
        self.assertLess(time.perf_counter() - t, 1.0)

    def test_crear_ficha_rapida(self):
        url = reverse("ficha_rapida", args=[self.proyecto.pk])
        r = self.client.post(url, json.dumps({"nombre": "  Luis  "}), content_type="application/json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["ficha"]["nombre"], "Luis")
        self.assertTrue(Ficha.objects.filter(proyecto=self.proyecto, nombre="Luis", tipo="personaje").exists())
        self.assertTrue(self.consulta("luis").json()["encontrada"])

    def test_crear_ficha_rapida_valida_datos(self):
        url = reverse("ficha_rapida", args=[self.proyecto.pk])
        self.assertEqual(self.client.post(url, json.dumps({"nombre": " "}), content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, "no es json", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, json.dumps({"nombre": "la CAPITANA"}), content_type="application/json").status_code, 409)
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_otra_cuenta_no_consulta_ni_crea_en_proyectos_ajenos(self):
        self.client.force_login(self.beto)
        self.assertEqual(self.consulta("Ana").status_code, 404)
        r = self.client.post(reverse("ficha_rapida", args=[self.proyecto.pk]), json.dumps({"nombre": "X"}), content_type="application/json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(self.client.get(reverse("editor", args=[self.cap.pk])).status_code, 404)

    def test_requiere_sesion(self):
        self.client.logout()
        self.assertEqual(self.consulta("Ana").status_code, 302)


class ColorDeFichaTests(TestCase):
    def test_colores_ciclan_por_proyecto_y_no_cambian_al_borrar(self):
        ana = User.objects.create_user("colores", password="x-clave-segura-1")
        a = Proyecto.objects.create(dueno=ana, titulo="A")
        b = Proyecto.objects.create(dueno=ana, titulo="B")
        Ficha.objects.create(proyecto=b, nombre="Ruido")        # otra obra no debe correr los colores de A
        f1, f2, f3, f4 = (Ficha.objects.create(proyecto=a, nombre=n) for n in ("Uno", "Dos", "Tres", "Cuatro"))
        self.assertEqual([f.color for f in (f1, f2, f3, f4)], ["lila", "menta", "durazno", "lila"])
        f2.delete()
        f1.refresh_from_db(); f3.refresh_from_db()
        self.assertEqual((f1.color, f3.color), ("lila", "durazno"))
        self.assertNotEqual(f1.color, Ficha.objects.create(proyecto=a, nombre="Cinco").color)
