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
        self.palabras = contar_palabras(strip_tags(self.contenido))
        super().save(*args, **kwargs)


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

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        nombres = [self.nombre, *(self.alias or [])]
        self.terminos = "|".join(normalizar(n) for n in nombres if n and n.strip())
        super().save(*args, **kwargs)

    def coincide(self, texto):
        """True si el texto (ya sea nombre o alias) corresponde a esta ficha."""
        return normalizar(texto) in self.terminos.split("|")


class Atributo(models.Model):
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="atributos")
    clave = models.CharField(max_length=80)
    valor = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.clave}: {self.valor}"


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


class Evento(models.Model):
    """Registro de uso para medir la señal y el umbral del MVP."""

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
