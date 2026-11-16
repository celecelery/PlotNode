# Despliegue en PythonAnywhere (T-06, plan gratuito)

Requisitos: cuenta gratuita en <https://www.pythonanywhere.com>, el repositorio en GitHub y una clave gratuita de Google AI Studio.
El plan gratuito permite llamadas salientes a `*.googleapis.com`, que es lo que usa el auditor.

## 1. Código y entorno
En una consola **Bash** de PythonAnywhere:
```bash
git clone https://github.com/<usuario>/plotnode.git
cd plotnode
python3.12 -m venv ~/venv-plotnode
source ~/venv-plotnode/bin/activate
pip install -r requirements.txt
```
(Si el repositorio es privado, usa un token de acceso personal de GitHub en la URL de `git clone`.)

## 2. Configuración secreta
Crea `~/plotnode/.env` (nunca va a Git):
```
DEBUG=False
SECRET_KEY=<una-clave-larga-y-aleatoria>
ALLOWED_HOSTS=<usuario>.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://<usuario>.pythonanywhere.com
GEMINI_API_KEY=<tu-clave-de-ai-studio>
MAILERLITE_FORM_URL=<url-del-formulario-de-mailerlite>
```
Una clave aleatoria: `python -c "import secrets; print(secrets.token_urlsafe(50))"`.

## 3. Base de datos y estáticos
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 4. Aplicación web
1. Pestaña **Web** → *Add a new web app* → *Manual configuration* → Python 3.12.
2. **Virtualenv:** `/home/<usuario>/venv-plotnode`.
3. **Código:** `/home/<usuario>/plotnode`.
4. **Archivo WSGI:** reemplaza su contenido por:
   ```python
   import os, sys
   ruta = "/home/<usuario>/plotnode"
   if ruta not in sys.path:
       sys.path.insert(0, ruta)
   os.environ["DJANGO_SETTINGS_MODULE"] = "plotnode.settings"
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
   (`settings.py` ya lee el `.env` con python-dotenv, así que no hace falta repetir los secretos aquí.)
5. **Static files:** agrega dos filas: URL `/static/` → directorio `/home/<usuario>/plotnode/staticfiles` y URL `/media/` → directorio `/home/<usuario>/plotnode/media` (ahí se guardan las fotos de los personajes; crea la carpeta con `mkdir -p ~/plotnode/media`).
6. Pulsa **Reload**. La app abre en `https://<usuario>.pythonanywhere.com`.

## 5. Comprobar
- Abre la portada, regístrate, crea un proyecto y escribe: debe decir «Guardado».
- Selecciona un nombre con ficha: el panel la muestra.
- Crea una ficha con foto: la imagen se ve en el panel (si no, revisa el mapeo de `/media/`).
- `DEBUG=False` está activo (una URL inexistente muestra la página 404 simple, no la de depuración).

## Después de cada merge a `main`
```bash
cd ~/plotnode && source ~/venv-plotnode/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
y **Reload** en la pestaña Web.

## Cada mes
En el plan gratuito hay que entrar a la pestaña **Web** y pulsar el botón de extender la app (*Run until ...*), o se apaga.

## Si algo falla
- Pestaña **Web → Error log**: ahí aparece el traceback.
- *DisallowedHost* → falta el dominio en `ALLOWED_HOSTS`. *CSRF verification failed* → falta `CSRF_TRUSTED_ORIGINS`.
- El auditor responde «no está configurado» → falta `GEMINI_API_KEY` en `.env` (haz Reload).
- El correo de recuperar contraseña se imprime en el log del servidor; restablece contraseñas desde `/admin/` si hace falta.
