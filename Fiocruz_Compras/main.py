import sys
import os
import warnings  # Adiciona a biblioteca warnings
import logging  # Para registrar erros
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDateTime, QTimer, Qt
from db_operations import authenticate_user, add_user
from utils import show_message_box
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtWidgets import QVBoxLayout, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap
from listas_suspensas import Listas_Suspensas
from db_connection import get_pyodbc_connection
from planilhas import PlanilhasApp

# Inicializa o QApplication ANTES de criar qualquer QWidget
app = QtWidgets.QApplication([])

# Ignora warnings específicos ou todos os warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)  # Ou use warnings.filterwarnings("ignore") para ignorar todos

# Configuração do logger
logging.basicConfig(filename="app_errors.log", 
                    level=logging.ERROR, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Testa a conexão ao iniciar
def testar_conexao():
    conexao = get_pyodbc_connection(log=False)
    if conexao:
        print("Conexão obtida com sucesso no main.py")
        conexao.close()  # Fecha a conexão após testar
    else:
        print("Erro ao obter a conexão. Verifique as configurações.")


# Retorna o caminho absoluto para um arquivo, considerando se o script está sendo executado diretamente ou empacotado pelo PyInstaller.
def resource_path(relative_path):
    try:
        # Quando empacotado pelo PyInstaller, _MEIPASS contém o caminho temporário onde os arquivos são extraídos
        base_path = sys._MEIPASS
    except AttributeError:
        # Quando rodando diretamente, o caminho base é o diretório atual do script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Configuração do Splash Screen que exibe uma imagem do carregamento do sistema
splash_pix = QPixmap(resource_path("carregamento.png"))  # Substitua pelo caminho da sua imagem
splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
splash.setWindowFlag(Qt.FramelessWindowHint)  # Remove bordas
splash.showMessage("Carregando o sistema...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
splash.show()

# Simula carregamento (use `QTimer` para delays mais longos ou tarefas reais)
QTimer.singleShot(2000, lambda: splash.showMessage("Inicializando componentes...", Qt.AlignBottom | Qt.AlignCenter, Qt.white))
QTimer.singleShot(2000, splash.close)  # Fecha o Splash após 4 segundos


# Carregando as interfaces
try:
    primeira_tela = uic.loadUi(resource_path("primeira_tela.ui"))
    segunda_tela = uic.loadUi(resource_path("segunda_tela.ui"))
    tela_cadastro = uic.loadUi(resource_path("tela_cadastro.ui"))

    print("Interfaces carregadas com sucesso.")
except Exception as e:
    logging.error(f"Erro ao carregar as interfaces: {e}")
    print(f"Erro ao carregar as interfaces: {e}")

# Crie a variável global
listas_suspensas = None

try:
    # Crie uma instância
    listas_suspensas = Listas_Suspensas()
except Exception as e:
    print(f"Erro ao inicializar listas_suspensas: {e}")
    logging.error(f"Erro ao inicializar as janelas: {e}")

# Configura o campo de senha para ocultar os caracteres
primeira_tela.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)                
       

# Ajustando para que as janelas se redimensionem corretamente
def configure_window(window):
    window.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
    # Verificar se a janela tem um layout; se não tiver, criar um layout padrão
    if window.layout() is None:
        layout = QVBoxLayout()
        window.setLayout(layout)
    
    window.layout().setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
    window.setMinimumSize(500, 500)  # Ajuste o tamanho mínimo se necessário

######################################################################################################################################
         
# Login e Cadastro no sistema para usuários comuns e administradores
def chama_segunda_tela():
    primeira_tela.label_6.setText("")
    nome_usuario = primeira_tela.lineEdit.text()
    senha = primeira_tela.lineEdit_2.text()

    # Verifica se é um administrador
    if (nome_usuario.lower() == 'jefferson' and senha == '123456') or (nome_usuario.lower() == 'valdeir' and senha == '123456'):
        login(nome_usuario)
        primeira_tela.close()
        segunda_tela.label_2.setText(nome_usuario)

        # Acesso como administrador
        for btn in [segunda_tela.btn_cadastrar]:
            btn.show()  # Mostra todos os botões

        segunda_tela.btn_cadastrar.setEnabled(True)  # Habilita o botão de cadastrar

        segunda_tela.show()
        start_timer()

    else:
        # Para usuários comuns, chamamos a função de autenticação
        user = authenticate_user(nome_usuario, senha)
        if user:
            login(nome_usuario)
            primeira_tela.close()
            segunda_tela.label_2.setText(nome_usuario)

            # Exibir todos os botões, mas desabilitar e alterar a cor
            '''for btn in [segunda_tela.btn_concursos, segunda_tela.btn_contato_profissionais, segunda_tela.btn_levantamento,
                        segunda_tela.btn_movimentacao_serv, segunda_tela.btn_movimentacao, segunda_tela.btn_mudanca_setor,
                        segunda_tela.btn_prof_desligados, segunda_tela.btn_prof_tratada, segunda_tela.btn_planilhas]:
                btn.show()
                btn.setEnabled(False)  # Desabilitar o botão
                btn.setStyleSheet("background-color: lightgray; color: darkgray;")  # Alterar a cor'''

            segunda_tela.btn_cadastrar.show()  # O botão de cadastrar fica visível e habilitado
            segunda_tela.btn_cadastrar.setEnabled(True)

            segunda_tela.show()
            start_timer()

        else:    

            # Cria uma caixa de mensagem para exibir o erro
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Dados de login incorretos!")
            msg.setInformativeText("Verifique os seguintes itens:\n"
                                "- Nome de usuário\n"
                                "- Senha (mínimo de 6 caracteres)")
            msg.setWindowTitle("Erro de Login")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()  # Exibe a caixa de mensagem

def start_timer():
    timer = QTimer(segunda_tela)
    timer.timeout.connect(update_time)
    timer.start(1000)

def update_time():
    current_date_time = QDateTime.currentDateTime()
    segunda_tela.label_3.setText(current_date_time.toString("dd/MM/yyyy HH:mm:ss"))

def logout():
    # Cria uma caixa de diálogo de mensagem de confirmação
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Sair do Sistema")
    msg_box.setText("Tem certeza que deseja sair do sistema e abandonar sua missão de gestão?")
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)

    # Mostra a caixa de diálogo e captura a resposta do usuário
    resposta = msg_box.exec_()

    if resposta == QMessageBox.Yes:
        segunda_tela.close()
        primeira_tela.show()
    else:
        pass  # O usuário escolheu "Não", então nada acontece

def abre_tela_cadastro():
    tela_cadastro.show()

# fora da função
janela_global = None

def abrir_planilhas():
    global janela_global
    janela_global = PlanilhasApp()
    janela_global.show()

def abre_listas_suspensas():
    global listas_suspensas
    listas_suspensas.show()

def cadastrar():
    nome = tela_cadastro.lineEdit.text()
    login = tela_cadastro.lineEdit_2.text()
    senha = tela_cadastro.lineEdit_3.text()
    c_senha = tela_cadastro.lineEdit_4.text()

    if not nome or not login or not senha or not c_senha:
        show_message_box("Campos obrigatórios", "Todos os campos são obrigatórios", QMessageBox.Warning)
        return

    if len(senha) < 6:
        show_message_box("Erro", "A senha deve ter pelo menos 6 caracteres", QMessageBox.Warning)
        return

    if senha == c_senha:
        if add_user(nome, login, senha):
            show_message_box("Sucesso", "Usuário cadastrado com sucesso")
        else:
            show_message_box("Erro", "Erro ao inserir os dados")
    else:
        show_message_box("Erro", "As senhas digitadas estão diferentes", QMessageBox.Warning)

# Variável global para armazenar o usuário logado
usuario_logado = None  # Inicialmente, nenhum usuário está logado

def login(usuario):
    global usuario_logado
    usuario_logado = usuario  # Armazena o login do usuário
    print(f"Usuário logado: {usuario_logado}")

def conectar_banco():
    if QSqlDatabase.contains("qt_sql_default_connection"):
        db = QSqlDatabase.database("qt_sql_default_connection")
    else:
        db = QSqlDatabase.addDatabase("QODBC")
        db.setDatabaseName("Driver={ODBC Driver 17 for SQL Server};Server=VALDEIR\SQLEXPRESS,1533;Database=autenticacao_compras;UID=fiocruz;PWD=fiocruz;")

    if not db.open():
        print("Erro ao conectar ao banco de dados:", db.lastError().text())
        return False
    return True

def salvar_alteracao_senha(model):
    """
    Função para salvar as alterações no banco de dados e exibir uma mensagem de sucesso.
    Faz a validação para garantir que a senha tenha no mínimo 6 caracteres.
    """
    for row in range(model.rowCount()):

        # Obtém o valor da coluna 'senha'
        senha = model.data(model.index(row, model.fieldIndex('senha')))
        
        # Valida o tamanho da senha
        if len(senha) < 6:
            QMessageBox.critical(None, "Erro", "A senha deve ter no mínimo 6 caracteres.")
            return  # Cancela o salvamento se a senha for inválida

    if model.submitAll():
        QMessageBox.information(None, "Sucesso", "Senha alterada com sucesso!")
    else:
        QMessageBox.critical(None, "Erro", f"Erro ao alterar a senha: {model.lastError().text()}")

def on_edit_finished(index, model):
    """
    Função para capturar o evento de finalização da edição da célula (por exemplo, quando pressionar Enter)
    e validar a senha.
    """
    if index.column() == model.fieldIndex('senha'):  # Se a coluna editada for 'senha'
        senha = model.data(index)

        # Valida o tamanho da senha
        if len(senha) < 6:
            QMessageBox.critical(None, "Erro", "A senha deve ter no mínimo 6 caracteres.")
            model.setData(index, "")  # Limpa o campo de senha inválida

def abre_tabela_cadastro():
    """
    Abre uma janela para o cadastro de usuários, permitindo que o usuário logado
    altere suas informações no banco de dados, especificamente a senha.
    A função se conecta ao banco de dados, filtra os dados do usuário logado, 
    exibe as informações em uma tabela e permite que o usuário edite a senha, 
    validando que ela tenha no mínimo 6 caracteres antes de salvar as alterações.
    """
    global usuario_logado
    
    if usuario_logado is None:
        print("Nenhum usuário logado.")
        return

    # Tente conectar ao banco de dados
    if not conectar_banco():
        print("Não foi possível conectar ao banco de dados.")
        return

    # Cria uma nova janela com o QTableView
    janela_tabela = QtWidgets.QDialog()
    janela_tabela.setWindowTitle("Alterar Senha - Cadastro de Usuários")
    
    # Layout para a nova janela
    layout = QtWidgets.QVBoxLayout()
    
    # Cria um modelo SQL e filtra os dados do usuário logado
    model = QSqlTableModel()
    model.setTable("cadastro")  # Nome da tabela no banco de dados
    
    # Filtra os dados para mostrar apenas o usuário logado
    model.setFilter(f"login = '{usuario_logado}'")  # Substitua 'login' pelo nome correto da coluna
    if not model.select():  # Popula o modelo com os dados filtrados
        print("Erro ao selecionar dados:", model.lastError().text())
    else:
        print(f"Número de registros encontrados: {model.rowCount()}")
    
    # Define a coluna 'id' como somente leitura
    model.setEditStrategy(QSqlTableModel.OnManualSubmit)
    table_view = QtWidgets.QTableView()
    table_view.setModel(model)

    # Oculta a coluna 'id' (supondo que 'id' seja a primeira coluna, índice 0)
    table_view.setColumnHidden(0, True)  # Altere o índice se a coluna 'id' estiver em outra posição

    # Torna a coluna 'id' somente leitura
    for row in range(model.rowCount()):
        index = model.index(row, 0)  # Supondo que a coluna 'id' é a primeira
        model.setData(index, model.data(index), Qt.ItemIsEditable)

    # Cria a tabela para exibir os dados
    table_view.setSortingEnabled(True)  # Permite ordenar clicando nos cabeçalhos
    table_view.resizeColumnsToContents()  # Ajusta o tamanho das colunas ao conteúdo
    table_view.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)  # Permite editar apenas ao clicar duas vezes

    def on_data_changed(topLeft):
        # Chame a função de validação passando o índice da célula editada
        on_edit_finished(topLeft, model)

    # Conecte o sinal de edição finalizada à função de validação
    table_view.model().dataChanged.connect(on_data_changed)
    
    # Adiciona a tabela ao layout
    layout.addWidget(table_view)

    # Cria o botão de salvar
    botao_salvar = QtWidgets.QPushButton("Salvar Alterações")
    botao_salvar.clicked.connect(lambda: salvar_alteracao_senha(model))  # Chama a função para salvar alterações
    layout.addWidget(botao_salvar)  # Adiciona o botão ao layout
    
    # Adiciona o layout à janela
    janela_tabela.setLayout(layout)
    
    # Exibe a janela
    janela_tabela.exec_()


# Eventos de clique
primeira_tela.pushButton.clicked.connect(chama_segunda_tela)
segunda_tela.btn_sair.clicked.connect(logout)
primeira_tela.btn_cadastre_se.clicked.connect(abre_tela_cadastro) # Botão cadastro para acessar o sistema
segunda_tela.btn_cadastrar.clicked.connect(abre_listas_suspensas) # Botão do formulário para cadastrar profissional
tela_cadastro.pushButton_cadastrar.clicked.connect(cadastrar) # Botão cadastro para acessar o sistema
segunda_tela.btn_alterar_senha.clicked.connect(abre_tabela_cadastro)
segunda_tela.btn_planilhas.clicked.connect(abrir_planilhas)

# Função principal
def main():
    try:
        testar_conexao()  # Testa a conexão
        primeira_tela.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Erro na execução principal: {e}")

if __name__ == "__main__":
    main()

    # Adicione a pausa para manter o terminal aberto
    input("Pressione qualquer tecla para sair...")