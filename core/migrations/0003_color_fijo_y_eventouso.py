from django.db import migrations, models


def asignar_colores(apps, schema_editor):
    """Las fichas que ya existen conservan el orden de colores por proyecto (lila, menta, durazno)."""
    Ficha = apps.get_model("core", "Ficha")
    contador = {}
    for ficha in Ficha.objects.order_by("proyecto_id", "pk"):
        n = contador.get(ficha.proyecto_id, 0)
        Ficha.objects.filter(pk=ficha.pk).update(indice_color=n % 3)
        contador[ficha.proyecto_id] = n + 1


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_ficha_completa_y_glosario"),
    ]

    operations = [
        migrations.RenameModel(old_name="Evento", new_name="EventoUso"),
        migrations.AddField(
            model_name="ficha",
            name="indice_color",
            field=models.PositiveSmallIntegerField(
                default=0, editable=False, help_text="Posición en el ciclo de colores (lila, menta, durazno)."),
        ),
        migrations.RunPython(asignar_colores, migrations.RunPython.noop),
    ]
