import io
import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from core.fichas_schema import SECCIONES, campos_de, secciones_con_datos
from core.models import Atributo, Capitulo, Ficha, Proyecto
from core.services.fichas import ficha_a_dict

User = get_user_model()
MEDIA = tempfile.mkdtemp(prefix="plotnode-media-")
FETCH = {"HTTP_X_REQUESTED_WITH": "fetch"}
FORMSET = {"atributos-TOTAL_FORMS": "2", "atributos-INITIAL_FORMS": "0", "atributos-MIN_NUM_FORMS": "0",
           "atributos-MAX_NUM_FORMS": "1000", "atributos-0-clave": "", "atributos-0-valor": "",
           "atributos-1-clave": "", "atributos-1-valor": ""}


def imagen(formato="JPEG", nombre="foto.jpg", tipo="image/jpeg", tamano=(40, 40)):
    buffer = io.BytesIO()
    Image.new("RGB", tamano, (120, 80, 200)).save(buffer, formato)
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type=tipo)


def datos(nombre, **campos):
    d = {"nombre": nombre, "alias_texto": "", "notas": "", **FORMSET}
    d.update({f"d_{k}": v for k, v in campos.items()})
    return d


def tearDownModule():
    shutil.rmtree(MEDIA, ignore_errors=True)


@override_settings(MEDIA_ROOT=MEDIA)
class FichaCompletaTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="x-clave-segura-1")
        self.beto = User.objects.create_user("beto", password="x-clave-segura-2")
        self.p = Proyecto.objects.create(dueno=self.ana, titulo="La torre")
        self.cap = Capitulo.objects.create(proyecto=self.p, titulo="Uno")
        self.client.force_login(self.ana)
        self.url_nueva = reverse("ficha_nueva", args=[self.p.pk])

    # --- campos por tipo ---
    def test_el_esquema_cubre_los_cuatro_tipos_y_el_personaje_tiene_unos_30_campos(self):
        self.assertEqual(set(SECCIONES), {"personaje", "lugar", "objeto", "evento"})
        self.assertGreaterEqual(len(campos_de("personaje")), 28)
        claves = [c["clave"] for c in campos_de("personaje")]
        self.assertEqual(len(claves), len(set(claves)))

    def test_el_formulario_de_personaje_tiene_tres_secciones_plegables(self):
        r = self.client.get(self.url_nueva)
        for titulo in ("Esenciales", "Historia", "Más detalles", "Otros atributos"):
            self.assertContains(r, titulo)
        self.assertContains(r, 'id="id_d_motivacion"')
        self.assertContains(r, "<details", count=4)

    def test_guarda_los_datos_del_personaje_y_omite_los_vacios(self):
        r = self.client.post(self.url_nueva, datos("Ana", edad="17", rol="Protagonista / Principal",
                                                    motivacion="Salvar la torre", secreto="", especie="  elfa "))
        self.assertEqual(r.status_code, 302)
        f = Ficha.objects.get(nombre="Ana")
        self.assertEqual(f.tipo, "personaje")
        self.assertEqual(f.datos, {"edad": "17", "rol": "Protagonista / Principal", "motivacion": "Salvar la torre", "especie": "elfa"})

    def test_las_listas_desplegables_solo_aceptan_sus_opciones(self):
        r = self.client.post(self.url_nueva, datos("Ana", rol="Rey del universo"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Ficha.objects.exists())

    def test_ficha_de_lugar_objeto_y_evento_con_sus_campos(self):
        casos = {"lugar": ("Torre Norte", {"tipo_lugar": "Torre", "habitantes": "Magos"}),
                 "objeto": ("Orbe de Ilvar", {"duenio": "Ana", "poderes": "Muestra el pasado"}),
                 "evento": ("La boda", {"momento": "Año 3", "consecuencias": "Guerra"})}
        for tipo, (nombre, campos) in casos.items():
            url = f"{self.url_nueva}?tipo={tipo}"
            pagina = self.client.get(url)
            self.assertNotContains(pagina, "id_d_motivacion")   # campos de personaje: no aparecen
            r = self.client.post(url, datos(nombre, **campos))
            self.assertEqual(r.status_code, 302, tipo)
            f = Ficha.objects.get(nombre=nombre)
            self.assertEqual((f.tipo, f.datos), (tipo, campos))

    def test_tipo_desconocido_se_trata_como_personaje(self):
        self.assertContains(self.client.get(f"{self.url_nueva}?tipo=dragon"), "id_d_motivacion")

    def test_el_tipo_no_cambia_al_editar(self):
        lugar = Ficha.objects.create(proyecto=self.p, nombre="Torre", tipo="lugar")
        url = reverse("ficha_editar", args=[self.p.pk, lugar.pk])
        self.client.post(url + "?tipo=personaje", datos("Torre", tipo_lugar="Torre alta"))
        lugar.refresh_from_db()
        self.assertEqual((lugar.tipo, lugar.datos), ("lugar", {"tipo_lugar": "Torre alta"}))

    def test_editar_precarga_los_datos_y_los_atributos(self):
        f = Ficha.objects.create(proyecto=self.p, nombre="Ana", datos={"edad": "17", "secreto": "Es la heredera"})
        Atributo.objects.create(ficha=f, clave="Color favorito", valor="verde")
        r = self.client.get(reverse("ficha_editar", args=[self.p.pk, f.pk]))
        self.assertContains(r, 'value="17"')
        self.assertContains(r, "Es la heredera")
        self.assertContains(r, "Color favorito")

    def test_el_nombre_del_formulario_nuevo_se_puede_precargar(self):
        self.assertContains(self.client.get(f"{self.url_nueva}?nombre=Tomás"), 'value="Tomás"')

    def test_limite_de_largo_de_los_campos(self):
        r = self.client.post(self.url_nueva, datos("Ana", edad="x" * 201))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Ficha.objects.exists())

    # --- foto o avatar ---
    def test_sin_foto_hay_avatar_con_inicial_y_color(self):
        f = Ficha.objects.create(proyecto=self.p, nombre="Ana")
        d = ficha_a_dict(f)
        self.assertEqual((d["foto"], d["inicial"]), ("", "A"))
        self.assertIn(d["color"], {"lila", "menta", "durazno"})

    def test_sube_una_foto_con_nombre_aleatorio_dentro_de_fichas(self):
        r = self.client.post(self.url_nueva, {**datos("Ana"), "foto": imagen(nombre="mi foto privada.jpg")})
        self.assertEqual(r.status_code, 302)
        f = Ficha.objects.get(nombre="Ana")
        self.assertTrue(f.foto.name.startswith("fichas/"))
        self.assertNotIn("privada", f.foto.name)
        self.assertTrue(ficha_a_dict(f)["foto"].endswith(f.foto.name))

    def test_acepta_png_y_webp(self):
        for formato, nombre, tipo in (("PNG", "a.png", "image/png"), ("WEBP", "a.webp", "image/webp")):
            r = self.client.post(self.url_nueva, {**datos(f"Pj {formato}"), "foto": imagen(formato, nombre, tipo)})
            self.assertEqual(r.status_code, 302, formato)

    def test_rechaza_archivos_que_no_son_imagen(self):
        falso = SimpleUploadedFile("a.png", b"esto no es una imagen", content_type="image/png")
        r = self.client.post(self.url_nueva, {**datos("Ana"), "foto": falso})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "no es una imagen válida")
        self.assertFalse(Ficha.objects.exists())

    def test_rechaza_formatos_distintos_de_jpg_png_webp(self):
        r = self.client.post(self.url_nueva, {**datos("Ana"), "foto": imagen("GIF", "a.gif", "image/gif")})
        self.assertContains(r, "Solo se aceptan imágenes JPG, PNG o WebP")
        self.assertFalse(Ficha.objects.exists())

    @override_settings(MAX_FOTO_BYTES=500)
    def test_rechaza_fotos_de_mas_de_2_mb(self):
        r = self.client.post(self.url_nueva, {**datos("Ana"), "foto": imagen(tamano=(300, 300))})
        self.assertContains(r, "pesa más de 2 MB")
        self.assertFalse(Ficha.objects.exists())

    def test_cambiar_o_quitar_la_foto_borra_el_archivo_anterior(self):
        self.client.post(self.url_nueva, {**datos("Ana"), "foto": imagen()})
        f = Ficha.objects.get(nombre="Ana")
        primera = f.foto.name
        url = reverse("ficha_editar", args=[self.p.pk, f.pk])
        self.client.post(url, {**datos("Ana"), "foto": imagen()})
        f.refresh_from_db()
        self.assertNotEqual(f.foto.name, primera)
        self.assertFalse(f.foto.storage.exists(primera))
        segunda = f.foto.name
        self.client.post(url, {**datos("Ana"), "quitar_foto": "on"})
        f.refresh_from_db()
        self.assertFalse(f.foto)
        self.assertFalse(Ficha.objects.get(pk=f.pk).foto.storage.exists(segunda))

    def test_editar_sin_tocar_la_foto_la_conserva(self):
        self.client.post(self.url_nueva, {**datos("Ana"), "foto": imagen()})
        f = Ficha.objects.get(nombre="Ana")
        nombre_foto = f.foto.name
        self.client.post(reverse("ficha_editar", args=[self.p.pk, f.pk]), datos("Ana", edad="18"))
        f.refresh_from_db()
        self.assertEqual(f.foto.name, nombre_foto)

    def test_eliminar_la_ficha_borra_su_foto(self):
        self.client.post(self.url_nueva, {**datos("Ana"), "foto": imagen()})
        f = Ficha.objects.get(nombre="Ana")
        ruta = f.foto.name
        self.client.post(reverse("ficha_eliminar", args=[self.p.pk, f.pk]))
        self.assertFalse(f.foto.storage.exists(ruta))

    # --- panel: fragmento y JSON ---
    def test_el_panel_recibe_el_formulario_como_fragmento_sin_la_pagina(self):
        r = self.client.get(self.url_nueva, **FETCH)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "<html")
        self.assertContains(r, "data-form-ficha")
        self.assertContains(r, 'enctype="multipart/form-data"')
        self.assertContains(r, "data-cancelar")
        self.assertContains(r, "Nuevo personaje")

    def test_guardar_desde_el_panel_responde_json_con_la_ficha(self):
        r = self.client.post(self.url_nueva, datos("Ana", edad="17"), **FETCH)
        self.assertEqual(r.status_code, 200)
        cuerpo = r.json()
        self.assertTrue(cuerpo["ok"])
        self.assertEqual(cuerpo["ficha"]["nombre"], "Ana")
        self.assertEqual(cuerpo["ficha"]["secciones"][0]["campos"], [{"etiqueta": "Edad", "valor": "17"}])

    def test_errores_desde_el_panel_devuelven_el_formulario_con_estado_422(self):
        r = self.client.post(self.url_nueva, datos(""), **FETCH)
        self.assertEqual(r.status_code, 422)
        self.assertContains(r, "required", status_code=422, html=False)
        self.assertContains(r, "data-form-ficha", status_code=422)

    def test_nombre_repetido_desde_el_panel_se_rechaza(self):
        Ficha.objects.create(proyecto=self.p, nombre="Ana")
        r = self.client.post(self.url_nueva, datos("ána"), **FETCH)
        self.assertEqual(r.status_code, 422)
        self.assertContains(r, "ya está en la ficha de Ana", status_code=422)

    def test_eliminar_desde_el_panel_responde_json(self):
        f = Ficha.objects.create(proyecto=self.p, nombre="Ana")
        r = self.client.post(reverse("ficha_eliminar", args=[self.p.pk, f.pk]), **FETCH)
        self.assertEqual(r.json(), {"ok": True})
        self.assertFalse(Ficha.objects.exists())

    def test_otra_cuenta_no_abre_ni_guarda_fichas_ajenas_en_el_panel(self):
        f = Ficha.objects.create(proyecto=self.p, nombre="Ana")
        self.client.force_login(self.beto)
        self.assertEqual(self.client.get(self.url_nueva, **FETCH).status_code, 404)
        self.assertEqual(self.client.get(reverse("ficha_editar", args=[self.p.pk, f.pk]), **FETCH).status_code, 404)
        self.assertEqual(self.client.post(self.url_nueva, datos("Intruso"), **FETCH).status_code, 404)
        self.assertEqual(self.client.post(reverse("ficha_eliminar", args=[self.p.pk, f.pk]), **FETCH).status_code, 404)
        self.assertEqual(Ficha.objects.count(), 1)

    def test_la_consulta_trae_secciones_con_datos_y_foto(self):
        f = Ficha.objects.create(proyecto=self.p, nombre="Ana", datos={"edad": "17", "secreto": "Heredera"})
        d = self.client.get(reverse("ficha_consulta", args=[self.p.pk]), {"nombre": "ana"}).json()["ficha"]
        self.assertEqual([s["titulo"] for s in d["secciones"]], ["Esenciales", "Más detalles"])
        self.assertEqual(d["tipo_clave"], "personaje")
        self.assertEqual(d["foto"], "")

    def test_secciones_con_datos_ignora_campos_vacios(self):
        self.assertEqual(secciones_con_datos("personaje", {"edad": "", "rol": "Aliado"}),
                         [{"titulo": "Esenciales", "abierta": True, "campos": [{"etiqueta": "Rol", "valor": "Aliado"}]}])
        self.assertEqual(secciones_con_datos("personaje", {}), [])

    # --- lista y filtro por tipo ---
    def test_la_lista_filtra_por_tipo(self):
        Ficha.objects.create(proyecto=self.p, nombre="Ana")
        Ficha.objects.create(proyecto=self.p, nombre="Torre Norte", tipo="lugar")
        url = reverse("fichas_lista", args=[self.p.pk])
        r = self.client.get(url, {"tipo": "lugar"})
        self.assertContains(r, "Torre Norte")
        self.assertNotContains(r, "<h2><span class=\"nombre nombre-lila\">Ana")
        self.assertContains(self.client.get(url), "Ana")

    def test_el_editor_trae_el_tipo_de_cada_ficha_para_filtrar_en_el_panel(self):
        Ficha.objects.create(proyecto=self.p, nombre="Torre Norte", tipo="lugar")
        r = self.client.get(reverse("editor", args=[self.cap.pk]))
        self.assertContains(r, "tipo_clave")
        self.assertContains(r, 'id="filtro-tipo"')
        for tipo in ("personaje", "lugar", "objeto", "evento"):
            self.assertContains(r, f'data-nueva="{tipo}"')
