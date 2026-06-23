from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "seu@email.com"}),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )


class UserForm(forms.ModelForm):
    class Meta:
        model = None
        fields = ["first_name", "last_name", "email", "phone", "theme"]
