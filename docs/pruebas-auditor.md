# Pruebas del auditor de coherencia (T-03)

El servicio está en `core/services/auditor.py` (SDK `google-genai`, nivel gratuito de Gemini).
Las pruebas automáticas (`core/tests/test_auditor.py`) usan un cliente simulado: no gastan cuota ni necesitan clave.
**Esta tabla es la prueba real contra Gemini y se llena a mano**, porque necesita tu `GEMINI_API_KEY`.

## Cómo correrla

1. Pon `GEMINI_API_KEY=...` en tu `.env` (clave gratuita de Google AI Studio). Opcional: `MODELO_AUDITOR=` para cambiar de modelo (por defecto `gemini-2.5-flash-lite`).
2. `python manage.py shell` y pega:

```python
from core.services.auditor import auditar
ana = {"nombre": "Ana", "alias": ["la capitana"], "notas": "",
       "atributos": [{"clave": "Ojos", "valor": "verdes"}, {"clave": "Edad", "valor": "30"},
                     {"clave": "Habilidad", "valor": "no sabe nadar"}, {"clave": "Pasatiempo", "valor": "tejer"}]}
caso = "Ana parpadeó y sus ojos azules brillaron."
print(auditar(caso, [ana]))
```

3. Repite con cada texto y anota el resultado.

## Ficha base

**Ana** (alias: la capitana) · Ojos: verdes · Edad: 30 · Habilidad: no sabe nadar · Pasatiempo: tejer.

## Casos

| # | Texto de prueba | Debe detectar | Resultado | ¿Acierto? |
|---|---|---|---|---|
| 1 | «Ana parpadeó y sus ojos azules brillaron.» | Ojos: azules ≠ verdes | | |
| 2 | «La capitana, de 45 años, subió al puente.» | Edad: 45 ≠ 30 (por el alias) | | |
| 3 | «Ana se lanzó al mar y nadó hasta la isla.» | Habilidad: no sabe nadar | | |
| 4 | «Ana tejía en silencio junto a la ventana.» | Nada (control) | | |
| 5 | «Ana abrió la puerta y miró la lluvia.» | Nada (control) | | |

## Resumen (llenar al terminar)

- Aciertos: __ de 3 · Falsos positivos en los 2 controles: __ · Tiempo de respuesta típico: __ s
- Observaciones sobre el prompt y ajustes que hicieron falta:
