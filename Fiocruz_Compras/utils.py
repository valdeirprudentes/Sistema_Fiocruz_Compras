from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets

def show_message_box(title, message, icon=None):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    if icon:
        msg.setIcon(icon)
    msg.exec_()

def clear_fields_listas_suspensas(self):
    """Limpa todos os campos da interface."""
    self.lineEdit_id_listas.clear()
    self.lineEdit_busca_nome.clear() # Apaga os campos depois da busca
    self.comboBox_nome_agente_contratacao.setCurrentIndex(0)
    self.comboBox_elemento_despesa.setCurrentIndex(0)
    self.comboBox_requisitante.setCurrentIndex(0)
    self.comboBox_licitacao_tipo.setCurrentIndex(0)
    self.comboBox_situacao_arp.setCurrentIndex(0)
    self.comboBox_situacao_item.setCurrentIndex(0)
    self.comboBox_uasg_gerenciadora.setCurrentIndex(0)
    self.comboBox_ocorrencias_licitacao.setCurrentIndex(0)
    self.comboBox_situacao_OF_e_NE.setCurrentIndex(0)
    self.comboBox_procedimento.setCurrentIndex(0)
    self.comboBox_inexigibilidade.setCurrentIndex(0)
    self.comboBox_situacao_entrega.setCurrentIndex(0)
    self.comboBox_situacao_irp.setCurrentIndex(0)
    self.lineEdit_cnpj_listas.clear()
    self.lineEdit_numero_processo_listas.clear()

#######################################################

def clear_fields_of_e_entregas(self):
    """Limpa todos os campos da interface."""
    self.lineEdit_id_of.clear()
    self.lineEdit_fornecedor.clear()
    self.lineEdit_valor_solicitado.clear()
    self.lineEdit_seor_envio.clear()
    self.lineEdit_seor_retorno.clear()
    self.lineEdit_nota_empenho_inicio.clear()
    self.lineEdit_nota_empenho_fim.clear()
    self.lineEdit_valor_empenhado.clear()
    self.lineEdit_data_empenho.clear()
    self.lineEdit_data_limite_envio.clear()
    self.lineEdit_prazo_entrega.clear()
    self.lineEdit_data_limite_entrega.clear()
    self.lineEdit_ultima_verificacao.clear()
    self.lineEdit_id_listas_of.clear()

    #######################################################

def clear_fields_contratacao(self):
    """Limpa todos os campos da interface."""
    self.lineEdit_id_contratacao.clear()
    self.comboBox_dfd_sei.setCurrentIndex(0)  # Correto / Incorreto
    self.lineEdit_num_contratacao_pca.clear()
    self.lineEdit_data_entrada_smc.clear()
    self.lineEdit_item.clear()
    self.lineEdit_descricao_item.clear()
    self.comboBox_codigo_item.setCurrentIndex(0)  # CATSER / CATMAT
    self.lineEdit_qtde_solicitada.clear()
    self.lineEdit_objeto_contratacao.clear()
    self.lineEdit_data_portaria.clear()
    self.lineEdit_data_email.clear()
    self.lineEdit_etp_data_entrega.clear()
    self.lineEdit_gr_data_entrega_efetiva.clear()
    self.lineEdit_tr_data_entrega_efetiva.clear()
    self.comboBox_rco.setCurrentIndex(0)
    self.comboBox_procuradoria_federal.setCurrentIndex(0)
    self.lineEdit_pregao.clear()
    self.lineEdit_aviso_licitacao.clear()
    self.comboBox_ocorrencias_abertura.setCurrentIndex(0)
    self.lineEdit_data_tributar.clear()
    self.comboBox_gerenciamento_contratacao.setCurrentIndex(0)
    self.lineEdit_id_listas_contratacao.clear()

#######################################################
def clear_fields_participante(self):
    """Limpa todos os campos da interface."""
    self.lineEdit_id_participante.clear()
    self.comboBox_termo_participacao.setCurrentIndex(0)
    self.lineEdit_num_contratacao_pca_part.clear()
    self.lineEdit_item_irp.clear()
    self.lineEdit_descricao_sucinta.clear()
    self.lineEdit_qtde_item_manifestado.clear()
    self.lineEdit_valor_unitario_estimado.clear()
    self.lineEdit_valor_total_estimado.clear()
    self.lineEdit_qtde_aprovada_gerenciador.clear()
    self.lineEdit_valor_unitario_homologado.clear()
    self.lineEdit_valor_total_homologado.clear()
    self.lineEdit_data_abertura_licitacao.clear()
    self.comboBox_homologacao.setCurrentIndex(0)
    self.comboBox_recurso.setCurrentIndex(0)
    self.lineEdit_fornecedor_vencedor.clear()
    self.lineEdit_processo_pagamento.clear()
    self.lineEdit_ata.clear()
    self.lineEdit_data_inicio_vigencia.clear()
    self.lineEdit_fim_vigencia.clear()
    self.lineEdit_of_ordem_fornecimento.clear()
    self.lineEdit_qtde_solicitada_part.clear()
    self.lineEdit_saldo.clear()
    self.lineEdit_id_listas_part.clear()  # Limpa o campo do ID_Listas

def clear_fields_historico(self):
    # === Listas Suspensas ===
    self.lineEdit_id_listas.clear()
    self.comboBox_nome_agente_contratacao.setCurrentIndex(0)
    self.comboBox_elemento_despesa.setCurrentIndex(0)
    self.comboBox_requisitante.setCurrentIndex(0)
    self.comboBox_licitacao_tipo.setCurrentIndex(0)
    self.comboBox_situacao_arp.setCurrentIndex(0)
    self.comboBox_situacao_item.setCurrentIndex(0)
    self.comboBox_uasg_gerenciadora.setCurrentIndex(0)
    self.comboBox_situacao_OF_e_NE.setCurrentIndex(0)
    self.comboBox_ocorrencias_licitacao.setCurrentIndex(0)
    self.comboBox_procedimento.setCurrentIndex(0)
    self.comboBox_inexigibilidade.setCurrentIndex(0)
    self.comboBox_situacao_entrega.setCurrentIndex(0)
    self.comboBox_situacao_irp.setCurrentIndex(0)
    self.lineEdit_cnpj_listas.clear()
    self.lineEdit_numero_processo_listas.clear()

    # IDs replicados nas abas
    self.lineEdit_id_listas_of.clear()
    self.lineEdit_id_listas_contratacao.clear()
    self.lineEdit_id_listas_part.clear()

    # === OF e Entregas ===
    self.lineEdit_id_of.clear()
    self.lineEdit_fornecedor.clear()
    self.lineEdit_valor_solicitado.clear()
    self.lineEdit_seor_envio.clear()
    self.lineEdit_seor_retorno.clear()
    self.lineEdit_nota_empenho_inicio.clear()
    self.lineEdit_nota_empenho_fim.clear()
    self.lineEdit_valor_empenhado.clear()
    self.lineEdit_data_empenho.clear()
    self.lineEdit_data_limite_envio.clear()
    self.lineEdit_prazo_entrega.clear()
    self.lineEdit_data_limite_entrega.clear()
    self.lineEdit_ultima_verificacao.clear()

    # === Contratação ===
    self.lineEdit_id_contratacao.clear()
    self.comboBox_dfd_sei.setCurrentIndex(0)
    self.lineEdit_num_contratacao_pca.clear()
    self.lineEdit_data_entrada_smc.clear()
    self.lineEdit_item.clear()
    self.lineEdit_descricao_item.clear()
    self.comboBox_codigo_item.setCurrentIndex(0)
    self.lineEdit_qtde_solicitada.clear()
    self.lineEdit_objeto_contratacao.clear()
    self.lineEdit_data_portaria.clear()
    self.lineEdit_data_email.clear()
    self.lineEdit_etp_data_entrega.clear()
    self.lineEdit_gr_data_entrega_efetiva.clear()
    self.lineEdit_tr_data_entrega_efetiva.clear()
    self.comboBox_rco.setCurrentIndex(0)
    self.comboBox_procuradoria_federal.setCurrentIndex(0)
    self.lineEdit_pregao.clear()
    self.lineEdit_aviso_licitacao.clear()
    self.comboBox_ocorrencias_abertura.setCurrentIndex(0)
    self.lineEdit_data_tributar.clear()
    self.comboBox_gerenciamento_contratacao.setCurrentIndex(0)

    # === Participante ===
    self.lineEdit_id_participante.clear()
    self.comboBox_termo_participacao.setCurrentIndex(0)
    self.lineEdit_num_contratacao_pca_part.clear()
    self.lineEdit_item_irp.clear()
    self.lineEdit_descricao_sucinta.clear()
    self.lineEdit_qtde_item_manifestado.clear()
    self.lineEdit_valor_unitario_estimado.clear()
    self.lineEdit_valor_total_estimado.clear()
    self.lineEdit_qtde_aprovada_gerenciador.clear()
    self.lineEdit_valor_unitario_homologado.clear()
    self.lineEdit_valor_total_homologado.clear()
    self.lineEdit_data_abertura_licitacao.clear()
    self.comboBox_homologacao.setCurrentIndex(0)
    self.comboBox_recurso.setCurrentIndex(0)
    self.lineEdit_fornecedor_vencedor.clear()
    self.lineEdit_processo_pagamento.clear()
    self.lineEdit_ata.clear()
    self.lineEdit_data_inicio_vigencia.clear()
    self.lineEdit_fim_vigencia.clear()
    self.lineEdit_of_ordem_fornecimento.clear()
    self.lineEdit_qtde_solicitada_part.clear()
    self.lineEdit_saldo.clear()

    # Limpa a Table View com os Históricos
    self.tableView_historico.setModel(None)

    # Limpa todos os QComboBox da tela (reseta para o primeiro item se existir)
    for widget in self.findChildren(QtWidgets.QComboBox):
        if widget.count() > 0:
            widget.setCurrentIndex(0)
