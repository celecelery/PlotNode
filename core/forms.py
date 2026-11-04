from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Proyecto


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True,
                             help_text="Lo usamos para recuperar tu contraseña.")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Letras, números y @ . + - _ (sin espacios)."

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ("titulo", "genero")
        widgets = {"titulo": forms.TextInput(attrs={"placeholder": "Ej. Crónicas de la torre"})}
