from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm, SetPasswordForm,
                                       UserCreationForm)

from .models import Proyecto


class SinDosPuntos:
    """Etiquetas sin «:» al final, como el resto de la interfaz."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)


class LoginForm(SinDosPuntos, AuthenticationForm):
    pass


class RecuperarForm(SinDosPuntos, PasswordResetForm):
    pass


class NuevaContrasenaForm(SinDosPuntos, SetPasswordForm):
    pass


class RegistroForm(SinDosPuntos, UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    privacidad = forms.BooleanField(
        label="Entiendo y acepto el aviso de privacidad",
        error_messages={"required": "Para crear tu cuenta, acepta el aviso de privacidad."})

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .views import _correo_real
        self.fields["email"].help_text = ("Lo usamos para recuperar tu contraseña." if _correo_real()
                                          else "Para identificarte. Esta versión de prueba aún no envía correos.")
        self.fields["username"].help_text = "Letras, números y @ . + - _ (sin espacios)."
        self.fields["password1"].help_text = "Mínimo 8 caracteres. Que no sea solo números ni una contraseña común."
        self.fields["password2"].label = "Repite la contraseña"
        self.fields["password2"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email


class ProyectoForm(SinDosPuntos, forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ("titulo", "genero")
        widgets = {"titulo": forms.TextInput(attrs={"placeholder": "Ej. Crónicas de la torre"})}


# --- Capítulos (HU-05) y fichas (HU-07) ---------------------------------------
from django.forms import inlineformset_factory  # noqa: E402

from django.conf import settings  # noqa: E402

from .fichas_schema import (AYUDA_NOTAS, ELEGIR, ETIQUETA_NOTAS, LARGO, MAX_CORTO, MAX_LARGO,  # noqa: E402
                            SECCIONES, campos_de)
from .models import Atributo, Capitulo, Ficha, Termino  # noqa: E402
from .utils import normalizar  # noqa: E402


class CapituloForm(SinDosPuntos, forms.ModelForm):
    class Meta:
        model = Capitulo
        fields = ("titulo",)

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if not titulo:
            raise forms.ValidationError("El capítulo necesita un título.")
        return titulo


MAX_ALIAS = 8
MAX_LARGO_ALIAS = 50
FORMATOS_FOTO = {"JPEG", "PNG", "WEBP"}


class FichaBaseForm(SinDosPuntos, forms.ModelForm):
    """Datos comunes de toda ficha. Los campos de cada tipo se agregan en `FichaForm(tipo)`."""

    alias_texto = forms.CharField(
        label="Alias", required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "la capitana, Ani"}),
        help_text="Otros nombres con que aparece en el texto. Sepáralos con comas o saltos de línea.",
    )
    foto = forms.ImageField(
        label="Foto", required=False, widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        error_messages={"invalid_image": "El archivo no es una imagen válida. Usa JPG, PNG o WebP."},
    )
    quitar_foto = forms.BooleanField(label="Quitar la foto", required=False)

    class Meta:
        model = Ficha
        fields = ("nombre", "notas", "foto")
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Ana"}),
            "notas": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {"nombre": "Nombre"}

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        self._foto_anterior = self.instance.foto.name if self.instance.pk and self.instance.foto else ""
        tipo = self.instance.tipo
        self.fields["notas"].label = ETIQUETA_NOTAS[tipo]
        self.fields["notas"].widget.attrs["placeholder"] = AYUDA_NOTAS.get(tipo, "Lo que quieras recordar.")
        if self.instance.pk:
            self.fields["alias_texto"].initial = "\n".join(self.instance.alias or [])
            for campo in campos_de(tipo):
                self.initial[f"d_{campo['clave']}"] = (self.instance.datos or {}).get(campo["clave"], "")

    # --- validaciones ---
    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())
        if not nombre:
            raise forms.ValidationError("La ficha necesita un nombre.")
        return nombre

    def clean_alias_texto(self):
        crudo = self.cleaned_data["alias_texto"].replace(",", "\n")
        alias, vistos = [], set()
        for a in crudo.splitlines():
            a = " ".join(a.split())
            if a and normalizar(a) not in vistos:
                vistos.add(normalizar(a))
                alias.append(a)
        if len(alias) > MAX_ALIAS:
            raise forms.ValidationError(f"Máximo {MAX_ALIAS} alias por ficha.")
        if any(len(a) > MAX_LARGO_ALIAS for a in alias):
            raise forms.ValidationError(f"Cada alias admite hasta {MAX_LARGO_ALIAS} caracteres.")
        return alias

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if not foto or not hasattr(foto, "image"):
            return foto
        if foto.size > settings.MAX_FOTO_BYTES:
            raise forms.ValidationError("La imagen pesa más de 2 MB. Elige una más ligera.")
        if foto.image.format not in FORMATOS_FOTO:
            raise forms.ValidationError("Solo se aceptan imágenes JPG, PNG o WebP.")
        return foto

    def clean(self):
        datos = super().clean()
        nombre, alias = datos.get("nombre"), datos.get("alias_texto")
        if nombre is None or alias is None or self.proyecto is None:
            return datos
        propios = {normalizar(n) for n in [nombre, *alias]}
        # Un mismo nombre o alias no puede apuntar a dos fichas: el panel no sabría cuál mostrar.
        for otra in self.proyecto.fichas.exclude(pk=self.instance.pk):
            choque = propios & set(otra.terminos.split("|"))
            if choque:
                raise forms.ValidationError(
                    f"«{sorted(choque)[0]}» ya está en la ficha de {otra.nombre}. Usa un nombre o alias distinto.")
        return datos

    def save(self, commit=True):
        foto_anterior = self._foto_anterior   # antes de que la validación asigne la foto nueva
        ficha = super().save(commit=False)
        ficha.alias = self.cleaned_data["alias_texto"]
        ficha.datos = {c["clave"]: self.cleaned_data.get(f"d_{c['clave']}", "").strip()
                       for c in campos_de(ficha.tipo) if self.cleaned_data.get(f"d_{c['clave']}", "").strip()}
        quitar = self.cleaned_data.get("quitar_foto") and not self.files.get(self.add_prefix("foto"))
        if quitar:
            ficha.foto = ""
        if commit:
            ficha.save()
            reemplazada = foto_anterior and foto_anterior != (ficha.foto.name if ficha.foto else "")
            if reemplazada:  # no dejar archivos huérfanos
                ficha.foto.storage.delete(foto_anterior)
        return ficha


def FichaForm(tipo, *args, **kwargs):
    """Formulario de una ficha del tipo dado (personaje, lugar, objeto o evento)."""
    campos = {}
    for campo in campos_de(tipo):
        largo = campo["tipo"] == LARGO
        if campo["tipo"] == ELEGIR:
            campos[f"d_{campo['clave']}"] = forms.ChoiceField(
                label=campo["etiqueta"], required=False,
                choices=[("", "Sin definir")] + [(o, o) for o in campo["opciones"]])
        else:
            campos[f"d_{campo['clave']}"] = forms.CharField(
                label=campo["etiqueta"], required=False, max_length=MAX_LARGO if largo else MAX_CORTO,
                widget=forms.Textarea(attrs={"rows": 2, "placeholder": campo["ayuda"]}) if largo
                else forms.TextInput(attrs={"placeholder": campo["ayuda"]}))
    clase = type(f"FichaForm_{tipo}", (FichaBaseForm,), campos)
    return clase(*args, **kwargs)


def secciones_del_formulario(form):
    """Agrupa los campos del formulario en las secciones de su tipo, para dibujarlos."""
    return [{"titulo": sec["titulo"], "abierta": sec["abierta"],
             "campos": [form[f"d_{c['clave']}"] for c in sec["campos"]]}
            for sec in SECCIONES[form.instance.tipo]]


class TerminoForm(SinDosPuntos, forms.ModelForm):
    class Meta:
        model = Termino
        fields = ("nombre", "definicion", "categoria")
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Orbe de Ilvar"}),
            "definicion": forms.Textarea(attrs={"rows": 3, "placeholder": "Qué significa en tu mundo."}),
            "categoria": forms.TextInput(attrs={"placeholder": "Hechizo, raza, lugar…"}),
        }
        labels = {"nombre": "Término", "definicion": "Definición", "categoria": "Categoría (opcional)"}

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())
        if not nombre:
            raise forms.ValidationError("El término necesita un nombre.")
        if self.proyecto is not None and self.proyecto.terminos.exclude(pk=self.instance.pk).filter(
                clave=normalizar(nombre)).exists():
            raise forms.ValidationError("Ya existe un término con ese nombre en el glosario.")
        return nombre

    def clean_definicion(self):
        definicion = self.cleaned_data["definicion"].strip()
        if not definicion:
            raise forms.ValidationError("Escribe qué significa el término.")
        return definicion


AtributoFormSet = inlineformset_factory(
    Ficha, Atributo, fields=("clave", "valor"), extra=2, can_delete=True,
    widgets={
        "clave": forms.TextInput(attrs={"placeholder": "Ej. Edad"}),
        "valor": forms.TextInput(attrs={"placeholder": "Ej. 17"}),
    },
)


# --- Iteración 3: relaciones, línea de tiempo y tablón ---------------------------------
from .models import EventoTrama, Nota, Relacion  # noqa: E402


class RelacionForm(SinDosPuntos, forms.ModelForm):
    class Meta:
        model = Relacion
        fields = ("origen", "destino", "categoria", "etiqueta", "nota")
        labels = {"origen": "Personaje o ficha", "destino": "Con quién", "categoria": "Tipo de relación",
                  "etiqueta": "Cómo se llama (opcional)", "nota": "Nota (opcional)"}
        widgets = {"etiqueta": forms.TextInput(attrs={"placeholder": "Hermanas, mentor de…"}),
                   "nota": forms.TextInput(attrs={"placeholder": "Qué las une o las separa"})}

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        fichas = proyecto.fichas.all()
        self.fields["origen"].queryset = fichas
        self.fields["destino"].queryset = fichas
        self.fields["origen"].empty_label = "Elige una ficha"
        self.fields["destino"].empty_label = "Elige una ficha"

    def clean(self):
        datos = super().clean()
        o, d = datos.get("origen"), datos.get("destino")
        if o and d:
            if o.pk == d.pk:
                raise forms.ValidationError("Una ficha no puede relacionarse consigo misma.")
            repetida = self.proyecto.relaciones.exclude(pk=self.instance.pk).filter(
                categoria=datos.get("categoria")).filter(
                models.Q(origen=o, destino=d) | models.Q(origen=d, destino=o))
            if repetida.exists():
                raise forms.ValidationError("Esas dos fichas ya tienen una relación de ese tipo.")
        return datos


class EventoTramaForm(SinDosPuntos, forms.ModelForm):
    class Meta:
        model = EventoTrama
        fields = ("titulo", "etapa", "descripcion", "capitulo", "participantes")
        labels = {"titulo": "Qué pasa", "etapa": "Cuándo (texto libre)", "descripcion": "Descripción (opcional)",
                  "capitulo": "Capítulo donde ocurre (opcional)", "participantes": "Quiénes participan"}
        widgets = {"titulo": forms.TextInput(attrs={"placeholder": "Cruzan el puente"}),
                   "etapa": forms.TextInput(attrs={"placeholder": "Año 3, Hace una semana, Día 2…"}),
                   "descripcion": forms.Textarea(attrs={"rows": 3}),
                   "participantes": forms.CheckboxSelectMultiple}

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        self.fields["capitulo"].queryset = proyecto.capitulos.all()
        self.fields["capitulo"].empty_label = "Ninguno"
        self.fields["participantes"].queryset = proyecto.fichas.all()
        self.fields["participantes"].required = False

    def clean_titulo(self):
        t = " ".join(self.cleaned_data["titulo"].split())
        if not t:
            raise forms.ValidationError("Escribe qué pasa en este evento.")
        return t

    def clean_etapa(self):
        e = " ".join(self.cleaned_data["etapa"].split())
        if not e:
            raise forms.ValidationError("Indica cuándo ocurre.")
        return e

    def save(self, commit=True):
        evento = super().save(commit=False)
        evento.proyecto = self.proyecto
        if not evento.pk:       # un evento nuevo va al final; el orden se cambia a mano con subir y bajar
            ultimo = self.proyecto.eventos_trama.aggregate(m=models.Max("orden"))["m"]
            evento.orden = (ultimo or 0) + 1
        if commit:
            evento.save()
            self.save_m2m()
        return evento


class NotaForm(SinDosPuntos, forms.ModelForm):
    class Meta:
        model = Nota
        fields = ("contenido", "ficha", "capitulo", "color")
        labels = {"contenido": "Tu idea", "ficha": "Ficha relacionada (opcional)",
                  "capitulo": "Capítulo relacionado (opcional)", "color": "Color de la nota"}
        widgets = {"contenido": forms.Textarea(attrs={"rows": 4, "placeholder": "Una escena, una duda, un giro…"})}

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ficha"].queryset = proyecto.fichas.all()
        self.fields["ficha"].empty_label = "Ninguna"
        self.fields["capitulo"].queryset = proyecto.capitulos.all()
        self.fields["capitulo"].empty_label = "Ninguno"
        self.fields["color"].required = False

    def clean_color(self):
        return self.cleaned_data.get("color") or Nota.Color.LILA

    def clean_contenido(self):
        c = self.cleaned_data["contenido"].strip()
        if not c:
            raise forms.ValidationError("Escribe algo en la nota.")
        return c
