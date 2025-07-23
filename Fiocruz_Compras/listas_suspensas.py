from PyQt5.QtWidgets import QWidget, QTabWidget
from PyQt5.uic import loadUi  # Importa o método para carregar a interface a partir do .ui
import datetime
from utils import clear_fields_listas_suspensas, clear_fields_of_e_entregas, clear_fields_contratacao, clear_fields_participante, clear_fields_historico
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QLocale, QTimer
import pyodbc
from db_connection import get_pyodbc_connection
import os
import sys
import unicodedata

# Função para obter o caminho relativo no PyInstaller
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Remove acentos e normaliza o texto para comparação insensível a maiúsculas/minúsculas/acentos.
def normalize_text(text):
    if not text:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text.strip().lower())
        if not unicodedata.combining(c)
    )

class Listas_Suspensas(QWidget):
    def __init__(self):
        super(Listas_Suspensas, self).__init__()
        loadUi(resource_path('listas_suspensas.ui'), self)  # Carrega o arquivo .ui

        # Obtenha a conexão PyODBC do módulo centralizado
        self.conn = get_pyodbc_connection(log=False)
        if not self.conn:
            QtWidgets.QMessageBox.critical(self, "Erro", "Não foi possível conectar ao banco de dados.")
            return
        
        self.cursor = self.conn.cursor()

        # Acessa o QTabWidget e verifica as abas
        self.tabWidget_cadastrar = self.findChild(QTabWidget, 'tabWidget_cadastrar')
        if not self.tabWidget_cadastrar:
            print("QTabWidget 'tabWidget_cadastrar' não encontrado.")
            return

        # Verifica as abas
        self.aba_listas_suspensas = self.tabWidget_cadastrar.findChild(QWidget, 'aba_listas_suspensas')
        self.aba_of_e_entregas = self.tabWidget_cadastrar.findChild(QWidget, 'aba_of_e_entregas')
        self.aba_contratacao = self.tabWidget_cadastrar.findChild(QWidget, 'aba_contratacao')
        self.aba_participante = self.tabWidget_cadastrar.findChild(QWidget, 'aba_participante')

        if not self.aba_listas_suspensas or not self.aba_of_e_entregas or not self.aba_contratacao or not self.aba_participante:
            print("Erro ao encontrar abas.")

        self.carregar_profissionais() # Carrega o combobox com os profissionais ao iniciar
        self.comboBox_profissionais.currentIndexChanged.connect(self.carregar_tudo_para_profissional)
        self.setup_ui_pessoais()  # Preenche os ComboBox e LineEdit
        self.setup_connections()  # Configura as conexões dos botões

###############################################################################################################################################

    def buscar_por_nome(self):
        """Busca um registro no banco de dados pelo nome do comprador usando pyodbc."""
        nome = self.lineEdit_busca_nome.text()

        if nome:
            try:
                # Query SQL para busca
                query = """
                    SELECT ls.ID_Listas, ls.Nome_Agente_Contratacao, ls.Elemento_Despesa, ls.Requisitante,
                        ls.Licitacao_Tipo, ls.Situacao_ARP, ls.Situacao_item, ls.UASG_Gerenciadora, ls.Situacao_OF_e_NE,
                        ls.Ocorrencias_Licitacao, ls.Procedimento, ls.Inexigibilidade, ls.Situacao_Entrega,
                        ls.Situacao_IRP, ls.CNPJ, ls.Numero_Processo,
                        
                        ofe.ID_OF, ofe.Fornecedor_Vencedor, ofe.Valor_Solicitado, 
                        ofe.SEOR_Cogead_Envio, ofe.SEOR_Cogead_Retorno, ofe.Nota_Empenho, ofe.Valor_Empenhado, 
                        ofe.Data_Empenho, ofe.Data_Limite_Envio, ofe.Prazo_Entrega, 
                        ofe.Data_Limite_Entrega, ofe.Ultima_Verificacao, ofe.ID_Listas,

                        c.ID_Contratacao, c.DFD_do_SEI, c.Num_Contratacao, c.Data_Entrada_na_SMC, c.Item, c.Descricao_Item,
                        c.Codigo_Item, c.Quantidade, c.Objeto_Contratacao, c.Data_da_Portaria, c.Data_Email,
                        c.ETP_Data_Entrega, c.GR_Data_Entrega_Efetiva, c.TR_Data_Entrega_Efetiva,
                        c.RCO_Data_Entrega, c.Procuradoria_Federal, c.Pregao, c.Aviso_Licitacao,
                        c.Ocorrencias_Abertura_Licitacao, c.Data_Tributar, c.Gerenciamento_Contratacao, c.ID_Listas,

                        p.ID_Participante, p.Termo_Participacao, p.Num_Contratacao_PCA, 
                        p.Item_do_IRP, p.Descricao_Sucinta, p.Qtde_Item_Manifestado, 
                        p.Valor_Unitario_Estimado, p.Valor_Total_Estimado, 
                        p.Qtde_Aprovada_Gerenciador, p.Valor_Unitario_Homologado, 
                        p.Valor_Total_Homologado, p.Data_Abertura_Licitacao, p.Homologacao, 
                        p.Recurso, p.Fornecedor_Vencedor_Licitacao, p.Processo_Pagamento, p.ATA, 
                        p.Data_Inicio_Vigencia, p.Fim_Vigencia, p.OF_Ordem_Fornecimento, 
                        p.Qtde_Solicitada, p.Saldo, p.ID_Listas

                    FROM Listas_Suspensas ls
                    LEFT JOIN OF_e_Entregas ofe ON ls.ID_Listas = ofe.ID_Listas
                    LEFT JOIN Contratacao c ON ls.ID_Listas = c.ID_Listas
                    LEFT JOIN Participante p ON ls.ID_Listas = p.ID_Listas
                    WHERE ls.Nome_Agente_Contratacao LIKE ?
                """
                print(f"Executando query para nome: {nome}")

                # Executa a query com pyodbc
                self.cursor.execute(query, f"%{nome}%")
                result = self.cursor.fetchone()
                #print("[DEBUG] Resultado da busca:", result)

                if result:
                    # Preenche os campos da interface com os valores retornados
                    self.lineEdit_id_listas.setText(str(result[0]))  # ID_Listas
                    self.comboBox_nome_agente_contratacao.setCurrentText(str(result[1]))  # Nome_Agente_Contratacao                    
                    self.comboBox_elemento_despesa.setCurrentText(str(result[2]))  # Elemento_Despesa
                    self.comboBox_requisitante.setCurrentText(str(result[3]))  # Requisitante
                    self.comboBox_licitacao_tipo.setCurrentText(str(result[4]))  # Licitacao_Tipo
                    self.comboBox_situacao_arp.setCurrentText(str(result[5]))  # Situacao_ARP
                    self.comboBox_situacao_item.setCurrentText(str(result[6]))  # Situação_item
                    self.comboBox_uasg_gerenciadora.setCurrentText(str(result[7]))  # UASG_Gerenciadora
                    self.comboBox_situacao_OF_e_NE.setCurrentText(str(result[8]))  # Situacao_OF_e_NE
                    self.comboBox_ocorrencias_licitacao.setCurrentText(str(result[9]))  # Ocorrencias_Licitacao                    
                    self.comboBox_procedimento.setCurrentText(str(result[10]))  # Procedimento                    
                    self.comboBox_inexigibilidade.setCurrentText(str(result[11]))  # Inexigibilidade
                    self.comboBox_situacao_entrega.setCurrentText(str(result[12]))  # Situação_Entrega                
                    self.comboBox_situacao_irp.setCurrentText(str(result[13]))  # Situação_IRP  
                    self.lineEdit_cnpj_listas.setText(result[14] or "") # CNPJ
                    self.lineEdit_numero_processo_listas.setText(result[15] or "") # Numero_Processo

                    # Preencher campos da tabela OF_e_Entregas
                    self.lineEdit_id_of.setText(str(result[16]) if result[16] else "")                  
                    self.lineEdit_fornecedor.setText(result[17] or "")

                    self.lineEdit_valor_solicitado.setText(
                    f"{result[18]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if result[18] else "")

                    self.lineEdit_seor_envio.setText(result[19].strftime("%d/%m/%Y") if result[19] else "")
                    self.lineEdit_seor_retorno.setText(result[20].strftime("%d/%m/%Y") if result[20] else "")

                    nota_empenho = result[21] if result[21] is not None else ""

                    if "NE" in nota_empenho:
                        partes = nota_empenho.split("NE")
                        self.lineEdit_nota_empenho_inicio.setText(partes[0])
                        self.lineEdit_nota_empenho_fim.setText(partes[1])
                    else:
                        self.lineEdit_nota_empenho_inicio.setText("")
                        self.lineEdit_nota_empenho_fim.setText("")

                    self.lineEdit_valor_empenhado.setText(
                    f"{result[22]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if result[22] else "")

                    self.lineEdit_data_empenho.setText(result[23].strftime("%d/%m/%Y") if result[23] else "")                    
                    self.lineEdit_data_limite_envio.setText(result[24].strftime("%d/%m/%Y") if result[24] else "")

                    prazo = ''.join(filter(str.isdigit, str(result[25]) if result[25] else ""))
                    self.lineEdit_prazo_entrega.setText(f"{prazo} dias" if prazo else "")

                    self.lineEdit_data_limite_entrega.setText(result[26].strftime("%d/%m/%Y") if result[26] else "")                   
                    self.lineEdit_ultima_verificacao.setText(result[27].strftime("%d/%m/%Y") if result[27] else "")
                    self.lineEdit_id_listas_of.setText(str(result[28]) if result[28] else "")

                    # --- Preenchimento Contratacao ---
                    self.lineEdit_id_contratacao.setText(str(result[29]) if result[29] else "")                    
                    self.comboBox_dfd_sei.setCurrentText(str(result[30]))
                    self.lineEdit_num_contratacao_pca.setText(str(result[31]))
                    self.lineEdit_data_entrada_smc.setText(result[32].strftime("%d/%m/%Y") if result[32] else "")
                    self.lineEdit_item.setText(str(result[33]))
                    self.lineEdit_descricao_item.setText(str(result[34]))
                    self.comboBox_codigo_item.setCurrentText(str(result[35]))
                    self.lineEdit_qtde_solicitada.setText(str(result[36]))
                    self.lineEdit_objeto_contratacao.setText(str(result[37]))
                    self.lineEdit_data_portaria.setText(result[38].strftime("%d/%m/%Y") if result[38] else "")
                    self.lineEdit_data_email.setText(result[39].strftime("%d/%m/%Y") if result[39] else "")
                    self.lineEdit_etp_data_entrega.setText(result[40].strftime("%d/%m/%Y") if result[40] else "")
                    self.lineEdit_gr_data_entrega_efetiva.setText(result[41].strftime("%d/%m/%Y") if result[41] else "")
                    self.lineEdit_tr_data_entrega_efetiva.setText(result[42].strftime("%d/%m/%Y") if result[42] else "")
                    self.comboBox_rco.setCurrentText(str(result[43]))
                    self.comboBox_procuradoria_federal.setCurrentText(str(result[44]))
                    self.lineEdit_pregao.setText(str(result[45]))
                    self.lineEdit_aviso_licitacao.setText(str(result[46]))
                    self.comboBox_ocorrencias_abertura.setCurrentText(str(result[47]))
                    self.lineEdit_data_tributar.setText(result[48].strftime("%d/%m/%Y") if result[48] else "")
                    self.comboBox_gerenciamento_contratacao.setCurrentText(str(result[49]))
                    self.lineEdit_id_listas_contratacao.setText(str(result[50]) if result[50] else "")

                    # --- Preenchimento Participante ---
                    self.lineEdit_id_participante.setText(str(result[51]) if result[51] else "")                    
                    self.comboBox_termo_participacao.setCurrentText(result[52] or "")
                    self.lineEdit_num_contratacao_pca_part.setText(result[53] or "")
                    
                    self.lineEdit_item_irp.setText(str(result[54]) if result[54] is not None else "")
                    self.lineEdit_descricao_sucinta.setText(result[55] or "")
                    self.lineEdit_qtde_item_manifestado.setText(str(result[56]) if result[56] else "")
                    
                    # Valores monetários
                    self.lineEdit_valor_unitario_estimado.setText(
                        f"{result[57]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if result[57] else ""
                    )
                    self.lineEdit_valor_total_estimado.setText(
                        f"{result[58]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if result[58] else ""
                    )

                    self.lineEdit_qtde_aprovada_gerenciador.setText(str(result[59]) if result[59] else "")
                    self.lineEdit_valor_unitario_homologado.setText(
                        f"{result[60]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if result[60] else ""
                    )
                    self.lineEdit_valor_total_homologado.setText(
                        f"{result[61]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if result[61] else ""
                    )
                    
                    self.lineEdit_data_abertura_licitacao.setText(result[62].strftime("%d/%m/%Y") if result[62] else "")
                    self.comboBox_homologacao.setCurrentText(result[63] or "")
                    self.comboBox_recurso.setCurrentText(result[64] or "")
                    self.lineEdit_fornecedor_vencedor.setText(result[65] or "")
                    self.lineEdit_processo_pagamento.setText(result[66] or "")
                    self.lineEdit_ata.setText(result[67] or "")
                    self.lineEdit_data_inicio_vigencia.setText(result[68].strftime("%d/%m/%Y") if result[68] else "")
                    self.lineEdit_fim_vigencia.setText(result[69] or "")
                    self.lineEdit_of_ordem_fornecimento.setText(result[70] or "")
                    self.lineEdit_qtde_solicitada_part.setText(str(result[71]) if result[71] else "")
                    self.lineEdit_saldo.setText(str(result[72]) if result[72] else "")
                    self.lineEdit_id_listas_part.setText(str(result[73]) if result[73] else "")
                    
                else:
                    QtWidgets.QMessageBox.warning(self, "Aviso", "Nenhum resultado encontrado.")
            except pyodbc.Error as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao buscar o nome: {e}")

###############################################################################################################################################

    def cadastrar_dados_completos(self):
        """Insere um novo registro no banco de dados."""
        try:            
            # Exibir a caixa de diálogo de confirmação
            resposta = QtWidgets.QMessageBox.question(
                self,
                "Confirmação",
                "Você deseja realmente cadastrar este registro?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            # Se o usuário clicar em "Sim", prossegue com o cadastro
            if resposta == QtWidgets.QMessageBox.No:
                return
            
            # ---- 1. Inserção em Listas_Suspensas ----
            query_listas_suspensas = """
                INSERT INTO Listas_Suspensas (
                    Nome_Agente_Contratacao, Elemento_Despesa, Requisitante,
                    Licitacao_Tipo, Situacao_ARP, Situacao_item, UASG_Gerenciadora, Situacao_OF_e_NE,
                    Ocorrencias_Licitacao, Procedimento, Inexigibilidade, Situacao_Entrega,
                    Situacao_IRP, CNPJ, Numero_Processo
                ) 
                OUTPUT INSERTED.ID_Listas
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Obtenção dos valores dos ComboBox
            valores_listas_suspensas = (
                self.comboBox_nome_agente_contratacao.currentText().strip(),                
                self.comboBox_elemento_despesa.currentText().strip(),
                self.comboBox_requisitante.currentText().strip(),
                self.comboBox_licitacao_tipo.currentText().strip(),
                self.comboBox_situacao_arp.currentText().strip(),
                self.comboBox_situacao_item.currentText().strip(),
                self.comboBox_uasg_gerenciadora.currentText().strip(),
                self.comboBox_situacao_OF_e_NE.currentText().strip(),
                self.comboBox_ocorrencias_licitacao.currentText().strip(),                    
                self.comboBox_procedimento.currentText().strip(),                   
                self.comboBox_inexigibilidade.currentText().strip(),
                self.comboBox_situacao_entrega.currentText().strip(),                                       
                self.comboBox_situacao_irp.currentText(),   
                self.lineEdit_cnpj_listas.text().strip().replace(".", "").replace("/", "").replace("-", ""), 
                self.lineEdit_numero_processo_listas.text().strip().replace(".", "").replace("/", "").replace("-", ""),
            )

            self.cursor.execute(query_listas_suspensas, valores_listas_suspensas)
            id_listas = self.cursor.fetchone()[0]          

            if not id_listas:
                print("[ERRO] Não foi possível obter o ID_Listas.")
                QtWidgets.QMessageBox.critical(self, "Erro", "Falha ao obter o ID da Lista Suspensa.")
                return
            else:
                '''print(f"[DEBUG] ID_Listas recuperado: {id_listas}")'''

            # ---- 2. Inserção em OF_e_Entregas ----
            query_of_entregas = """
                INSERT INTO OF_e_Entregas (
                    Fornecedor_Vencedor, Valor_Solicitado, SEOR_Cogead_Envio, SEOR_Cogead_Retorno, Nota_Empenho, 
                    Valor_Empenhado, Data_Empenho, Data_Limite_Envio, Prazo_Entrega, Data_Limite_Entrega,
                    Ultima_Verificacao, ID_Listas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            valores_of_entregas = (              
                self.lineEdit_fornecedor.text().strip(),
                self.extrair_valor_float(self.lineEdit_valor_solicitado),
                self.converter_data(self.lineEdit_seor_envio.text()),
                self.converter_data(self.lineEdit_seor_retorno.text()),
                self.lineEdit_nota_empenho_inicio.text() + "NE" + self.lineEdit_nota_empenho_fim.text(),
                self.extrair_valor_float(self.lineEdit_valor_empenhado),
                self.converter_data(self.lineEdit_data_empenho.text()),
                self.converter_data(self.lineEdit_data_limite_envio.text()),    # Campo de data
                ''.join(filter(str.isdigit, self.lineEdit_prazo_entrega.text())),  # Pega só o número para salvar
                self.converter_data(self.lineEdit_data_limite_entrega.text()),  # Campo de data             
                self.converter_data(self.lineEdit_ultima_verificacao.text()), # Campo de data
                id_listas  # Aqui vai a chave estrangeira
            )
            # Executa a segunda query
            #print("[DEBUG] Dados OF_e_Entregas:")
            for i, valor in enumerate(valores_of_entregas):
                print(f"Campo {i+1}: {repr(valor)}")

            self.cursor.execute(query_of_entregas, valores_of_entregas)

            # ---- 3. Inserção em Contratacao ----
            query_contratacao = """
                INSERT INTO Contratacao (
                    DFD_do_SEI, Num_Contratacao, Data_Entrada_na_SMC, Item, Descricao_Item,
                    Codigo_Item, Quantidade, Objeto_Contratacao, Data_da_Portaria,
                    Data_Email, ETP_Data_Entrega, GR_Data_Entrega_Efetiva, TR_Data_Entrega_Efetiva,
                    RCO_Data_Entrega, Procuradoria_Federal, Pregao, Aviso_Licitacao,
                    Ocorrencias_Abertura_Licitacao, Data_Tributar, Gerenciamento_Contratacao,
                    ID_Listas
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            valores_contratacao = (
                self.comboBox_dfd_sei.currentText().strip(),  # Correto / Incorreto
                self.lineEdit_num_contratacao_pca.text().strip().replace(".", "").replace("/", ""),
                self.converter_data(self.lineEdit_data_entrada_smc.text()),
                self.lineEdit_item.text().strip(),
                self.lineEdit_descricao_item.text().strip(),
                self.comboBox_codigo_item.currentText().strip(),  # CATSER / CATMAT
                ''.join(filter(str.isdigit, self.lineEdit_qtde_solicitada.text())), 
                self.lineEdit_objeto_contratacao.text().strip(),
                self.converter_data(self.lineEdit_data_portaria.text()),
                self.converter_data(self.lineEdit_data_email.text()),
                self.converter_data(self.lineEdit_etp_data_entrega.text()),
                self.converter_data(self.lineEdit_gr_data_entrega_efetiva.text()),
                self.converter_data(self.lineEdit_tr_data_entrega_efetiva.text()),
                self.comboBox_rco.currentText().strip(),
                self.comboBox_procuradoria_federal.currentText().strip(),
                self.lineEdit_pregao.text().strip().replace(".", "").replace("/", ""),
                self.lineEdit_aviso_licitacao.text().strip().replace(".", "").replace("/", "").replace("-", ""), 
                self.comboBox_ocorrencias_abertura.currentText().strip(),
                self.converter_data(self.lineEdit_data_tributar.text()),
                self.comboBox_gerenciamento_contratacao.currentText().strip(),
                id_listas
            )

            #print("[DEBUG] Dados Contratacao:")
            for i, valor in enumerate(valores_contratacao):
                print(f"Campo {i+1}: {repr(valor)}")

            self.cursor.execute(query_contratacao, valores_contratacao)

            # ---- 4. Inserção em Participante ----
            query_participante = """
                INSERT INTO Participante (
                Termo_Participacao, Num_Contratacao_PCA, 
                Item_do_IRP, Descricao_Sucinta, Qtde_Item_Manifestado, 
                Valor_Unitario_Estimado, Valor_Total_Estimado, Qtde_Aprovada_Gerenciador, 
                Valor_Unitario_Homologado, Valor_Total_Homologado, Data_Abertura_Licitacao, 
                Homologacao, Recurso, Fornecedor_Vencedor_Licitacao, Processo_Pagamento, ATA, 
                Data_Inicio_Vigencia, Fim_Vigencia, OF_Ordem_Fornecimento, Qtde_Solicitada, Saldo, ID_Listas
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Validação e conversão da Qtde Aprovada
            texto_qtde_aprovada = self.lineEdit_qtde_aprovada_gerenciador.text()
            qtde_aprovada_str = ''.join(filter(str.isdigit, texto_qtde_aprovada))

            if not qtde_aprovada_str:
                QtWidgets.QMessageBox.warning(self, "Erro", "O campo 'Qtde Aprovada Gerenciador' está vazio ou inválido.")
                return

            qtde_aprovada = int(qtde_aprovada_str)

            # Validação e conversão da Qtde Solicitada
            texto_qtde_solicitada = self.lineEdit_qtde_solicitada_part.text()
            qtde_solicitada_str = ''.join(filter(str.isdigit, texto_qtde_solicitada))

            if not qtde_solicitada_str:
                QtWidgets.QMessageBox.warning(self, "Erro", "O campo 'Qtde Solicitada' está vazio ou inválido.")
                return

            qtde_solicitada = int(qtde_solicitada_str)

            # Agora calcula o saldo
            saldo = qtde_aprovada - qtde_solicitada

            # Atualiza o campo saldo na interface se quiser ver o resultado na hora
            self.lineEdit_saldo.setText(str(saldo))

            valores_participante = (
                self.comboBox_termo_participacao.currentText().strip(),
                self.lineEdit_num_contratacao_pca_part.text().strip().replace(".", "").replace("/", ""),
                self.lineEdit_item_irp.text().strip(),
                self.lineEdit_descricao_sucinta.text().strip(),
                self.lineEdit_qtde_item_manifestado.text().strip(),
                self.extrair_valor_float(self.lineEdit_valor_unitario_estimado),
                self.extrair_valor_float(self.lineEdit_valor_total_estimado),
                qtde_aprovada,  # valor já como int
                self.extrair_valor_float(self.lineEdit_valor_unitario_homologado),
                self.extrair_valor_float(self.lineEdit_valor_total_homologado),
                self.converter_data(self.lineEdit_data_abertura_licitacao.text()),
                self.comboBox_homologacao.currentText().strip(),
                self.comboBox_recurso.currentText().strip(),
                self.lineEdit_fornecedor_vencedor.text().strip(),
                self.lineEdit_processo_pagamento.text().strip(),
                self.lineEdit_ata.text().strip(),
                self.converter_data(self.lineEdit_data_inicio_vigencia.text()),
                ''.join(filter(str.isdigit, self.lineEdit_fim_vigencia.text())),
                self.lineEdit_of_ordem_fornecimento.text().strip().replace(".", "").replace("/", ""),
                qtde_solicitada,
                saldo,
                id_listas
            )

            #print("[DEBUG] Dados Participante:")
            for i, valor in enumerate(valores_participante):
                print(f"Campo {i+1}: {repr(valor)}")

            self.cursor.execute(query_participante, valores_participante)          

            self.conn.commit()
            self.carregar_profissionais()

            QtWidgets.QMessageBox.information(self, "Sucesso", "Registro cadastrado com sucesso!")
            clear_fields_listas_suspensas(self)
            clear_fields_of_e_entregas(self)
            clear_fields_contratacao(self)
            clear_fields_participante(self)
            clear_fields_historico(self)
    
        except pyodbc.Error as e:
            self.conn.rollback()
            print(f"[ERRO SQL detalhado] {e.args}")
            QtWidgets.QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao cadastrar: {e}")

        # Função para calcular valores da tabela de Participante
    def calcular_saldo(self):
        try:
            locale = QLocale(QLocale.Portuguese)

            texto_aprovado = self.lineEdit_qtde_aprovada_gerenciador.text().strip()
            texto_solicitado = self.lineEdit_qtde_solicitada_part.text().strip()

            # Limpa e converte para float com sinal (considerando vírgula decimal)
            valor_aprovado, ok1 = locale.toDouble(texto_aprovado)
            valor_solicitado, ok2 = locale.toDouble(texto_solicitado)

            # Se não conseguir converter, coloca 0
            if not ok1:
                valor_aprovado = 0.0
            if not ok2:
                valor_solicitado = 0.0

            saldo = valor_aprovado - valor_solicitado

            # Mostra saldo negativo corretamente (ex: -1,00)
            self.lineEdit_saldo.setText(locale.toString(saldo, 'f', 2))
        except Exception as e:
            print(f"[ERRO calcular_saldo]: {e}")
            self.lineEdit_saldo.setText("0,00")
   

###############################################################################################################################################

    def salvar_dados_completos(self):
        """Atualiza um registro existente no banco de dados usando pyodbc."""
            
            # Exibir a caixa de diálogo de confirmação
        resposta = QtWidgets.QMessageBox.question(
            self,
            "Confirmação",
            "Você deseja realmente salvar as alterações?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        # Se o usuário clicar em "Yes", prossegue com o salvamento
        if resposta == QtWidgets.QMessageBox.Yes:
            
            try:
                self.conn.autocommit = False

                # -------- Atualizar Listas_Suspensas --------
                query = """
                    UPDATE Listas_Suspensas SET
                        Nome_Agente_Contratacao = ?,                        
                        Elemento_Despesa = ?,
                        Requisitante = ?,
                        Licitacao_Tipo = ?,
                        Situacao_ARP = ?,
                        Situacao_item = ?,
                        UASG_Gerenciadora = ?,
                        Situacao_OF_e_NE = ?,
                        Ocorrencias_Licitacao = ?,                       
                        Procedimento = ?,                        
                        Inexigibilidade = ?,
                        Situacao_Entrega = ?,                                                
                        Situacao_IRP = ?,  
                        CNPJ = ?,
                        Numero_Processo = ?               
                    WHERE ID_Listas = ?
                """
            
                # Parâmetros da query
                params_listas = (
                    self.comboBox_nome_agente_contratacao.currentText(),                    
                    self.comboBox_elemento_despesa.currentText(),
                    self.comboBox_requisitante.currentText(),
                    self.comboBox_licitacao_tipo.currentText(),
                    self.comboBox_situacao_arp.currentText(),
                    self.comboBox_situacao_item.currentText(),
                    self.comboBox_uasg_gerenciadora.currentText(),
                    self.comboBox_situacao_OF_e_NE.currentText(),
                    self.comboBox_ocorrencias_licitacao.currentText(),                    
                    self.comboBox_procedimento.currentText(),                    
                    self.comboBox_inexigibilidade.currentText(),
                    self.comboBox_situacao_entrega.currentText(),                            
                    self.comboBox_situacao_irp.currentText(),   
                    self.lineEdit_cnpj_listas.text(),
                    self.lineEdit_numero_processo_listas.text(),                                   
                    self.lineEdit_id_listas.text()  # ID_Listas (condição do WHERE)
                )

                # Executa a query usando o cursor do pyodbc
                self.cursor.execute(query, params_listas)

                # Pegando o ID_Listas para usar no OF_e_Entregas
                id_listas = self.lineEdit_id_listas.text()
                self.lineEdit_id_listas_of.setText(str(id_listas))  # Preenche o campo automaticamente

                print("ID_Listas usado na OF_e_Entregas:", id_listas)

                # -------- Atualizar OF_e_Entregas --------
                query_of = """
                    UPDATE OF_e_Entregas SET
                        Fornecedor_Vencedor = ?,
                        Valor_Solicitado = ?,
                        SEOR_Cogead_Envio = ?,
                        SEOR_Cogead_Retorno = ?,
                        Nota_Empenho = ?,
                        Valor_Empenhado = ?,
                        Data_Empenho = ?,
                        Data_Limite_Envio = ?,
                        Prazo_Entrega = ?,
                        Data_Limite_Entrega = ?,
                        Ultima_Verificacao = ?,
                        ID_Listas = ?
                    WHERE ID_OF = ?
                """
                
                params_of = (
                    self.lineEdit_fornecedor.text(),
                    self.extrair_valor_float(self.lineEdit_valor_solicitado),
                    self.converter_data(self.lineEdit_seor_envio.text()),         # SEOR_Cogead_Envio
                    self.converter_data(self.lineEdit_seor_retorno.text()),       # SEOR_Cogead_Retorno
                    self.lineEdit_nota_empenho_inicio.text() + "NE" + self.lineEdit_nota_empenho_fim.text(),
                    self.extrair_valor_float(self.lineEdit_valor_empenhado),
                    self.converter_data(self.lineEdit_data_empenho.text()),                   
                    self.converter_data(self.lineEdit_data_limite_envio.text()),
                    ''.join(filter(str.isdigit, self.lineEdit_prazo_entrega.text())),
                    self.converter_data(self.lineEdit_data_limite_entrega.text()),                    
                    self.converter_data(self.lineEdit_ultima_verificacao.text()),
                    self.lineEdit_id_listas_of.text(),  # <- ID_Listas FK
                    self.lineEdit_id_of.text()
                )
                self.cursor.execute(query_of, params_of)

                # -------- Atualizar Contratação --------
                query = """
                    UPDATE Contratacao SET
                        DFD_do_SEI = ?,
                        Num_Contratacao = ?,
                        Data_Entrada_na_SMC = ?,
                        Item = ?,
                        Descricao_Item = ?,
                        Codigo_Item = ?,
                        Quantidade = ?,
                        Objeto_Contratacao = ?,
                        Data_da_Portaria = ?,
                        Data_Email = ?,
                        ETP_Data_Entrega = ?,
                        GR_Data_Entrega_Efetiva = ?,
                        TR_Data_Entrega_Efetiva = ?,
                        RCO_Data_Entrega = ?,
                        Procuradoria_Federal = ?,
                        Pregao = ?,
                        Aviso_Licitacao = ?,
                        Ocorrencias_Abertura_Licitacao = ?,
                        Data_Tributar = ?,
                        Gerenciamento_Contratacao = ?,
                        ID_Listas = ?
                    WHERE ID_Contratacao = ?
                """

                params_contratacao = (
                    self.comboBox_dfd_sei.currentText(), # Correto / Incorreto
                    self.lineEdit_num_contratacao_pca.text().strip().replace(".", "").replace("/", ""),
                    self.converter_data(self.lineEdit_data_entrada_smc.text()),
                    self.lineEdit_item.text().strip(),
                    self.lineEdit_descricao_item.text().strip(),
                    self.comboBox_codigo_item.currentText(), # CATSER / CATMAT
                    ''.join(filter(str.isdigit, self.lineEdit_qtde_solicitada.text())),
                    self.lineEdit_objeto_contratacao.text().strip(),
                    self.converter_data(self.lineEdit_data_portaria.text()),
                    self.converter_data(self.lineEdit_data_email.text()), 
                    self.converter_data(self.lineEdit_etp_data_entrega.text()),
                    self.converter_data(self.lineEdit_gr_data_entrega_efetiva.text()),
                    self.converter_data(self.lineEdit_tr_data_entrega_efetiva.text()),
                    self.comboBox_rco.currentText(),  # Sim / Não
                    self.comboBox_procuradoria_federal.currentText(), # Sim / Não
                    self.lineEdit_pregao.text().replace(".", "").replace("/", ""),
                    self.lineEdit_aviso_licitacao.text().strip().replace(".", "").replace("/", "").replace("-", ""), 
                    self.comboBox_ocorrencias_abertura.currentText(),
                    self.converter_data(self.lineEdit_data_tributar.text()),
                    self.comboBox_gerenciamento_contratacao.currentText(),
                    self.lineEdit_id_listas_contratacao.text(),  # ID_Listas (FK)
                    self.lineEdit_id_contratacao.text()
                )
                # Executar o UPDATE na tabela Contratacao
                self.cursor.execute(query, params_contratacao)

                # -------- Atualizar Participante --------
                query = """
                    UPDATE Participante SET
                        Termo_Participacao = ?,
                        Num_Contratacao_PCA = ?,
                        Item_do_IRP = ?,
                        Descricao_Sucinta = ?,
                        Qtde_Item_Manifestado = ?,
                        Valor_Unitario_Estimado = ?,
                        Valor_Total_Estimado = ?,
                        Qtde_Aprovada_Gerenciador = ?,
                        Valor_Unitario_Homologado = ?,
                        Valor_Total_Homologado = ?,
                        Data_Abertura_Licitacao = ?,
                        Homologacao = ?,
                        Recurso = ?,
                        Fornecedor_Vencedor_Licitacao = ?,
                        Processo_Pagamento = ?,
                        ATA = ?,
                        Data_Inicio_Vigencia = ?,
                        Fim_Vigencia = ?,
                        OF_Ordem_Fornecimento = ?,
                        Qtde_Solicitada = ?,
                        Saldo = ?,
                        ID_Listas = ?
                    WHERE ID_Participante = ?
                """

                # Captura as quantidades como inteiros
                qtde_aprovada = int(''.join(filter(str.isdigit, self.lineEdit_qtde_aprovada_gerenciador.text())))
                qtde_solicitada = int(''.join(filter(str.isdigit, self.lineEdit_qtde_solicitada_part.text())))

                # Calcula o saldo
                saldo = qtde_aprovada - qtde_solicitada

                params_participante = (
                    self.comboBox_termo_participacao.currentText(),
                    self.lineEdit_num_contratacao_pca_part.text().strip().replace(".", "").replace("/", ""),
                    self.lineEdit_item_irp.text().strip(),
                    self.lineEdit_descricao_sucinta.text().strip(),
                    self.lineEdit_qtde_item_manifestado.text().strip(),
                    self.extrair_valor_float(self.lineEdit_valor_unitario_estimado),
                    self.extrair_valor_float(self.lineEdit_valor_total_estimado),
                    qtde_aprovada,
                    self.extrair_valor_float(self.lineEdit_valor_unitario_homologado),
                    self.extrair_valor_float(self.lineEdit_valor_total_homologado),
                    self.converter_data(self.lineEdit_data_abertura_licitacao.text()), ######
                    self.comboBox_homologacao.currentText(),
                    self.comboBox_recurso.currentText(),
                    self.lineEdit_fornecedor_vencedor.text().strip(),
                    self.lineEdit_processo_pagamento.text().strip(),
                    self.lineEdit_ata.text().strip(),
                    self.converter_data(self.lineEdit_data_inicio_vigencia.text()),
                    ''.join(filter(str.isdigit, self.lineEdit_fim_vigencia.text())),  
                    self.lineEdit_of_ordem_fornecimento.text().strip().replace(".", "").replace("/", ""),
                    qtde_solicitada,
                    saldo,
                    self.lineEdit_id_listas_part.text(),  # ID_Listas (FK)
                    self.lineEdit_id_participante.text()
                )

                self.cursor.execute(query, params_participante)
    
                # Confirma a transação
                self.conn.commit()
                self.conn.autocommit = True  # Reativa autocommit após o commit
                
                # Exibe mensagem de sucesso
                QtWidgets.QMessageBox.information(self, "Sucesso", "Registro atualizado com sucesso!")
                clear_fields_listas_suspensas(self)
                clear_fields_of_e_entregas(self)
                clear_fields_contratacao(self)
                clear_fields_participante(self)
                clear_fields_historico(self)

            except pyodbc.Error as e:
                self.conn.rollback()  # Reverte a transação se houver erro
                self.conn.autocommit = True
                QtWidgets.QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao salvar: {e}")

###############################################################################################################################################

    def salvar_historico(self):
        """Salva os dados atuais como um novo registro no histórico."""

        # Confirmação do usuário
        resposta = QtWidgets.QMessageBox.question(
            self,
            "Confirmação",
            "Deseja salvar os dados atuais como histórico?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if resposta != QtWidgets.QMessageBox.Yes:
            return

        try:
            # Obtém o ID do profissional selecionado
            id_listas = self.comboBox_profissionais.currentData()

            if not id_listas:
                QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um profissional para salvar o histórico.")
                return

            # >>> BUSCA o ID_OF correspondente ao ID_Listas selecionado <<<
            cursor = self.conn.cursor()

            # Busca o último histórico completo do profissional
            cursor.execute("SELECT TOP 1 * FROM Historico WHERE ID_Listas = ? ORDER BY ID_Historico DESC", (id_listas,))
            last_historico = cursor.fetchone()
            dados_anteriores = list(last_historico) if last_historico else [None] * 72

            def val_or_old(valor_atual, index):
                """Retorna o valor atual SOMENTE se for diferente do anterior, senão retorna o valor anterior."""
                anterior = dados_anteriores[index]
                
                if isinstance(valor_atual, str):
                    return valor_atual.strip() if valor_atual.strip() != str(anterior).strip() else anterior
                
                elif isinstance(valor_atual, (int, float)):
                    return valor_atual if valor_atual != anterior else anterior

                elif isinstance(valor_atual, QtCore.QDate):  # Caso esteja usando datas do tipo QDate
                    return valor_atual if valor_atual != anterior else anterior
                
                return valor_atual or anterior

        
            cursor.execute("SELECT ID_OF FROM OF_e_Entregas WHERE ID_Listas = ?", (id_listas,))
            resultado = cursor.fetchone()
            if not resultado:
                QtWidgets.QMessageBox.warning(self, "Aviso", "Nenhuma informação de OF encontrada para este profissional.")
                return
            id_of = resultado[0]

            # >>> BUSCA o ID_Contratacao correspondente ao ID_Listas selecionado <<<
            cursor.execute("SELECT ID_Contratacao FROM Contratacao WHERE ID_Listas = ?", (id_listas,))
            resultado_contratacao = cursor.fetchone()
            if not resultado_contratacao:
                QtWidgets.QMessageBox.warning(self, "Aviso", "Nenhuma informação de contratação encontrada para este profissional.")
                return
            id_contratacao = resultado_contratacao[0]

            # >>> BUSCA o ID_Participante correspondente ao ID_Listas selecionado <<<
            cursor.execute("SELECT ID_Participante FROM Participante WHERE ID_Listas = ?", (id_listas,))
            resultado_participante = cursor.fetchone()
            if not resultado_participante:
                QtWidgets.QMessageBox.warning(self, "Aviso", "Nenhuma informação de contratação encontrada para este profissional.")
                return
            id_participante = resultado_participante[0]

            # >>> Prepara os dados para inserção no histórico de Participante <<<
            qtde_aprovada = int(''.join(filter(str.isdigit, self.lineEdit_qtde_aprovada_gerenciador.text())))
            qtde_solicitada = int(''.join(filter(str.isdigit, self.lineEdit_qtde_solicitada_part.text())))
            saldo = qtde_aprovada - qtde_solicitada


            # Coleta os dados da tela atual (mesmos campos da aba de cadastro)
            params_historico = (
                id_listas,  # 0
                val_or_old(self.comboBox_nome_agente_contratacao.currentText(), 1),
                val_or_old(self.comboBox_elemento_despesa.currentText(), 2),
                val_or_old(self.comboBox_requisitante.currentText(), 3),
                val_or_old(self.comboBox_licitacao_tipo.currentText(), 4),
                val_or_old(self.comboBox_situacao_arp.currentText(), 5),
                val_or_old(self.comboBox_situacao_item.currentText(), 6),
                val_or_old(self.comboBox_uasg_gerenciadora.currentText(), 7),
                val_or_old(self.comboBox_situacao_OF_e_NE.currentText(), 8),
                val_or_old(self.comboBox_ocorrencias_licitacao.currentText(), 9),
                val_or_old(self.comboBox_procedimento.currentText(), 10),
                val_or_old(self.comboBox_inexigibilidade.currentText(), 11),
                val_or_old(self.comboBox_situacao_entrega.currentText(), 12),
                val_or_old(self.comboBox_situacao_irp.currentText(), 13),
                val_or_old(self.lineEdit_cnpj_listas.text(), 14),
                val_or_old(self.lineEdit_numero_processo_listas.text(), 15),

                id_of,  # 16
                val_or_old(self.lineEdit_fornecedor.text(), 17),
                val_or_old(self.extrair_valor_float(self.lineEdit_valor_solicitado), 18),
                val_or_old(self.converter_data(self.lineEdit_seor_envio.text()), 19),
                val_or_old(self.converter_data(self.lineEdit_seor_retorno.text()), 20),
                val_or_old(self.lineEdit_nota_empenho_inicio.text() + "NE" + self.lineEdit_nota_empenho_fim.text(), 21),
                val_or_old(self.extrair_valor_float(self.lineEdit_valor_empenhado), 22),
                val_or_old(self.converter_data(self.lineEdit_data_empenho.text()), 23),
                val_or_old(self.converter_data(self.lineEdit_data_limite_envio.text()), 24),
                val_or_old(''.join(filter(str.isdigit, self.lineEdit_prazo_entrega.text())), 25),
                val_or_old(self.converter_data(self.lineEdit_data_limite_entrega.text()), 26),
                val_or_old(self.converter_data(self.lineEdit_ultima_verificacao.text()), 27),

                id_contratacao,  # 28
                val_or_old(self.comboBox_dfd_sei.currentText(), 29),
                val_or_old(self.lineEdit_num_contratacao_pca.text().strip().replace(".", "").replace("/", ""), 30),
                val_or_old(self.converter_data(self.lineEdit_data_entrada_smc.text()), 31),
                val_or_old(self.lineEdit_item.text().strip(), 32),
                val_or_old(self.lineEdit_descricao_item.text().strip(), 33),
                val_or_old(self.comboBox_codigo_item.currentText(), 34),
                val_or_old(''.join(filter(str.isdigit, self.lineEdit_qtde_solicitada.text())), 35),
                val_or_old(self.lineEdit_objeto_contratacao.text().strip(), 36),
                val_or_old(self.converter_data(self.lineEdit_data_portaria.text()), 37),
                val_or_old(self.converter_data(self.lineEdit_data_email.text()), 38),
                val_or_old(self.converter_data(self.lineEdit_etp_data_entrega.text()), 39),
                val_or_old(self.converter_data(self.lineEdit_gr_data_entrega_efetiva.text()), 40),
                val_or_old(self.converter_data(self.lineEdit_tr_data_entrega_efetiva.text()), 41),
                val_or_old(self.comboBox_rco.currentText(), 42),
                val_or_old(self.comboBox_procuradoria_federal.currentText(), 43),
                val_or_old(self.lineEdit_pregao.text().replace(".", "").replace("/", ""), 44),
                val_or_old(self.lineEdit_aviso_licitacao.text().strip().replace(".", "").replace("/", "").replace("-", ""), 45),
                val_or_old(self.comboBox_ocorrencias_abertura.currentText(), 46),
                val_or_old(self.converter_data(self.lineEdit_data_tributar.text()), 47),
                val_or_old(self.comboBox_gerenciamento_contratacao.currentText(), 48),

                id_participante,  # 49
                val_or_old(self.comboBox_termo_participacao.currentText(), 50),
                val_or_old(self.lineEdit_num_contratacao_pca_part.text().strip().replace(".", "").replace("/", ""), 51),
                val_or_old(self.lineEdit_item_irp.text().strip(), 52),
                val_or_old(self.lineEdit_descricao_sucinta.text().strip(), 53),
                val_or_old(''.join(filter(str.isdigit, self.lineEdit_qtde_item_manifestado.text())), 54),
                val_or_old(self.extrair_valor_float(self.lineEdit_valor_unitario_estimado), 55),
                val_or_old(self.extrair_valor_float(self.lineEdit_valor_total_estimado), 56),
                qtde_aprovada,  # 57
                val_or_old(self.extrair_valor_float(self.lineEdit_valor_unitario_homologado), 58),
                val_or_old(self.extrair_valor_float(self.lineEdit_valor_total_homologado), 59),
                val_or_old(self.converter_data(self.lineEdit_data_abertura_licitacao.text()), 60),
                val_or_old(self.comboBox_homologacao.currentText(), 61),
                val_or_old(self.comboBox_recurso.currentText(), 62),
                val_or_old(self.lineEdit_fornecedor_vencedor.text().strip(), 63),
                val_or_old(self.lineEdit_processo_pagamento.text().strip(), 64),
                val_or_old(self.lineEdit_ata.text().strip(), 65),
                val_or_old(self.converter_data(self.lineEdit_data_inicio_vigencia.text()), 66),
                val_or_old(''.join(filter(str.isdigit, self.lineEdit_fim_vigencia.text())), 67),
                val_or_old(self.lineEdit_of_ordem_fornecimento.text().strip().replace(".", "").replace("/", ""), 68),
                qtde_solicitada,  # 69
                saldo  # 70
            )

            # Comando SQL de inserção
            query = """
                INSERT INTO Historico (
                    ID_Listas,
                    Nome_Agente_Contratacao,
                    Elemento_Despesa,
                    Requisitante,
                    Licitacao_Tipo,
                    Situacao_ARP,
                    Situacao_item,
                    UASG_Gerenciadora,
                    Situacao_OF_e_NE,
                    Ocorrencias_Licitacao,
                    Procedimento,
                    Inexigibilidade,
                    Situacao_Entrega,
                    Situacao_IRP,
                    CNPJ,
                    Numero_Processo,
                
                    ID_OF,
                    Fornecedor_Vencedor,
                    Valor_Solicitado,
                    SEOR_Cogead_Envio,
                    SEOR_Cogead_Retorno,
                    Nota_Empenho,
                    Valor_Empenhado,
                    Data_Empenho,
                    Data_Limite_Envio,
                    Prazo_Entrega,
                    Data_Limite_Entrega,
                    Ultima_Verificacao,

                    ID_Contratacao,
                    DFD_do_SEI,
                    Num_Contratacao,
                    Data_Entrada_na_SMC,
                    Item,
                    Descricao_Item,
                    Codigo_Item,
                    Quantidade,
                    Objeto_Contratacao,
                    Data_da_Portaria,
                    Data_Email,
                    ETP_Data_Entrega,
                    GR_Data_Entrega_Efetiva,
                    TR_Data_Entrega_Efetiva,
                    RCO_Data_Entrega,
                    Procuradoria_Federal,
                    Pregao,
                    Aviso_Licitacao,
                    Ocorrencias_Abertura_Licitacao,
                    Data_Tributar,
                    Gerenciamento_Contratacao,

                    ID_Participante,
                    Termo_Participacao,
                    Num_Contratacao_PCA,
                    Item_do_IRP,
                    Descricao_Sucinta,
                    Qtde_Item_Manifestado,
                    Valor_Unitario_Estimado,
                    Valor_Total_Estimado,
                    Qtde_Aprovada_Gerenciador,
                    Valor_Unitario_Homologado,
                    Valor_Total_Homologado,
                    Data_Abertura_Licitacao,
                    Homologacao,
                    Recurso,
                    Fornecedor_Vencedor_Licitacao,
                    Processo_Pagamento,
                    ATA,
                    Data_Inicio_Vigencia,
                    Fim_Vigencia,
                    OF_Ordem_Fornecimento,
                    Qtde_Solicitada,
                    Saldo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor = self.conn.cursor()
            cursor.execute(query, params_historico)
            self.conn.commit()

            clear_fields_listas_suspensas(self)
            clear_fields_of_e_entregas(self)
            clear_fields_contratacao(self)
            clear_fields_participante(self)
            clear_fields_historico(self)

            QtWidgets.QMessageBox.information(self, "Sucesso", "Histórico salvo com sucesso!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar histórico: {e}")
            print(f"[ERRO] salvar_historico: {e}")

###############################################################################################################################################
    
    # Carrega as opções de todos os QComboBox.
    def carregar_combos_todos(self):
        try:
            cursor = self.conn.cursor()

            # Estrutura: (comboBox, nome_coluna, lista de tabelas onde buscar)
            campos_combo = [
                (self.comboBox_nome_agente_contratacao, "Nome_Agente_Contratacao", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_elemento_despesa, "Elemento_Despesa", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_requisitante, "Requisitante", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_licitacao_tipo, "Licitacao_Tipo", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_situacao_arp, "Situacao_ARP", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_situacao_item, "Situacao_Item", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_uasg_gerenciadora, "UASG_Gerenciadora", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_situacao_OF_e_NE, "Situacao_OF_e_NE", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_ocorrencias_licitacao, "Ocorrencias_Licitacao", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_procedimento, "Procedimento", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_inexigibilidade, "Inexigibilidade", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_situacao_entrega, "Situacao_Entrega", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_situacao_irp, "Situacao_IRP", ["Listas_Suspensas", "Historico"]),
                (self.comboBox_dfd_sei, "DFD_do_SEI", ["Contratacao", "Historico"]),
                (self.comboBox_codigo_item, "Codigo_Item", ["Contratacao", "Historico"]),
                (self.comboBox_rco, "RCO_Data_Entrega", ["Contratacao", "Historico"]),
                (self.comboBox_procuradoria_federal, "Procuradoria_Federal", ["Contratacao", "Historico"]),
                (self.comboBox_ocorrencias_abertura, "Ocorrencias_Abertura_Licitacao", ["Contratacao", "Historico"]),
                (self.comboBox_gerenciamento_contratacao, "Gerenciamento_Contratacao", ["Contratacao", "Historico"]),
                (self.comboBox_termo_participacao, "Termo_Participacao", ["Participante", "Historico"]),
                (self.comboBox_homologacao, "Homologacao", ["Participante", "Historico"]),
                (self.comboBox_recurso, "Recurso", ["Participante", "Historico"])
            ]

            for combo, coluna, tabelas in campos_combo:
                valores = set()
                for tabela in tabelas:
                    cursor.execute(f"SELECT DISTINCT {coluna} FROM {tabela} WHERE {coluna} IS NOT NULL")
                    resultados = cursor.fetchall()
                    for row in resultados:
                        valor = str(row[0]).strip()
                        if valor:
                            valores.add(valor)

                combo.clear()
                combo.addItem("")  # Item vazio como valor neutro
                for valor in sorted(valores):
                    combo.addItem(valor)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar combos: {e}")

    def carregar_historico(self):
        id_listas = self.comboBox_profissionais.currentData()
        self.id_listas = id_listas
        print(f"[DEBUG] ID selecionado: {id_listas}")

        if not id_listas:
            return

        try:
            self.carregar_combos_todos()  # carrega todos os combos com dados amplos

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM Historico WHERE ID_Listas = ? ORDER BY ID_Historico DESC", (id_listas,))
            dados = cursor.fetchall()

            if not dados:
                QtWidgets.QMessageBox.information(self, "Informação", "Nenhum histórico encontrado para este profissional.")
                self.tableView_historico.setModel(None)
                return

            # Exibe tabela
            modelo = QtGui.QStandardItemModel()
            colunas = [desc[0] for desc in cursor.description]
            modelo.setHorizontalHeaderLabels(colunas)
            for linha in dados:
                itens = [QtGui.QStandardItem(str(campo) if campo is not None else "") for campo in linha]
                modelo.appendRow(itens)
            self.tableView_historico.setModel(modelo)

            # Estiliza o cabeçalho horizontal da QTableView
            self.tableView_historico.setStyleSheet("""
                QHeaderView::section {
                    background-color: #ADD8E6;  /* Azul claro */
                    color: black;              /* Texto preto */
                    font-weight: bold;         /* Negrito */
                    border: 1px solid #CCCCCC; /* Bordas */
                }
            """)

            # Preenche campos
            self.preencher_campos_com_historico()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar histórico: {e}")


    def carregar_profissionais(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ls.ID_Listas, ls.Nome_Agente_Contratacao
            FROM Listas_Suspensas ls
            JOIN OF_e_Entregas ofe ON ls.ID_Listas = ofe.ID_Listas
            ORDER BY ls.Nome_Agente_Contratacao
        """)
        resultados = cursor.fetchall()
        
        self.comboBox_profissionais.clear()
        self.comboBox_profissionais.addItem("Selecione um profissional", None)  # Item inicial

        for id_listas, nome in resultados:
            self.comboBox_profissionais.addItem(nome, id_listas)

    # Preenche todos os campos da interface, incluindo QLineEdit, QComboBox...
    def preencher_campos_com_historico(self):
        """Preenche todos os campos da interface com o último histórico salvo do profissional selecionado."""
        id_listas = self.comboBox_profissionais.currentData()
        if not id_listas:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT TOP 1 
                    ID_Listas, Nome_Agente_Contratacao, Elemento_Despesa, Requisitante, Licitacao_Tipo,
                    Situacao_ARP, Situacao_item, UASG_Gerenciadora, Situacao_OF_e_NE, Ocorrencias_Licitacao,
                    Procedimento, Inexigibilidade, Situacao_Entrega, Situacao_IRP, CNPJ, Numero_Processo,

                    ID_OF, Fornecedor_Vencedor, Valor_Solicitado, SEOR_Cogead_Envio, SEOR_Cogead_Retorno,
                    Nota_Empenho, Valor_Empenhado, Data_Empenho, Data_Limite_Envio, Prazo_Entrega,
                    Data_Limite_Entrega, Ultima_Verificacao,

                    ID_Contratacao, DFD_do_SEI, Num_Contratacao, Data_Entrada_na_SMC, Item,
                    Descricao_Item, Codigo_Item, Quantidade, Objeto_Contratacao, Data_da_Portaria,
                    Data_Email, ETP_Data_Entrega, GR_Data_Entrega_Efetiva, TR_Data_Entrega_Efetiva,
                    RCO_Data_Entrega, Procuradoria_Federal, Pregao, Aviso_Licitacao,
                    Ocorrencias_Abertura_Licitacao, Data_Tributar, Gerenciamento_Contratacao,

                    ID_Participante, Termo_Participacao, Num_Contratacao_PCA, Item_do_IRP,
                    Descricao_Sucinta, Qtde_Item_Manifestado, Valor_Unitario_Estimado,
                    Valor_Total_Estimado, Qtde_Aprovada_Gerenciador, Valor_Unitario_Homologado,
                    Valor_Total_Homologado, Data_Abertura_Licitacao, Homologacao, Recurso,
                    Fornecedor_Vencedor_Licitacao, Processo_Pagamento, ATA, Data_Inicio_Vigencia,
                    Fim_Vigencia, OF_Ordem_Fornecimento, Qtde_Solicitada, Saldo
                FROM Historico
                WHERE ID_Listas = ?
                ORDER BY ID_Historico DESC
            """, (id_listas,))

            historico = cursor.fetchone()

            if not historico:
                return

            # Bloco 1 — Listas_Suspensas
            self.lineEdit_id_listas.setText(str(historico[0]))  # ID_Listas
            self.lineEdit_id_listas_of.setText(str(historico[0])) 
            self.lineEdit_id_listas_contratacao.setText(str(historico[0]))
            self.lineEdit_id_listas_part.setText(str(historico[0]))
            self.set_combo_value_safe(self.comboBox_nome_agente_contratacao, historico[1])
            self.set_combo_value_safe(self.comboBox_elemento_despesa, historico[2])
            self.set_combo_value_safe(self.comboBox_requisitante, historico[3])
            self.set_combo_value_safe(self.comboBox_licitacao_tipo, historico[4])
            self.set_combo_value_safe(self.comboBox_situacao_arp, historico[5])
            self.set_combo_value_safe(self.comboBox_situacao_item, historico[6])
            self.set_combo_value_safe(self.comboBox_uasg_gerenciadora, historico[7])
            self.set_combo_value_safe(self.comboBox_situacao_OF_e_NE, historico[8])
            self.set_combo_value_safe(self.comboBox_ocorrencias_licitacao, historico[9])
            self.set_combo_value_safe(self.comboBox_procedimento, historico[10])
            self.set_combo_value_safe(self.comboBox_inexigibilidade, historico[11])
            self.set_combo_value_safe(self.comboBox_situacao_entrega, historico[12])
            self.set_combo_value_safe(self.comboBox_situacao_irp, historico[13])
            self.lineEdit_cnpj_listas.setText(str(historico[14]))
            self.lineEdit_numero_processo_listas.setText(str(historico[15]))

            # Bloco 2 — OF_e_Entregas
            self.lineEdit_id_of.setText(str(historico[16]))     # ID_OF
            self.lineEdit_fornecedor.setText(str(historico[17]))
            self.lineEdit_valor_solicitado.setText(str(historico[18]))
            self.lineEdit_seor_envio.setText(self.converter_data_para_interface(historico[19]))
            self.lineEdit_seor_retorno.setText(self.converter_data_para_interface(historico[20]))

            nota_empenho = str(historico[21]) if historico[21] else ""
            nota_empenho = nota_empenho.replace("NE", "")
            metade = len(nota_empenho) // 2
            self.lineEdit_nota_empenho_inicio.setText(nota_empenho[:metade])
            self.lineEdit_nota_empenho_fim.setText(nota_empenho[metade:])

            self.lineEdit_valor_empenhado.setText(str(historico[22]))
            self.lineEdit_data_empenho.setText(self.converter_data_para_interface(historico[23]))
            self.lineEdit_data_limite_envio.setText(self.converter_data_para_interface(historico[24]))
            self.lineEdit_prazo_entrega.setText(str(historico[25]))
            self.lineEdit_data_limite_entrega.setText(self.converter_data_para_interface(historico[26]))
            self.lineEdit_ultima_verificacao.setText(self.converter_data_para_interface(historico[27]))

            # Bloco 3 — Contratacao
            self.lineEdit_id_contratacao.setText(str(historico[28]))  # ID_Contratacao
            self.set_combo_value_safe(self.comboBox_dfd_sei, historico[29])
            self.lineEdit_num_contratacao_pca.setText(str(historico[30]))
            self.lineEdit_data_entrada_smc.setText(self.converter_data_para_interface(historico[31]))
            self.lineEdit_item.setText(str(historico[32]))
            self.lineEdit_descricao_item.setText(str(historico[33]))
            self.set_combo_value_safe(self.comboBox_codigo_item, historico[34])
            self.lineEdit_qtde_solicitada.setText(str(historico[35]))
            self.lineEdit_objeto_contratacao.setText(str(historico[36]))
            self.lineEdit_data_portaria.setText(self.converter_data_para_interface(historico[37]))
            self.lineEdit_data_email.setText(self.converter_data_para_interface(historico[38]))
            self.lineEdit_etp_data_entrega.setText(self.converter_data_para_interface(historico[39]))
            self.lineEdit_gr_data_entrega_efetiva.setText(self.converter_data_para_interface(historico[40]))
            self.lineEdit_tr_data_entrega_efetiva.setText(self.converter_data_para_interface(historico[41]))
            self.set_combo_value_safe(self.comboBox_rco, historico[42])
            self.set_combo_value_safe(self.comboBox_procuradoria_federal, historico[43])
            self.lineEdit_pregao.setText(str(historico[44]))
            self.lineEdit_aviso_licitacao.setText(str(historico[45]))
            self.set_combo_value_safe(self.comboBox_ocorrencias_abertura, historico[46])
            self.lineEdit_data_tributar.setText(self.converter_data_para_interface(historico[47]))
            self.set_combo_value_safe(self.comboBox_gerenciamento_contratacao, historico[48])

            # Bloco 4 — Participante
            self.lineEdit_id_participante.setText(str(historico[49]))  # ID_Participante
            self.set_combo_value_safe(self.comboBox_termo_participacao, historico[50])
            self.lineEdit_num_contratacao_pca_part.setText(str(historico[51]))
            self.lineEdit_item_irp.setText(str(historico[52]))
            self.lineEdit_descricao_sucinta.setText(str(historico[53]))
            self.lineEdit_qtde_item_manifestado.setText(str(historico[54]))
            self.lineEdit_valor_unitario_estimado.setText(str(historico[55]))
            self.lineEdit_valor_total_estimado.setText(str(historico[56]))
            self.lineEdit_qtde_aprovada_gerenciador.setText(str(historico[57]))
            self.lineEdit_valor_unitario_homologado.setText(str(historico[58]))
            self.lineEdit_valor_total_homologado.setText(str(historico[59]))
            self.lineEdit_data_abertura_licitacao.setText(self.converter_data_para_interface(historico[60]))
            self.set_combo_value_safe(self.comboBox_homologacao, historico[61])
            self.set_combo_value_safe(self.comboBox_recurso, historico[62])
            self.lineEdit_fornecedor_vencedor.setText(str(historico[63]))
            self.lineEdit_processo_pagamento.setText(str(historico[64]))
            self.lineEdit_ata.setText(str(historico[65]))
            self.lineEdit_data_inicio_vigencia.setText(self.converter_data_para_interface(historico[66]))
            self.lineEdit_fim_vigencia.setText(str(historico[67]))
            self.lineEdit_of_ordem_fornecimento.setText(str(historico[68]))
            self.lineEdit_qtde_solicitada_part.setText(str(historico[69]))
            self.lineEdit_saldo.setText(str(historico[70]))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao preencher campos com histórico: {e}")

    # Define o valor do comboBox apenas se estiver entre as opções (com normalização).
    def set_combo_value_safe(self, combo, value):
        try:
            if value is None:
                combo.setCurrentIndex(0)
                return

            value_str = normalize_text(str(value))

            for i in range(combo.count()):
                item_text = normalize_text(combo.itemText(i))
                if item_text == value_str:
                    combo.setCurrentIndex(i)
                    return

            combo.addItem(str(value))  # Adiciona se não existir
            combo.setCurrentIndex(combo.count() - 1)

        except Exception as e:
            print(f"[ERRO] set_combo_value_safe: {e}")

    def carregar_tudo_para_profissional(self):
        self.carregar_combos_todos()
        self.carregar_historico()  # preenche tabela
        QTimer.singleShot(200, self.preencher_campos_com_historico)  # preenche campos

###############################################################################################################################################

    def excluir_dados_completos(self):
        """Exclui um registro do banco de dados."""
        try:
            id_listas = self.lineEdit_id_listas.text()
            id_of = self.lineEdit_id_of.text()
            id_contratacao = self.lineEdit_id_contratacao.text()
            id_participante = self.lineEdit_id_participante.text()

            if not id_listas or not id_of or not id_contratacao or not id_participante:
                QtWidgets.QMessageBox.warning(self, "Erro", "Nenhum registro selecionado para exclusão.")
                return

            # Exibir a caixa de diálogo de confirmação
            resposta = QtWidgets.QMessageBox.question(
                self,
                "Confirmação",
                "Você deseja realmente excluir este registro?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            # Se o usuário clicar em "Sim", prossegue com a exclusão
            if resposta != QtWidgets.QMessageBox.Yes:
                return  # Cancela se a resposta for diferente de "Sim"
            
            # 1. Excluir primeiro da tabela que depende (OF_e_Entregas)
            query_of = "DELETE FROM OF_e_Entregas WHERE ID_OF = ?"
            self.cursor.execute(query_of, (id_of,))

            # 2. Depois excluir da tabela (Contratacao)
            query_contratacao = "DELETE FROM Contratacao WHERE ID_Contratacao = ?"
            self.cursor.execute(query_contratacao, (id_contratacao,))

            # 3. Depois excluir da tabela (Participante)
            query_participante = "DELETE FROM Participante WHERE ID_Participante = ?"
            self.cursor.execute(query_participante, (id_participante,))

            # 4. Depois excluir da tabela principal (Listas_Suspensas)
            query_listas = "DELETE FROM Listas_Suspensas WHERE ID_Listas = ?"
            self.cursor.execute(query_listas, (id_listas,))

            # Confirma a exclusão no banco de dados
            self.conn.commit()  
            
            QtWidgets.QMessageBox.information(self, "Sucesso", "Registro excluído com sucesso!")
            clear_fields_listas_suspensas(self)
            clear_fields_of_e_entregas(self)
            clear_fields_contratacao(self)
            clear_fields_participante(self)
            clear_fields_historico(self)

        except pyodbc.Error as e:
            self.conn.rollback()
            QtWidgets.QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao excluir: {e}")


###############################################################################################################################################
    
    # Função para excluir linha selecionada do histórico
    def excluir_historico(self):
        # Pega a linha selecionada
        index = self.tableView_historico.currentIndex()
        if not index.isValid():
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione uma linha do histórico para excluir.")
            return

        # Confirmação do usuário
        resposta = QtWidgets.QMessageBox.question(
            self,
            "Confirmação",
            "Deseja realmente excluir esta linha do histórico?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if resposta != QtWidgets.QMessageBox.Yes:
            return

        try:
            # Pega o modelo atual e o ID_Historico (coluna 0)
            modelo = self.tableView_historico.model()
            id_historico = int(modelo.index(index.row(), 0).data())  # Supondo que a 1ª coluna é ID_Historico

            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Historico WHERE ID_Historico = ?", (id_historico,))
            self.conn.commit()

            QtWidgets.QMessageBox.information(self, "Sucesso", "Linha do histórico excluída com sucesso.")
            self.carregar_historico()  # Atualiza a tabela

            clear_fields_listas_suspensas(self)
            clear_fields_of_e_entregas(self)
            clear_fields_contratacao(self)
            clear_fields_participante(self)
            clear_fields_historico(self)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao excluir histórico: {e}")
            print(f"[ERRO] excluir_historico: {e}")

###############################################################################################################################################

    def setup_ui_pessoais(self):   

        # ComboBoxes Listas Suspensas
        self.comboBox_nome_agente_contratacao.addItems(['', 'Alexandre', 'Ana Paula', 'Cássia', 'Davidson', 'Juliana', 'Marcelle'])
         
        self.comboBox_elemento_despesa.addItems(['', '33.90.30', '33.90.30 TI',	'33.90.32',	'33.90.33',	'33.90.34',	'33.90.34 TI',
                                         	'33.90.36',	'33.90.36 TI',	'33.90.39',	'33.90.39 TI',	'33.90.39.08',	'33.90.39.84',	'33.90.40',	
                                            '44.90.40',	'44.90.52',	'44.90.52 TI'])  
        
        self.comboBox_requisitante.addItems(['', 'BEB', 'BVS', 'CCDE', 'CCI', 'CCPG', 'CEP', 'CODEMATES', 'COGETES', 'DIREÇÃO', 'Div Setores', 'EJA', 'LABFORM',
                                             'LABGESTÃO', 'LABMAN', 'LABORAT', 'LATEC', 'LATEPS', 'LAVSA', 'LIC-PROVOC', 'LIRES'])
        
        self.comboBox_licitacao_tipo.addItems(['', 'Adesão por SRP (Carona)', 'Chamada Pública', 'Dispensa de Licitação', 'Dispensa Eletrônica  - Lei 14.133/2021',
                                                        'Inexigibilidade de Licitação', 'Permissão de uso', 'Pregão eletrônico SISPP', 'Pregão eletrônico SRP',
                                                        'Pregão presencial', 'SRP - Externo', 'SRP-Fiocruz (compras compartilhadas)'])
        
        self.comboBox_situacao_arp.addItems(['', 'Adquirido', 'Aguardando solicitação', 'Ata Vigente com Saldo', 'Cancelado/Deserto', 'Impedida de Licitar',
                                                  'Licitado', 'Não aceito na SRP', 'NE Cancelada', 'Saldo Zerado', 'Vencida'])
        
        self.comboBox_situacao_item.addItems(['', 'Adquirido', 'Cancelado/Deserto', 'Em Andamento', 'Licitado', 'Não Licitado', 'Republicado'])
        self.comboBox_uasg_gerenciadora.addItems(['', '201057 - CENTRAL DE COMPRAS', '254420 - FIOCRUZ/RJ', '254421 - FIOCRUZ/PE', '254422 - FIOCRUZ/BA', '254423 - FIOCRUZ/MG',
                                                  '254431 - ICICT', '254434 - EPSJV', '254445 - BIOMANGUINHOS', '254446 - FARMANGUINHOS', '254447 - IFF', '254448 - INCQS',
                                                  '254450 - ENSP', '254452 - FIOCRUZ/DF', '254462 - COGIC', '254463 - IOC', '254474 - FIOCRUZ/MA', '254488 - COC', '254492 - IPEC', '254501- ICTB', 'Outros orgãos'])

        self.comboBox_situacao_OF_e_NE.addItems(['', 'Aguardando execução', 'Aguardando NE', 'Arquivado', 'Não é necessário controlar', 'NE cancelada', 'OF executada parcialmente', 'OF executada totalmente', 'OF Cancelada'])
        self.comboBox_ocorrencias_licitacao.addItems(['', 'Adesão (carona)', 'CP', 'DE (Lei 14.133/2021)', 'INEX', 'PE SISPP', 'PE SRP'])

        self.comboBox_procedimento.addItems(['', 'Credenciamento', 'Não se aplica', 'Pré-qualificação', 'SISPP', 'SRP'])
    

        self.comboBox_inexigibilidade.addItems(['', 'Lei 14.133/2021, art. 74, I', 'Lei 14.133/2021, art. 74, II', 'Lei 14.133/2021, art. 74, III', 'Lei 14.133/2021, art. 74, III, f',
                                         'Lei 14.133/2021, art. 74, IV', 'Lei 14.133/2021, art. 74, V', 'DE_lei14133art75', 'Lei 14.133/2021, art. 75, I',
                                         'Lei 14.133/2021, art. 75, II', 'Lei 14.133/2021, art. 75, III', 'Lei 14.133/2021, art. 75, IV', 'Lei 14.133/2021, art. 75, V',
                                         'Lei 14.133/2021, art. 75, VI', 'Lei 14.133/2021, art. 75, VII', 'Lei 14.133/2021, art. 75, VIII', 'Lei 14.133/2021, art. 75, IX', 'Lei 14.133/2021, art. 75, X',
                                         'Lei 14.133/2021, art. 75, XI', 'chamada Pública', 'Port 306/2011'])
        self.comboBox_situacao_entrega.addItems(['', 'Aguardando Entrega', 'Entrega Atrasada', 'Entrega com Problema', 'Entrega Parcial', 'Entrega Total/Concluída', 'Prazo Prorrogado'])
        
        
        self.comboBox_situacao_irp.addItems(['', 'Aceita', 'Cancelada', 'Em Andamento', 'Licitado', 'Não Confirmada', 'Não Aceita'])
        self.lineEdit_cnpj_listas.textChanged.connect(self.atualizar_mascara)
        self.lineEdit_numero_processo_listas.setInputMask("00000.000000/0000-00;_")

        # ComboBoxes OF e ENTREGAS - Conecta sinais e aplica máscaras 
        self.lineEdit_valor_solicitado.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_valor_solicitado))
        self.lineEdit_valor_empenhado.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_valor_empenhado))

        self.lineEdit_data_limite_envio.setInputMask("00/00/0000;_")
        self.lineEdit_data_limite_entrega.setInputMask("00/00/0000;_")
        self.lineEdit_seor_envio.setInputMask("00/00/0000;_")
        self.lineEdit_seor_retorno.setInputMask("00/00/0000;_")
        self.lineEdit_data_empenho.setInputMask("00/00/0000;_")
        self.lineEdit_ultima_verificacao.setInputMask("00/00/0000;_")

        self.lineEdit_prazo_entrega.textChanged.connect(lambda: self.formatar_prazo(self.lineEdit_prazo_entrega))
        self.lineEdit_nota_empenho_inicio.setInputMask("0000;_") # Só 4 dígitos
        self.lineEdit_nota_empenho_fim.setInputMask("00000;_") # Só 5 dígitos

        # ComboBoxes Contratação - Conecta sinais e aplica máscaras
        self.comboBox_dfd_sei.addItems(['', 'Correto', 'Incorreto'])
        self.lineEdit_num_contratacao_pca.setInputMask("00000.00000/0000;_")  
        self.lineEdit_data_entrada_smc.setInputMask("00/00/0000;_")
        self.comboBox_codigo_item.addItems(['', 'Catser', 'Catmat'])
        self.lineEdit_data_portaria.setInputMask("00/00/0000;_")
        self.lineEdit_data_email.setInputMask("00/00/0000;_")
        self.lineEdit_etp_data_entrega.setInputMask("00/00/0000;_")
        self.lineEdit_gr_data_entrega_efetiva.setInputMask("00/00/0000;_")
        self.lineEdit_tr_data_entrega_efetiva.setInputMask("00/00/0000;_")
        self.comboBox_rco.addItems(['', 'Sim', 'Não'])
        self.comboBox_procuradoria_federal.addItems(['', 'Sim', 'Não'])
        self.comboBox_ocorrencias_abertura.addItems(['', 'Cancelado', 'Republicado com alteração', 'Republicado sem alteração', 'Revogado', 'Suspensão administrativa', 'Suspensão judicial', 'Suspenso por tempo Indeterminado'])
        self.lineEdit_data_tributar.setInputMask("00/00/0000;_")
        self.comboBox_gerenciamento_contratacao.addItems(['', 'Contrato', 'ICNE-informações complementares a nota de empenho', 'OF / NE', 'Não se aplica'])
        self.lineEdit_pregao.setInputMask("00000/0000;_")
        self.lineEdit_aviso_licitacao.setInputMask("00000/0000;_")

        # ComboBoxes Participante - Conecta sinais e aplica máscaras
        self.comboBox_termo_participacao.addItems(['', 'Fase do planejamento', 'Licitação', 'Procuradoria Federal', 'Resultado da Licitação'])
        self.lineEdit_num_contratacao_pca_part.setInputMask("00000.00000/0000;_") 
        self.lineEdit_qtde_item_manifestado.setInputMask("0000000;_") 
        self.lineEdit_valor_unitario_estimado.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_valor_unitario_estimado))
        self.lineEdit_valor_total_estimado.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_valor_total_estimado))
        self.lineEdit_valor_unitario_homologado.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_valor_unitario_homologado))
        self.lineEdit_valor_total_homologado.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_valor_total_homologado))
        self.lineEdit_data_abertura_licitacao.setInputMask("00/00/0000;_")
        self.comboBox_homologacao.addItems(['', 'Sim', 'Não'])
        self.comboBox_recurso.addItems(['', 'Sim', 'Não'])
        self.lineEdit_processo_pagamento.setInputMask("00000.000000/0000-00;_")
        self.lineEdit_data_inicio_vigencia.setInputMask("00/00/0000;_")
        self.lineEdit_fim_vigencia.textChanged.connect(lambda: self.formatar_prazo(self.lineEdit_fim_vigencia))
        self.lineEdit_qtde_aprovada_gerenciador.textChanged.connect(self.calcular_saldo)
        self.lineEdit_qtde_solicitada_part.textChanged.connect(self.calcular_saldo)
        self.lineEdit_saldo.textChanged.connect(lambda: self.tratar_valor_moeda(self.lineEdit_saldo))
        self.lineEdit_of_ordem_fornecimento.setInputMask("00000/0000;_")

    #Máscara para CNPJ                            
    def atualizar_mascara(self):
        sender = self.sender()  # pega o campo que disparou
        text = sender.text().replace(".", "").replace("-", "").replace("/", "")

        cursor_position = sender.cursorPosition()

        sender.textChanged.disconnect(self.atualizar_mascara)  

        if len(text) <= 14:  # CNPJ
            sender.setInputMask("00.000.000/0000-00;_")

        sender.setText(text)
        sender.setCursorPosition(cursor_position)

        sender.textChanged.connect(self.atualizar_mascara)

      #Máscara para valores em dinheiro
    def formatar_moeda(self, valor):
        try:
            locale = QLocale(QLocale.Portuguese)
            
            # Converte o valor para float e divide por 100, mantendo sinal negativo se houver
            valor_float = float(valor) / 100

            return locale.toString(valor_float, 'f', 2)
        except ValueError:
            return "0,00"
    
        # Aplica máscara de moeda ao LineEdit (quando o usuário digita)
    def tratar_valor_moeda(self, line_edit):
        texto = line_edit.text().strip()

        if not texto:  # Se vazio, não faz nada
            return

        # Permite dígitos e sinal de menos no começo
        import re
        texto_valido = re.sub(r'[^\d\-]', '', texto)  # remove tudo exceto dígitos e '-'

        # Evita múltiplos sinais '-'
        if texto_valido.count('-') > 1:
            texto_valido = texto_valido.replace('-', '')

        # Mantém '-' só se estiver no início
        if '-' in texto_valido and not texto_valido.startswith('-'):
            texto_valido = texto_valido.replace('-', '')

        if texto_valido and texto_valido != '-':
            # Remove o sinal negativo temporariamente para formatar valor absoluto
            sinal = ''
            if texto_valido.startswith('-'):
                sinal = '-'
                texto_valido = texto_valido[1:]

            if texto_valido.isdigit():
                valor_formatado = self.formatar_moeda(texto_valido)
                line_edit.setText(sinal + valor_formatado)
            else:
                line_edit.setText("0,00")
        else:
            line_edit.setText("0,00")

        # Converte o valor do campo (em formato '1.234,56' ou '1234,56') para float
    def extrair_valor_float(self, campo):
        valor_texto = campo.text().strip()

        if not valor_texto:
            print(f"[extrair_valor_float] Campo vazio: '{valor_texto}' → 0.0")
            return 0.0

        try:
            # Remove pontos de milhar e troca vírgula por ponto para float
            valor_limpo = valor_texto.replace(".", "").replace(",", ".")
            valor_float = float(valor_limpo)
            return valor_float
        except ValueError:
            print(f"[extrair_valor_float] Valor inválido: '{valor_texto}' → 0.0")
            return 0.0

    #Máscara para prazo de entrega em dias (ex: 5 dias)
    def formatar_prazo(self, line_edit):
        texto = ''.join(filter(str.isdigit, line_edit.text()))
        line_edit.setText(f"{texto} dias" if texto else "")

        # Converte para o banco data do formato 'dd/mm/yyyy' para 'yyyy-mm-dd'
    def converter_data(self, texto_data):
        if isinstance(texto_data, datetime.date):
            return texto_data
        try:
            return datetime.datetime.strptime(texto_data, "%d/%m/%Y").date()
        except (ValueError, TypeError):
            return None
        # Converte para interface 
    def converter_data_para_interface(self, data_obj):
        if isinstance(data_obj, (datetime.date, datetime.datetime)):
            return data_obj.strftime("%d/%m/%Y")
        return ''



###############################################################################################################################################

    def setup_connections(self):        
        self.btn_cadastrar.clicked.connect(self.cadastrar_dados_completos) # Conecta o botão de cadastrar        
        self.btn_salvar.clicked.connect(self.salvar_dados_completos) # Conecta o botão de salvar
        self.btn_excluir.clicked.connect(self.excluir_dados_completos) # Conecta o botão de excluir        
        self.btn_buscar_nome.clicked.connect(self.buscar_por_nome) # Conecta o botão de buscar todos os campos        
        self.btn_limpar.clicked.connect(self.limpar_campos_apos_atualizacao) # Conecta o botão de limpar todos os campos
        self.btn_salvar_historico.clicked.connect(self.salvar_historico) # Conecta o botão de salvar o histórico
        self.btn_excluir_historico.clicked.connect(self.excluir_historico)

        # Impede que o usuário edite as células do histórico, tornando somente leitura
        # self.tableView_historico.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)        

    def limpar_campos_apos_atualizacao(self):
        print("Limpando campos...")  # DEBUG
        clear_fields_listas_suspensas(self)
        clear_fields_of_e_entregas(self)
        clear_fields_contratacao(self)
        clear_fields_participante(self)
        clear_fields_historico(self)