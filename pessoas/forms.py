# pessoas/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Medicamento, Perfil, Consulta
from django.contrib.auth import authenticate

class LoginUsuarioForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuário',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'form-control',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Nome de usuário ou senha incorretos.")
            cleaned_data['user'] = user
        return cleaned_data

# Formulário para um novo usuário se cadastrar
class CadastroUsuarioForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome',
            'class': 'form-control',
        })
    )

    # first_name = forms.CharField(
    #     max_length=150,
    #     required=True,
    #     widget=forms.TextInput(attrs={
    #         'placeholder': 'Nome',
    #         'class': 'form-control',
    #     })
    # )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Sobrenome',
            'class': 'form-control',
        })
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ["username", "last_name", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    # --- INÍCIO DA ALTERAÇÃO ---
    # --- FIM DA ALTERAÇÃO ---

    # Precisamos salvar o Perfil junto com o User
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # O Perfil será criado separadamente ou atualizado
        return user

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["data_nascimento", "rg", "endereco"]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulário para agendar uma nova consulta (para o paciente)
class AgendarConsultaForm(forms.ModelForm):
    # O campo "medico" será um dropdown com todos os usuários que são médicos
    medico = forms.ModelChoiceField(queryset=User.objects.filter(perfil__tipo_usuario="medico"))
    data_hora = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    class Meta:
        model = Consulta
        fields = ["medico", "data_hora"]

# Formulário para agendar uma nova consulta (para o atendente)
class AgendarConsultaAtendenteForm(forms.ModelForm):
    # O atendente precisa selecionar o paciente
    paciente = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__tipo_usuario="paciente"),
        label="Paciente"
    )
    # O atendente precisa selecionar o médico
    medico = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__tipo_usuario="medico"),
        label="Médico"
    )
    data_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Data e Hora"
    )

    class Meta:
        model = Consulta
        fields = ["paciente", "medico", "data_hora"]

# Formulário para o médico escrever o relatório
class RelatorioConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ["relatorio"]
        widgets = {
            "relatorio": forms.Textarea(attrs={"rows": 5}),
        }
class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        # Lista dos campos do modelo que devem aparecer no formulário
        fields = ['nome', 'foto', 'valor', 'necessita_receita']
        
        # Opcional: Adicionar classes do Bootstrap para estilização
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'necessita_receita': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
