from django import forms
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
    email = forms.EmailField(label="Correo electrónico", required=True,
                             help_text="Lo usamos para recuperar tu contraseña.")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
