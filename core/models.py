import html
import re
import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import strip_tags

from .utils import contar_palabras, normalizar


class Perfil(models.Model):
    """Datos propios de PlotNode para cada usuario (1:1 con el User de Django)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    onboarding_completado = models.BooleanField(default=False)
    acepto_privacidad = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"

    def __str__(self):
        return f"Perfil de {self.user}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)


class Proyecto(models.Model):
    class Genero(models.TextChoices):
        NOVELA = "novela", "Novela"
        FANFIC = "fanfic", "Fanfic"
        RELATO = "relato", "Relato"
        OTRO = "otro", "Otro"

    dueno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="proyectos")
    titulo = models.CharField("título", max_length=150)
    genero = models.CharField("género", max_length=20, choices=Genero.choices, default=Genero.NOVELA)
    es_plantilla = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizado"]

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("proyecto_abrir", args=[self.pk])

    @property
    def palabras(self):
        return sum(c.palabras for c in self.capitulos.all())


class Capitulo(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="capitulos")
    titulo = models.CharField("título", max_length=150)
    orden = models.PositiveIntegerField(default=1)
    contenido = models.TextField(blank=True, help_text="HTML generado por el editor Quill.")
    palabras = models.PositiveIntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "capítulo"
        ordering = ["orden", "pk"]

    def __str__(self):
        return f"{self.proyecto} · {self.titulo}"

    def get_absolute_url(self):
        return reverse("editor", args=[self.pk])

    def save(self, *args, **kwargs):
        # Un espacio entre bloques: «<p>uno</p><p>dos</p>» son dos palabras, no «unodos».
        con_espacios = re.sub(r"(?i)</(p|h[1-6]|li|blockquote|div|pre)>|<(br|hr)\s*/?>", " ", self.contenido)
        self.palabras = contar_palabras(html.unescape(strip_tags(con_espacios)))
        super().save(*args, **kwargs)


def ruta_foto(instancia, nombre_archivo):
    """Nombre aleatorio: no se puede adivinar y no depende del nombre original."""
    extension = nombre_archivo.rsplit(".", 1)[-1].lower() if "." in nombre_archivo else "jpg"
    return f"fichas/{uuid.uuid4().hex}.{extension}"


class Ficha(models.Model):
    class Tipo(models.TextChoices):
        PERSONAJE = "personaje", "Personaje"
        LUGAR = "lugar", "Lugar"
        OBJETO = "objeto", "Objeto"
        EVENTO = "evento", "Evento"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="fichas")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.PERSONAJE)
    nombre = models.CharField(max_length=120)
    alias = models.JSONField(default=list, blank=True, help_text='Lista de alias, p. ej. ["la capitana"].')
    terminos = models.CharField(max_length=600, editable=False, blank=True,
                                help_text="Nombre y alias normalizados para buscar.")
    notas = models.TextField(blank=True)
    datos = models.JSONField(default=dict, blank=True, help_text="Campos del tipo de ficha (ver fichas_schema.py).")
    foto = models.ImageField(upload_to=ruta_foto, blank=True)
    indice_color = models.PositiveSmallIntegerField(
        default=0, editable=False, help_text="Posición en el ciclo de colores (lila, menta, durazno).")

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if self._state.adding and self.proyecto_id:
            # El color se fija al crear: sigue al de la última ficha del proyecto, así las vecinas no se repiten.
            ultima = Ficha.objects.filter(proyecto_id=self.proyecto_id).order_by("-pk").first()
            self.indice_color = ((ultima.indice_color + 1) % 3) if ultima else 0
        nombres = [self.nombre, *(self.alias or [])]
        self.terminos = "|".join(normalizar(n) for n in nombres if n and n.strip())
        super().save(*args, **kwargs)

    @property
    def color(self):
        """Color del personaje (ciclo del sistema de diseño: lila, menta, durazno)."""
        return ("lila", "menta", "durazno")[(self.indice_color or 0) % 3]

    @property
    def inicial(self):
        return (self.nombre or "?").strip()[:1].upper()

    def coincide(self, texto):
        """True si el texto (ya sea nombre o alias) corresponde a esta ficha."""
        return normalizar(texto) in self.terminos.split("|")


class Termino(models.Model):
    """Término propio del mundo de la historia (hechizos, razas, lugares inventados): HU-29."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="terminos")
    nombre = models.CharField(max_length=120)
    definicion = models.TextField(max_length=1000)
    categoria = models.CharField("categoría", max_length=60, blank=True)
    clave = models.CharField(max_length=120, editable=False, blank=True,
                             help_text="Nombre normalizado: evita términos repetidos.")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "término"
        constraints = [models.UniqueConstraint(fields=["proyecto", "clave"], name="termino_unico_por_proyecto")]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.clave = normalizar(self.nombre)
        super().save(*args, **kwargs)


class Atributo(models.Model):
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="atributos")
    clave = models.CharField(max_length=80)
    valor = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.clave}: {self.valor}"


class Relacion(models.Model):
    """Vínculo entre dos fichas (familia, amistad, alianza, romance, enemistad…). Es una sola fila y se ve desde ambas fichas."""

    class Categoria(models.TextChoices):
        FAMILIA = "familia", "Familia"
        AMISTAD = "amistad", "Amistad"
        ALIANZA = "alianza", "Alianza"
        ROMANCE = "romance", "Romance"
        ENEMISTAD = "enemistad", "Enemistad"
        OTRA = "otra", "Otra"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="relaciones")
    origen = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="relaciones_salientes")
    destino = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="relaciones_entrantes")
    categoria = models.CharField("categoría", max_length=20, choices=Categoria.choices, default=Categoria.OTRA)
    etiqueta = models.CharField("cómo se llama", max_length=60, blank=True,
                                help_text="Ej. «hermanas», «mentor de Mateo». Si queda vacío se usa la categoría.")
    nota = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "relación"
        verbose_name_plural = "relaciones"
        ordering = ["pk"]

    def __str__(self):
        return f"{self.origen} — {self.destino} ({self.texto})"

    @property
    def texto(self):
        return self.etiqueta or self.get_categoria_display()

    def otro(self, ficha):
        return self.destino if ficha.pk == self.origen_id else self.origen


class EventoTrama(models.Model):
    """Evento de la historia para la línea de tiempo. No es el EventoUso de las métricas."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="eventos_trama")
    titulo = models.CharField("título", max_length=120)
    descripcion = models.TextField("descripción", max_length=1000, blank=True)
    etapa = models.CharField(max_length=40, help_text="Momento de la historia en texto libre: «Año 3», «Hace una semana».")
    orden = models.PositiveIntegerField(default=1, editable=False, help_text="Posición del evento en la línea de tiempo (se cambia a mano).")
    capitulo = models.ForeignKey(Capitulo, on_delete=models.SET_NULL, null=True, blank=True, related_name="eventos_trama")
    participantes = models.ManyToManyField(Ficha, blank=True, related_name="eventos_trama")

    class Meta:
        verbose_name = "evento de la trama"
        verbose_name_plural = "eventos de la trama"
        ordering = ["orden", "pk"]

    def __str__(self):
        return f"{self.etapa}: {self.titulo}"


class Nota(models.Model):
    """Nota del tablón de ideas: idea suelta o pasaje enviado desde el editor."""

    class Tipo(models.TextChoices):
        IDEA = "idea", "Idea"
        TEXTO = "texto", "Del texto"

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="notas")
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.IDEA)
    contenido = models.TextField(max_length=1000)
    class Color(models.TextChoices):
        LILA = "lila", "Lila"
        MENTA = "menta", "Menta"
        DURAZNO = "durazno", "Durazno"

    color = models.CharField(max_length=10, choices=Color.choices, default=Color.LILA)
    ficha = models.ForeignKey(Ficha, on_delete=models.SET_NULL, null=True, blank=True, related_name="notas_tablon")
    capitulo = models.ForeignKey(Capitulo, on_delete=models.SET_NULL, null=True, blank=True, related_name="notas_tablon")
    x = models.IntegerField(default=24)
    y = models.IntegerField(default=24)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.contenido[:40]


class Alerta(models.Model):
    class Estado(models.TextChoices):
        NUEVA = "nueva", "Nueva"
        CORREGIDA = "corregida", "Corregida"
        FALSO_POSITIVO = "falso_positivo", "Falso positivo"

    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name="alertas")
    ficha = models.ForeignKey(Ficha, on_delete=models.SET_NULL, null=True, blank=True, related_name="alertas")
    fragmento = models.TextField()
    dato_en_ficha = models.CharField(max_length=300, blank=True)
    explicacion = models.TextField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.NUEVA)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada"]

    def __str__(self):
        return f"Alerta en {self.capitulo}: {self.explicacion[:40]}"


class EventoUso(models.Model):
    """Registro de uso para medir la señal y el umbral del MVP.

    No confundir con las fichas de tipo «evento» (Ficha.Tipo.EVENTO): esas son parte de la historia."""

    class Tipo(models.TextChoices):
        CONSULTA_FICHA = "consulta_ficha", "Consulta de ficha"
        VERIFICACION = "verificacion", "Verificación de coherencia"
        SESION_ESCRITURA = "sesion_escritura", "Sesión de escritura"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eventos")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    valor = models.IntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario} · {self.get_tipo_display()}"
