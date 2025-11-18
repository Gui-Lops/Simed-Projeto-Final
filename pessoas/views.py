from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import (
    CadastroUsuarioForm, PerfilForm, AgendarConsultaForm, 
    RelatorioConsultaForm, AgendarConsultaAtendenteForm, 
    MedicamentoForm, LoginUsuarioForm
)
from .models import User, Perfil, Consulta, Medicamento

# --- VIEWS DE PÁGINA ---

def home(request):
    return render(request, 'pessoas/home.html')

def sobre(request):
    return render(request, 'pessoas/sobre.html')

def produtos(request):
    return render(request, 'pessoas/lista_medicamentos.html')

def nos_encontre(request):
    return render(request, 'pessoas/encontre.html')

def cirurgia(request):
    # Esta vai carregar o cirurgia.html
    return render(request, 'pessoas/cirurgia.html')

def exames(request):
    # Esta vai carregar o exames.html
    return render(request, 'pessoas/exames.html')

def odontologia(request):
    # Esta vai carregar o odontologia.html
    return render(request, 'pessoas/odontologia.html')

def oftalmologia(request):
    # Esta vai carregar o oftalmologia.html (corrigido de 'oftalmolofia')
    return render(request, 'pessoas/oftalmologia.html') 

def tomografia(request):
    # Esta vai carregar o tomografia.html
    return render(request, 'pessoas/tomografia.html')

def consulta(request):
    # Esta vai carregar o consulta.html
    return render(request, 'pessoas/consulta.html')

def agenda(request):
    # Esta vai carregar o agenda.html
    return render(request, 'pessoas/agenda.html')

    
# --- VIEWS DE AUTENTICAÇÃO ---

def login_view(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('home') # Redireciona para home (ou 'painel')
    else:
        form = LoginUsuarioForm()
    return render(request, 'pessoas/login.html', {'form': form})

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Cria o perfil padrão (Paciente) para o novo usuário
            Perfil.objects.get_or_create(usuario=user, defaults={'tipo_usuario': 'paciente'})
            return redirect('login')  # redireciona após cadastro
    else:
        form = CadastroUsuarioForm()

    return render(request, 'pessoas/cadastrar_usuario.html', {'form': form})


def logout_view(request):
    """Faz o logout do usuário."""
    logout(request)
    return redirect('login')

# --- VIEWS DE MEDICAMENTOS ---

def excluir_medicamento(request, medicamento_id):
    medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
    if request.method == 'POST':
        medicamento.delete()
        return redirect('lista_medicamentos')
    return redirect('lista_medicamentos')

def cadastrar_medicamento(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_medicamentos')
    else:
        form = MedicamentoForm()
    
    contexto = {
        'form': form
    }
    return render(request, 'pessoas/cadastrar_medicamento.html', contexto)

def lista_medicamentos(request):
    medicamentos = Medicamento.objects.all().order_by('nome')
    contexto = {
        'medicamentos': medicamentos
    }
    return render(request, 'pessoas/lista_medicamentos.html', contexto)

# --- PAINÉIS (DASHBOARDS) ---

@login_required # Garante que apenas usuários logados acessem esta view
def painel(request):
    """
    View principal que verifica o tipo de usuário e o redireciona
    para o painel correto (médico, paciente ou atendente).
    """
    try:
        perfil = request.user.perfil
        if request.user.is_staff:
            return redirect('dashboard_consultas') # Redireciona admin para a página de consultas
        elif perfil.tipo_usuario == 'medico':
            return redirect('dashboard') # Redireciona médico para o painel médico
        elif perfil.tipo_usuario == 'paciente':
            return redirect('home')
        elif perfil.tipo_usuario == "atendente":
            return redirect("painel_atendente")
    except Perfil.DoesNotExist:
        # Caso um usuário (ex: admin) não tenha perfil, redireciona
        return redirect('login') # Ou para uma página de "Completar Perfil"
        
@login_required
def painel_medico(request):
    """Painel do médico, mostra suas consultas agendadas."""
    consultas = Consulta.objects.filter(medico=request.user).order_by('data_hora')
    return render(request, 'pessoas/painel_medico.html', {'consultas': consultas})

@login_required
def painel_paciente(request):
    """Painel do paciente, mostra suas consultas e permite agendar novas."""
    consultas = Consulta.objects.filter(paciente=request.user).order_by('data_hora')
    perfil = request.user.perfil

    if request.method == 'POST':
        form = AgendarConsultaForm(request.POST)
        perfil_form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid() and perfil_form.is_valid():
            nova_consulta = form.save(commit=False)
            nova_consulta.paciente = request.user
            nova_consulta.save()
            perfil_form.save()
            return redirect('painel_paciente')
    else:
        form = AgendarConsultaForm()
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'pessoas/painel_paciente.html', {
        'consultas': consultas,
        'form': form,
        'perfil_form': perfil_form
    })

@login_required
def checkup_consulta(request):
    # Esta vai carregar o checkup_consulta.html
    return render(request, 'pessoas/checkup_consulta.html')

@login_required
def checkup_tratamento(request):
    # Esta vai carregar o checkup_tratamento.html
    return render(request, 'pessoas/checkup_tratamento.html')
    
@login_required
def painel_atendente(request):
    """Painel do atendente, mostra todas as consultas e permite agendar novas."""
    if request.user.perfil.tipo_usuario != "atendente":
        return redirect("painel")

    consultas = Consulta.objects.all().order_by("data_hora")

    if request.method == "POST":
        form = AgendarConsultaAtendenteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("painel_atendente")
    else:
        form = AgendarConsultaAtendenteForm()

    return render(request, "pessoas/painel_atendente.html", {
        "consultas": consultas,
        "form": form
    })

# --- AÇÕES ESPECÍFICAS ---

@login_required
def escrever_relatorio(request, consulta_id):
    """Permite que um médico adicione ou edite um relatório de uma consulta."""
    consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)

    if request.method == 'POST':
        form = RelatorioConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            consulta.status = 'concluida'
            form.save()
            return redirect('painel_medico')
    else:
        form = RelatorioConsultaForm(instance=consulta)

    return render(request, 'pessoas/escrever_relatorio.html', {'form': form, 'consulta': consulta})

# --- DASHBOARD ADMINISTRATIVO ---

@login_required
def dashboard_admin(request):
    """
    Dashboard administrativo principal - redireciona para a página de estatísticas.
    Apenas usuários staff/admin podem acessar.
    """
    if not request.user.is_staff:
        return redirect('painel')
    
    return redirect('dashboard_consultas')

@login_required
def dashboard_produtos(request):
    """Lista todos os medicamentos cadastrados para edição."""
    if not request.user.is_staff:
        return redirect('painel')
    
    medicamentos = Medicamento.objects.all().order_by('nome')
    return render(request, 'pessoas/dashboard_produtos.html', {'medicamentos': medicamentos})

@login_required
def dashboard_consultas(request):
    """Dashboard com estatísticas de consultas."""
    if not request.user.is_staff:
        return redirect('painel')
    
    from django.db.models import Count, Q
    from datetime import date
    
    # Estatísticas
    total_consultas = Consulta.objects.count()
    consultas_realizadas = Consulta.objects.filter(status='concluida').count()
    consultas_agendadas = Consulta.objects.filter(status='agendada').count()
    consultas_canceladas = Consulta.objects.filter(status='cancelada').count()
    
    # Máximo de atendimentos por dia (consultas agendadas para hoje)
    max_atendimentos_dia = Consulta.objects.filter(
        data_hora__date=date.today()
    ).count()
    
    # Profissional mais ocupado (médico com mais consultas agendadas)
    medico_mais_ocupado = Consulta.objects.filter(
        status='agendada'
    ).values(
        'medico__first_name', 'medico__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total').first()
    
    profissional_nome = "N/A"
    if medico_mais_ocupado:
        profissional_nome = f"{medico_mais_ocupado['medico__first_name']} {medico_mais_ocupado['medico__last_name']}"
    
    contexto = {
        'total_consultas': total_consultas,
        'consultas_realizadas': consultas_realizadas,
        'max_atendimentos_dia': max_atendimentos_dia,
        'consultas_agendadas': consultas_agendadas,
        'consultas_canceladas': consultas_canceladas,
        'profissional_nome': profissional_nome,
    }
    
    return render(request, 'pessoas/dashboard_consultas.html', contexto)

@login_required
def dashboard_ocupacao(request):
    """Lista todas as consultas agendadas."""
    if not request.user.is_staff:
        return redirect('painel')
    
    consultas = Consulta.objects.filter(status='agendada').order_by('data_hora')
    return render(request, 'pessoas/dashboard_ocupacao.html', {'consultas': consultas})

@login_required
def dashboard_pacientes(request):
    """Lista todos os pacientes cadastrados."""
    if not request.user.is_staff:
        return redirect('painel')
    
    pacientes = User.objects.filter(perfil__tipo_usuario='paciente').order_by('first_name')
    return render(request, 'pessoas/dashboard_pacientes.html', {'pacientes': pacientes})

@login_required
def dashboard_medicos(request):
    """Lista todos os médicos cadastrados."""
    if not request.user.is_staff:
        return redirect('painel')
    
    medicos = User.objects.filter(perfil__tipo_usuario='medico').order_by('first_name')
    return render(request, 'pessoas/dashboard_medicos.html', {'medicos': medicos})

# --- AÇÕES DO DASHBOARD ---

@login_required
def editar_medicamento(request, medicamento_id):
    """Edita um medicamento existente."""
    if not request.user.is_staff:
        return redirect('painel')
    
    medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
    
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, request.FILES, instance=medicamento)
        if form.is_valid():
            form.save()
            return redirect('dashboard_produtos')
    else:
        form = MedicamentoForm(instance=medicamento)
    
    return render(request, 'pessoas/editar_medicamento.html', {'form': form, 'medicamento': medicamento})

@login_required
def cancelar_consulta_admin(request, consulta_id):
    """Cancela uma consulta (ação do admin)."""
    if not request.user.is_staff:
        return redirect('painel')
    
    consulta = get_object_or_404(Consulta, pk=consulta_id)
    consulta.status = 'cancelada'
    consulta.save()
    return redirect('dashboard_ocupacao')

@login_required
def remover_medico(request, medico_id):
    """Remove um médico do sistema."""
    if not request.user.is_staff:
        return redirect('painel')
    
    medico = get_object_or_404(User, pk=medico_id, perfil__tipo_usuario='medico')
    if request.method == 'POST':
        medico.delete()
    return redirect('dashboard_medicos')

@login_required
def remover_paciente(request, paciente_id):
    """Remove um paciente do sistema."""
    if not request.user.is_staff:
        return redirect('painel')
    
    paciente = get_object_or_404(User, pk=paciente_id, perfil__tipo_usuario='paciente')
    if request.method == 'POST':
        paciente.delete()
    return redirect('dashboard_pacientes')


@login_required
def gerenciar_cargos(request, user_id):
    """Permite ao admin alterar o cargo (tipo_usuario) de um usuário."""
    if not request.user.is_staff:
        return redirect('painel')
    
    usuario = get_object_or_404(User, pk=user_id)
    
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        # Se o usuário não tiver perfil, cria um perfil padrão (paciente)
        perfil = Perfil.objects.create(usuario=usuario, tipo_usuario='paciente')

    if request.method == 'POST':
        novo_cargo = request.POST.get('novo_cargo')
        if novo_cargo in dict(Perfil.TIPOS_USUARIO):
            perfil.tipo_usuario = novo_cargo
            perfil.save()
            # Redireciona para a lista de pacientes ou médicos dependendo do novo cargo
            if novo_cargo == 'medico':
                return redirect('dashboard_medicos')
            elif novo_cargo == 'paciente':
                return redirect('dashboard_pacientes')
            else:
                return redirect('dashboard_admin')
        
    contexto = {
        'usuario': usuario,
        'perfil': perfil,
        'cargos': Perfil.TIPOS_USUARIO,
    }
    return render(request, 'pessoas/gerenciar_cargos.html', contexto)
