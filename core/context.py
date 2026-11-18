from django.conf import settings


def cuentas(request):
    """El botón de Google solo se muestra si la app de Google está configurada."""
    return {"google_activo": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)}
