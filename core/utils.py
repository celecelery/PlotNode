import re
import unicodedata

_PALABRA = re.compile(r"[\w'’-]+", re.UNICODE)


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos y sin espacios extra: 'La Capitána ' -> 'la capitana'."""
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.lower().split())


def contar_palabras(texto: str) -> int:
    """Cuenta palabras en texto plano (acepta acentos, ñ, apóstrofos y guiones)."""
    return len(_PALABRA.findall(texto or ""))
