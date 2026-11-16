import json
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from google.genai import errors

from core.models import Atributo, Ficha, Proyecto
from core.services.auditor import AuditorError, auditar, fichas_para_auditor

User = get_user_model()

FICHAS = [{"nombre": "Ana", "alias": ["la capitana"], "atributos": [{"clave": "Ojos", "valor": "verdes"}], "notas": ""}]


def cliente_con(texto=None, error=None):
    cli = MagicMock()
    if error:
        cli.models.generate_content.side_effect = error
    else:
        cli.models.generate_content.return_value.text = texto
    return cli


class AuditorTests(TestCase):
    def test_devuelve_las_inconsistencias(self):
        cli = cliente_con(json.dumps({"inconsistencias": [
            {"personaje": "Ana", "dato_en_ficha": "Ojos: verdes", "fragmento": "sus ojos azules",
             "explicacion": "En su ficha los ojos son verdes."}]}))
        r = auditar("Ana miró con sus ojos azules.", FICHAS, cliente=cli)
        self.assertEqual(r[0]["dato_en_ficha"], "Ojos: verdes")

    def test_el_prompt_lleva_solo_texto_y_fichas_recibidas(self):
        cli = cliente_con(json.dumps({"inconsistencias": []}))
        self.assertEqual(auditar("Ana sonrió.", FICHAS, cliente=cli), [])
        prompt = cli.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("Ana (alias: la capitana). Ojos: verdes", prompt)
        self.assertIn("Ana sonrió.", prompt)

    @override_settings(MODELO_AUDITOR="gemini-test")
    def test_el_modelo_sale_de_los_ajustes(self):
        cli = cliente_con(json.dumps({"inconsistencias": []}))
        auditar("Ana sonrió.", FICHAS, cliente=cli)
        self.assertEqual(cli.models.generate_content.call_args.kwargs["model"], "gemini-test")

    def test_cuota_agotada_429_da_aviso_en_lugar_de_fallar(self):
        cli = cliente_con(error=errors.APIError(429, {"error": {"message": "quota"}}))
        with self.assertRaises(AuditorError) as ctx:
            auditar("texto", FICHAS, cliente=cli)
        self.assertEqual(ctx.exception.codigo, "cuota")
        self.assertIn("cuota", ctx.exception.mensaje)

    def test_otros_errores_de_la_api_y_timeouts(self):
        with self.assertRaises(AuditorError) as ctx:
            auditar("texto", FICHAS, cliente=cliente_con(error=errors.APIError(500, {"error": {"message": "x"}})))
        self.assertEqual(ctx.exception.codigo, "api")
        with self.assertRaises(AuditorError) as ctx:
            auditar("texto", FICHAS, cliente=cliente_con(error=TimeoutError()))
        self.assertEqual(ctx.exception.codigo, "timeout")

    def test_respuesta_que_no_es_json_valido(self):
        with self.assertRaises(AuditorError) as ctx:
            auditar("texto", FICHAS, cliente=cliente_con("no es json"))
        self.assertEqual(ctx.exception.codigo, "formato")

    def test_sin_clave_no_intenta_llamar(self):
        import os
        previa = os.environ.pop("GEMINI_API_KEY", None)
        try:
            with self.assertRaises(AuditorError) as ctx:
                auditar("texto", FICHAS)
            self.assertEqual(ctx.exception.codigo, "sin_clave")
        finally:
            if previa is not None:
                os.environ["GEMINI_API_KEY"] = previa

    def test_sin_fichas_o_sin_texto_no_llama_a_la_api(self):
        cli = MagicMock()
        self.assertEqual(auditar("texto", [], cliente=cli), [])
        self.assertEqual(auditar("   ", FICHAS, cliente=cli), [])
        cli.models.generate_content.assert_not_called()

    def test_fichas_para_auditor_convierte_los_modelos(self):
        ana = User.objects.create_user("ana", password="x-clave-segura-1")
        p = Proyecto.objects.create(dueno=ana, titulo="La torre")
        f = Ficha.objects.create(proyecto=p, nombre="Ana", alias=["la capitana"], notas="Lidera")
        Atributo.objects.create(ficha=f, clave="Ojos", valor="verdes")
        self.assertEqual(fichas_para_auditor(p.fichas.prefetch_related("atributos")), [
            {"nombre": "Ana", "alias": ["la capitana"], "atributos": [{"clave": "Ojos", "valor": "verdes"}], "notas": "Lidera"}])

    def test_fichas_para_auditor_incluye_los_datos_de_la_ficha_completa(self):
        ana = User.objects.create_user("ana2", password="x-clave-segura-1")
        p = Proyecto.objects.create(dueno=ana, titulo="La torre")
        Ficha.objects.create(proyecto=p, nombre="Ana", datos={"edad": "34", "especie": "Elfa"})
        atributos = fichas_para_auditor(p.fichas.prefetch_related("atributos"))[0]["atributos"]
        self.assertIn({"clave": "Edad", "valor": "34"}, atributos)
        self.assertIn({"clave": "Especie", "valor": "Elfa"}, atributos)
