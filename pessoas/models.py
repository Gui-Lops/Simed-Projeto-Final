# pessoas/models.py

from django.db import models
from django.contrib.auth.models import User # Importa o modelo de usuário padrão do Django

# Modelo para estender o User padrão com o tipo de perfil (Médico ou Paciente)
class Perfil(models.Model):
    TIPOS_USUARIO = (
        ('medico', 'Médico'),
        ('paciente', 'Paciente'),
        ("atendente", "Atendente"),
    )
    # Relação um-para-um: cada usuário terá um, e apenas um, perfil.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO)
    data_nascimento = models.DateField(null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.get_tipo_usuario_display()}'

# Modelo para armazenar as consultas
class Consulta(models.Model):
    STATUS_CHOICES = (
        ('agendada', 'Agendada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    )
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_como_paciente')
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_como_medico')
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendada')
    relatorio = models.TextField(blank=True, null=True, help_text="Relatório a ser preenchido pelo médico após a consulta.")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Consulta de {self.paciente.username} com Dr(a). {self.medico.last_name} em {self.data_hora.strftime("%d/%m/%Y %H:%M")}'

    class Meta:
        ordering = ['-data_hora']

        # pessoas/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator # Importe o validator

class Medicamento(models.Model):
    """
    Este modelo armazena o cadastro de medicamentos da clínica.
    """
    nome = models.CharField(
        max_length=200, 
        unique=True, 
        help_text="Nome comercial do medicamento."
    )
    foto = models.ImageField(
        upload_to='medicamentos/', 
        blank=True, 
        null=True, 
        help_text="Foto da embalagem do medicamento."
    )
    valor = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Preço do medicamento em R$."
    )
    necessita_receita = models.BooleanField(
        default=True, 
        help_text="Marque esta opção se o medicamento exige receita médica."
    )

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome'] # Ordena os medicamentos por nome em ordem alfabética