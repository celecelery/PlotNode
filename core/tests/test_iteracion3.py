import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Capitulo, EventoTrama, Ficha, Nota, Perfil, Proyecto, Relacion
from core.services.fichas import ficha_a_dict

User = get_user_model()


class Base(TestCase):
    def setUp(self):
        self.ana_u = User.objects.create_user("celeste", password="x-clave-segura-1")
        self.otra = User.objects.create_user("intrusa", password="x-clave-segura-1")
        self.p = Proyecto.objects.create(dueno=self.ana_u, titulo="La torre")
        self.cap = Capitulo.objects.create(proyecto=self.p, titulo="Cap 1", orden=1)
        self.ana = Ficha.objects.create(proyecto=self.p, nombre="Ana")
        self.lia = Ficha.objects.create(proyecto=self.p, nombre="Lía")
        self.client.force_login(self.ana_u)

    def post_json(self, nombre, args, datos):
        return self.client.post(reverse(nombre, args=args), data=json.dumps(datos), content_type="application/json")


class RelacionesTests(Base):
    def crear(self, **extra):
        datos = {"origen": self.ana.pk, "destino": self.lia.pk, "categoria": "familia", "etiqueta": "Hermanas", "nota": ""}
        datos.update(extra)
        return self.client.post(reverse("relaciones", args=[self.p.pk]), datos)

    def test_crear_relacion_y_verla_desde_ambas_fichas(self):
        self.assertRedirects(self.crear(), reverse("relaciones", args=[self.p.pk]))
        self.assertEqual(Relacion.objects.get().texto, "Hermanas")
        a = ficha_a_dict(Ficha.objects.get(pk=self.ana.pk))["relaciones"]
        b = ficha_a_dict(Ficha.objects.get(pk=self.lia.pk))["relaciones"]
        self.assertEqual((a[0]["con"], b[0]["con"]), ("Lía", "Ana"))

    def test_no_permite_relacion_consigo_misma_ni_repetida(self):
        r = self.crear(destino=self.ana.pk)
        self.assertContains(r, "consigo misma")
        self.crear()
        r = self.crear(origen=self.lia.pk, destino=self.ana.pk)       # invertida = misma relación
        self.assertContains(r, "ya tienen una relación de ese tipo")
        self.assertEqual(Relacion.objects.count(), 1)

    def test_etiqueta_vacia_usa_la_categoria(self):
        self.crear(etiqueta="", categoria="enemistad")
        self.assertEqual(Relacion.objects.get().texto, "Enemistad")

    def test_no_acepta_fichas_de_otro_proyecto(self):
        q = Proyecto.objects.create(dueno=self.ana_u, titulo="Otra")
        ajena = Ficha.objects.create(proyecto=q, nombre="Ajena")
        self.crear(destino=ajena.pk)
        self.assertEqual(Relacion.objects.count(), 0)

    def test_editar_eliminar_y_filtro(self):
        self.crear()
        r = Relacion.objects.get()
        url = reverse("relacion_editar", args=[self.p.pk, r.pk])
        self.client.post(url, {"origen": self.ana.pk, "destino": self.lia.pk, "categoria": "romance", "etiqueta": "", "nota": "x"})
        r.refresh_from_db()
        self.assertEqual(r.categoria, "romance")
        self.assertNotContains(self.client.get(reverse("relaciones", args=[self.p.pk]) + "?categoria=familia"), "mapa-svg")
        self.assertContains(self.client.get(reverse("relaciones", args=[self.p.pk]) + "?categoria=romance"), "mapa-svg")
        self.client.post(reverse("relacion_eliminar", args=[self.p.pk, r.pk]))
        self.assertEqual(Relacion.objects.count(), 0)

    def test_se_borra_con_la_ficha(self):
        self.crear()
        self.lia.delete()
        self.assertEqual(Relacion.objects.count(), 0)

    def test_aparece_en_el_json_del_panel(self):
        self.crear()
        r = self.client.get(reverse("ficha_consulta", args=[self.p.pk]), {"nombre": "Ana"})
        self.assertEqual(r.json()["ficha"]["relaciones"][0]["texto"], "Hermanas")

    def test_privacidad(self):
        self.client.force_login(self.otra)
        for nombre in ("relaciones", "linea_tiempo", "tablon"):
            self.assertEqual(self.client.get(reverse(nombre, args=[self.p.pk])).status_code, 404)
        self.crear()
        self.client.force_login(self.ana_u)
        self.crear()
        r = Relacion.objects.get()
        self.client.force_login(self.otra)
        self.assertEqual(self.client.post(reverse("relacion_eliminar", args=[self.p.pk, r.pk])).status_code, 404)


class LineaTiempoTests(Base):
    def crear(self, titulo="Cruzan el puente", etapa="Día 2", participantes=(), capitulo=""):
        return self.client.post(reverse("linea_tiempo", args=[self.p.pk]),
                                {"titulo": titulo, "etapa": etapa, "descripcion": "", "capitulo": capitulo,
                                 "participantes": list(participantes)})

    def test_crear_evento_con_varios_participantes_y_capitulo(self):
        self.crear(participantes=[self.ana.pk, self.lia.pk], capitulo=self.cap.pk)
        e = EventoTrama.objects.get()
        self.assertEqual((e.participantes.count(), e.capitulo), (2, self.cap))
        r = self.client.get(reverse("linea_tiempo", args=[self.p.pk]))
        self.assertContains(r, reverse("ficha_editar", args=[self.p.pk, self.ana.pk]))     # abre la ficha desde el evento
        self.assertContains(r, self.cap.get_absolute_url())                                # y el capítulo

    def test_los_eventos_nuevos_van_al_final_y_la_etapa_es_texto_libre(self):
        self.crear("A", "Año 3")
        self.crear("B", "Hace una semana")
        self.crear("C", "Año 3")
        self.assertEqual([e.orden for e in EventoTrama.objects.order_by("pk")], [1, 2, 3])
        html = self.client.get(reverse("linea_tiempo", args=[self.p.pk])).content.decode()
        self.assertLess(html.index(">A<"), html.index(">B<"))
        self.assertLess(html.index(">B<"), html.index(">C<"))

    def test_subir_y_bajar_cambia_el_orden(self):
        for t in "ABC":
            self.crear(t, "Día 1")
        a, b, c = (EventoTrama.objects.get(titulo=t) for t in "ABC")
        self.client.post(reverse("evento_mover", args=[self.p.pk, c.pk]), {"direccion": "arriba"})
        self.assertEqual([e.titulo for e in EventoTrama.objects.order_by("orden")], ["A", "C", "B"])
        self.client.post(reverse("evento_mover", args=[self.p.pk, a.pk]), {"direccion": "arriba"})   # ya es el primero
        self.assertEqual([e.titulo for e in EventoTrama.objects.order_by("orden")], ["A", "C", "B"])
        self.client.post(reverse("evento_mover", args=[self.p.pk, a.pk]), {"direccion": "abajo"})
        self.assertEqual([e.titulo for e in EventoTrama.objects.order_by("orden")], ["C", "A", "B"])

    def test_mover_exige_post_y_ser_la_duena(self):
        self.crear()
        e = EventoTrama.objects.get()
        url = reverse("evento_mover", args=[self.p.pk, e.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.force_login(self.otra)
        self.assertEqual(self.client.post(url, {"direccion": "abajo"}).status_code, 404)

    def test_filtrar_por_personaje(self):
        self.crear("De Ana", participantes=[self.ana.pk])
        self.crear("De Lía", participantes=[self.lia.pk])
        r = self.client.get(reverse("linea_tiempo", args=[self.p.pk]) + f"?personaje={self.ana.pk}")
        self.assertEqual([e.titulo for e in r.context["eventos"]], ["De Ana"])

    def test_validacion_editar_y_eliminar(self):
        self.assertContains(self.crear(titulo="  ", etapa="Día 1"), "obligatorio")
        self.assertContains(self.crear(titulo="X", etapa=" "), "obligatorio")
        self.crear()
        e = EventoTrama.objects.get()
        self.client.post(reverse("evento_editar", args=[self.p.pk, e.pk]), {"titulo": "Nuevo", "etapa": "Día 3", "descripcion": ""})
        e.refresh_from_db()
        self.assertEqual((e.titulo, e.etapa, e.orden), ("Nuevo", "Día 3", 1))
        self.client.post(reverse("evento_eliminar", args=[self.p.pk, e.pk]))
        self.assertEqual(EventoTrama.objects.count(), 0)

    def test_capitulo_borrado_no_borra_el_evento(self):
        self.crear(capitulo=self.cap.pk)
        self.cap.delete()
        self.assertEqual(EventoTrama.objects.get().capitulo, None)


class TablonTests(Base):
    def test_crear_idea_y_posiciones_distintas(self):
        for t in ("uno", "dos"):
            self.client.post(reverse("tablon", args=[self.p.pk]), {"contenido": t, "ficha": ""})
        a, b = Nota.objects.all()
        self.assertEqual(a.tipo, "idea")
        self.assertNotEqual((a.x, a.y), (b.x, b.y))

    def test_contenido_vacio_se_rechaza(self):
        r = self.client.post(reverse("tablon", args=[self.p.pk]), {"contenido": "   ", "ficha": ""})
        self.assertContains(r, "obligatorio")
        self.assertEqual(Nota.objects.count(), 0)

    def test_enviar_pasaje_desde_el_editor(self):
        r = self.post_json("nota_desde_texto", [self.p.pk], {"texto": "  Había   una luz\nen la torre ", "capitulo": self.cap.pk})
        self.assertEqual(r.status_code, 200)
        n = Nota.objects.get()
        self.assertEqual((n.tipo, n.contenido, n.capitulo), ("texto", "Había una luz en la torre", self.cap))

    def test_pasaje_que_es_un_nombre_se_vincula_a_la_ficha(self):
        self.post_json("nota_desde_texto", [self.p.pk], {"texto": "Ana", "capitulo": self.cap.pk})
        self.assertEqual(Nota.objects.get().ficha, self.ana)

    def test_pasaje_vacio_y_capitulo_ajeno(self):
        self.assertEqual(self.post_json("nota_desde_texto", [self.p.pk], {"texto": "  "}).status_code, 400)
        otro = Capitulo.objects.create(proyecto=Proyecto.objects.create(dueno=self.otra, titulo="Z"), titulo="Z")
        self.post_json("nota_desde_texto", [self.p.pk], {"texto": "hola", "capitulo": otro.pk})
        self.assertIsNone(Nota.objects.get().capitulo)

    def test_mover_nota_y_validar(self):
        n = Nota.objects.create(proyecto=self.p, contenido="x")
        self.assertEqual(self.post_json("nota_mover", [self.p.pk, n.pk], {"x": 400, "y": 90}).status_code, 200)
        n.refresh_from_db()
        self.assertEqual((n.x, n.y), (400, 90))
        self.assertEqual(self.post_json("nota_mover", [self.p.pk, n.pk], {"x": "a", "y": 1}).status_code, 400)
        self.post_json("nota_mover", [self.p.pk, n.pk], {"x": -50, "y": 99999})
        n.refresh_from_db()
        self.assertEqual((n.x, n.y), (0, 5000))

    def test_otra_persona_no_puede_mover_ni_enviar(self):
        n = Nota.objects.create(proyecto=self.p, contenido="x")
        self.client.force_login(self.otra)
        self.assertEqual(self.post_json("nota_mover", [self.p.pk, n.pk], {"x": 1, "y": 1}).status_code, 404)
        self.assertEqual(self.post_json("nota_desde_texto", [self.p.pk], {"texto": "hola"}).status_code, 404)

    def test_filtros_busqueda_editar_y_eliminar(self):
        Nota.objects.create(proyecto=self.p, contenido="Una idea suelta", tipo="idea")
        n = Nota.objects.create(proyecto=self.p, contenido="Pasaje del capítulo", tipo="texto")
        url = reverse("tablon", args=[self.p.pk])
        self.assertContains(self.client.get(url + "?tipo=texto"), "Pasaje del capítulo")
        self.assertNotContains(self.client.get(url + "?tipo=texto"), "Una idea suelta")
        self.assertContains(self.client.get(url + "?q=SUELTA"), "Una idea suelta")
        self.client.post(reverse("nota_editar", args=[self.p.pk, n.pk]), {"contenido": "Cambiada", "ficha": ""})
        n.refresh_from_db()
        self.assertEqual(n.contenido, "Cambiada")
        self.client.post(reverse("nota_eliminar", args=[self.p.pk, n.pk]))
        self.assertEqual(Nota.objects.count(), 1)


class TutorialTests(Base):
    def test_registro_crea_proyecto_de_muestra_y_abre_el_tutorial(self):
        self.client.logout()
        r = self.client.post(reverse("registro"), {"username": "nueva", "email": "n@ejemplo.com",
                                                   "password1": "una-clave-larga-42", "password2": "una-clave-larga-42", "privacidad": "on"})
        u = User.objects.get(username="nueva")
        proyecto = u.proyectos.get()
        self.assertTrue(proyecto.es_plantilla)
        self.assertEqual(proyecto.fichas.count(), 2)
        self.assertEqual(proyecto.relaciones.count(), 1)
        cap = proyecto.capitulos.get()
        self.assertRedirects(r, reverse("editor", args=[cap.pk]))
        self.assertContains(self.client.get(reverse("editor", args=[cap.pk])), "data-tutorial=")

    def test_terminar_tutorial_lo_oculta_y_se_puede_repetir(self):
        url = reverse("editor", args=[self.cap.pk])
        self.assertContains(self.client.get(url), "data-tutorial=")
        self.assertEqual(self.client.post(reverse("tutorial_terminar")).status_code, 200)
        self.assertTrue(Perfil.objects.get(user=self.ana_u).onboarding_completado)
        self.assertNotContains(self.client.get(url), "data-tutorial=")
        self.assertContains(self.client.get(url + "?tutorial=1"), "data-tutorial=")

    def test_terminar_exige_sesion_y_post(self):
        self.assertEqual(self.client.get(reverse("tutorial_terminar")).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post(reverse("tutorial_terminar")).status_code, 302)

    def test_herramientas_en_el_menu_lateral(self):
        r = self.client.get(reverse("fichas_lista", args=[self.p.pk]))
        for nombre in ("relaciones", "linea_tiempo", "tablon"):
            self.assertContains(r, reverse(nombre, args=[self.p.pk]))
        self.assertContains(self.client.get(reverse("editor", args=[self.cap.pk])), "Guardar como nota")


class CierreDeBrechasTests(Base):
    """Historias del backlog que faltaban: HU-14, HU-16, HU-11, HU-22, HU-32 y tipos de HU-33."""

    DATOS = {"username": "nueva2", "email": "n2@ejemplo.com",
             "password1": "una-clave-larga-42", "password2": "una-clave-larga-42"}

    def test_registro_exige_aceptar_la_privacidad_y_guarda_la_fecha(self):
        self.client.logout()
        r = self.client.post(reverse("registro"), self.DATOS)
        self.assertContains(r, "acepta el aviso de privacidad")
        self.assertFalse(User.objects.filter(username="nueva2").exists())
        self.client.post(reverse("registro"), {**self.DATOS, "privacidad": "on"})
        self.assertIsNotNone(Perfil.objects.get(user__username="nueva2").acepto_privacidad)

    def test_el_aviso_de_privacidad_se_muestra_en_el_registro(self):
        self.client.logout()
        r = self.client.get(reverse("registro"))
        self.assertContains(r, "no se envía a servicios de terceros")

    def test_el_proyecto_de_muestra_trae_glosario_y_una_nota(self):
        self.client.logout()
        self.client.post(reverse("registro"), {**self.DATOS, "privacidad": "on"})
        p = User.objects.get(username="nueva2").proyectos.get()
        self.assertEqual(p.terminos.count(), 1)
        self.assertEqual(p.notas.count(), 1)

    def test_tipos_de_relacion_del_backlog(self):
        for tipo in ("familia", "amistad", "alianza", "romance", "enemistad"):
            self.assertIn(tipo, Relacion.Categoria.values)

    def test_filtrar_relaciones_por_personaje(self):
        zoe = Ficha.objects.create(proyecto=self.p, nombre="Zoe")
        Relacion.objects.create(proyecto=self.p, origen=self.ana, destino=self.lia, categoria="amistad")
        Relacion.objects.create(proyecto=self.p, origen=self.lia, destino=zoe, categoria="alianza")
        r = self.client.get(reverse("relaciones", args=[self.p.pk]) + f"?personaje={self.ana.pk}")
        self.assertEqual(len(r.context["relaciones"]), 1)
        self.assertEqual(r.context["mapa"]["aristas"][0]["categoria"], "amistad")

    def test_notas_con_color_y_filtro_por_color_y_capitulo(self):
        self.client.post(reverse("tablon", args=[self.p.pk]),
                         {"contenido": "verde", "ficha": "", "capitulo": self.cap.pk, "color": "menta"})
        Nota.objects.create(proyecto=self.p, contenido="lila", color="lila")
        n = Nota.objects.get(contenido="verde")
        self.assertEqual((n.color, n.capitulo), ("menta", self.cap))
        url = reverse("tablon", args=[self.p.pk])
        self.assertEqual(len(self.client.get(url + "?color=menta").context["notas"]), 1)
        self.assertEqual(len(self.client.get(url + f"?capitulo={self.cap.pk}").context["notas"]), 1)
        self.assertEqual(len(self.client.get(url + "?color=nada").context["notas"]), 2)

    def test_nota_en_blanco_desde_el_panel_y_lista_en_el_editor(self):
        r = self.post_json("nota_desde_texto", [self.p.pk], {"texto": "Idea suelta", "capitulo": self.cap.pk, "tipo": "idea"})
        self.assertEqual(r.json()["nota"]["tipo"], "idea")
        self.assertEqual(Nota.objects.get().tipo, "idea")
        html = self.client.get(reverse("editor", args=[self.cap.pk])).content.decode()
        self.assertIn('id="tab-notas"', html)
        self.assertIn("Idea suelta", html)
        self.assertIn("Guardar como nota", html)

    def test_el_editor_ofrece_la_lista_de_personajes_del_capitulo(self):
        html = self.client.get(reverse("editor", args=[self.cap.pk])).content.decode()
        self.assertIn('id="presentes-lista"', html)


class TablonGeneralTests(Base):
    def test_reune_las_notas_de_todas_las_historias_y_filtra(self):
        q = Proyecto.objects.create(dueno=self.ana_u, titulo="Otra historia")
        Nota.objects.create(proyecto=self.p, contenido="de la torre", color="lila")
        Nota.objects.create(proyecto=q, contenido="de la otra", color="menta")
        ajena = Proyecto.objects.create(dueno=self.otra, titulo="Ajena")
        Nota.objects.create(proyecto=ajena, contenido="secreta")
        url = reverse("tablon_general")
        self.assertEqual(sorted(n.contenido for n in self.client.get(url).context["notas"]), ["de la otra", "de la torre"])
        self.assertEqual([n.contenido for n in self.client.get(url + f"?proyecto={q.pk}").context["notas"]], ["de la otra"])
        self.assertEqual([n.contenido for n in self.client.get(url + "?color=lila").context["notas"]], ["de la torre"])
        self.assertContains(self.client.get(url + "?q=OTRA"), "de la otra")

    def test_exige_sesion_y_aparece_en_el_menu(self):
        self.assertContains(self.client.get(reverse("proyectos")), reverse("tablon_general"))
        self.client.logout()
        self.assertEqual(self.client.get(reverse("tablon_general")).status_code, 302)


class BuscarYReemplazarTests(Base):
    def test_el_editor_trae_el_dialogo_y_su_script(self):
        html = self.client.get(reverse("editor", args=[self.cap.pk])).content.decode()
        for fragmento in ('id="dlg-buscar"', 'id="bus-todo"', "core/js/buscar.js", "Buscar y reemplazar"):
            self.assertIn(fragmento, html)
