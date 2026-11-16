"""Auditor de coherencia con la API gratuita de Gemini (T-03).

Compara un texto con las fichas de los personajes mencionados y devuelve las
contradicciones directas. La IA solo señala: nunca reescribe el texto.
La clave vive en la variable de entorno GEMINI_API_KEY (.env), nunca en el código.
"""
import json
import os

from django.conf import settings
from google import genai
from google.genai import errors, types

from ..fichas_schema import secciones_con_datos

MODELO_POR_DEFECTO = "gemini-2.5-flash-lite"
TIMEOUT_MS = 15_000  # RNF-02: máximo 15 s

ESQUEMA = {
    "type": "object",
    "properties": {
        "inconsistencias": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "personaje": {"type": "string"},
                    "dato_en_ficha": {"type": "string"},
                    "fragmento": {"type": "string"},
                    "explicacion": {"type": "string"},
                },
                "required": ["personaje", "dato_en_ficha", "fragmento", "explicacion"],
            },
        }
    },
    "required": ["inconsistencias"],
}

INSTRUCCION = (
    "Eres un auditor de continuidad para escritores de ficción. Recibes FICHAS (datos que el "
    "autor ya decidió) y un TEXTO. Señala SOLO contradicciones directas entre el texto y las "
    "fichas. No sugieras mejoras de estilo, no inventes datos y no reescribas la historia. "
    "'dato_en_ficha' es el dato tal como está en la ficha (p. ej. 'Ojos: verdes'); 'fragmento' "
    "es la frase exacta del texto que choca. Si no hay contradicciones, devuelve una lista "
    "vacía. Responde en español."
)


class AuditorError(Exception):
    """Error controlado: `mensaje` se puede mostrar tal cual a la escritora."""

    def __init__(self, mensaje, codigo="error"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo  # sin_clave | cuota | api | formato | timeout


def fichas_para_auditor(fichas):
    """Modelos Ficha -> dicts con solo lo necesario (RNF-04: nada más sale del servidor)."""
    datos = []
    for f in fichas:
        atributos = sorted(f.atributos.all(), key=lambda a: a.pk)
        campos = [{"clave": c["etiqueta"], "valor": c["valor"]}
                  for sec in secciones_con_datos(f.tipo, f.datos) for c in sec["campos"]]
        datos.append({
            "nombre": f.nombre,
            "alias": list(f.alias or []),
            # La ficha completa (edad, ojos, rol…) vive en `datos`; los atributos libres van aparte.
            "atributos": campos + [{"clave": a.clave, "valor": a.valor} for a in atributos],
            "notas": f.notas,
        })
    return datos


def _fichas_a_texto(fichas):
    bloques = []
    for f in fichas:
        alias = f" (alias: {', '.join(f['alias'])})" if f.get("alias") else ""
        attrs = "; ".join(f"{a['clave']}: {a['valor']}" for a in f["atributos"])
        notas = f" Notas: {f['notas']}" if f.get("notas") else ""
        bloques.append(f"- {f['nombre']}{alias}. {attrs}.{notas}")
    return "\n".join(bloques)


def auditar(texto, fichas, cliente=None):
    """Devuelve [{personaje, dato_en_ficha, fragmento, explicacion}] (lista vacía = coherente).

    `fichas` son dicts (ver fichas_para_auditor), solo las mencionadas en el texto.
    Lanza AuditorError con un mensaje amable si falla o se agota la cuota diaria (429).
    """
    if not fichas or not (texto or "").strip():
        return []
    if cliente is None:
        clave = os.environ.get("GEMINI_API_KEY", "")
        if not clave:
            raise AuditorError("El auditor no está configurado todavía.", "sin_clave")
        cliente = genai.Client(api_key=clave, http_options=types.HttpOptions(timeout=TIMEOUT_MS))
    modelo = getattr(settings, "MODELO_AUDITOR", "") or MODELO_POR_DEFECTO
    prompt = f"FICHAS:\n{_fichas_a_texto(fichas)}\n\nTEXTO:\n{texto}"
    try:
        resp = cliente.models.generate_content(
            model=modelo,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCCION,
                response_mime_type="application/json",
                response_schema=ESQUEMA,
                temperature=0.1,
            ),
        )
        return json.loads(resp.text)["inconsistencias"]
    except errors.APIError as e:
        if getattr(e, "code", None) == 429:
            raise AuditorError("Se agotó la cuota diaria del auditor. Inténtalo mañana.", "cuota") from e
        raise AuditorError("No pude consultar al auditor ahora. Inténtalo de nuevo en un momento.", "api") from e
    except (ValueError, KeyError, TypeError) as e:
        raise AuditorError("El auditor devolvió una respuesta que no entendí. Inténtalo de nuevo.", "formato") from e
    except Exception as e:  # tiempo de espera o sin red
        raise AuditorError("El auditor tardó demasiado o no hay conexión. Inténtalo de nuevo.", "timeout") from e
