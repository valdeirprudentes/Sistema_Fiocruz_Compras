import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView
from PyQt5.uic import loadUi
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5 import QtWidgets
from db_connection import get_pyodbc_connection
import warnings

# Ignora/Esconde aviso
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            else:
                return str(self._df.index[section])
        return None

class PlanilhasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("planilhas.ui", self)

        # Obtenha a conexão PyODBC do módulo centralizado
        self.conn = get_pyodbc_connection(log=False)
        if not self.conn:
            QtWidgets.QMessageBox.critical(self, "Erro", "Não foi possível conectar ao banco de dados.")
            return
        
        self.cursor = self.conn.cursor()

        # Ações dos botões
        self.btn_carregar_tabela.clicked.connect(self.carregar_tabela)
        self.btn_exportar.clicked.connect(self.exportar_para_excel)
        self.btn_importar.clicked.connect(self.importar_do_excel)

        self.carregar_nomes_tabelas()


    def carregar_nomes_tabelas(self):
        self.comboBox_nomes_tabelas.clear()
        self.cursor.execute(""" SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME != 'sysdiagrams'""")
        tabelas = [row[0] for row in self.cursor.fetchall()]
        self.comboBox_nomes_tabelas.addItems(tabelas)

    def carregar_tabela(self):
        nome_tabela = self.comboBox_nomes_tabelas.currentText()
        if not nome_tabela:
            QMessageBox.warning(self, "Aviso", "Selecione uma tabela.")
            return

        query = f"SELECT * FROM [{nome_tabela}]"
        df = pd.read_sql(query, self.conn)
        model = PandasModel(df)
        self.tableView_planilhas.setModel(model)

    def exportar_para_excel(self):
        nome_tabela = self.comboBox_nomes_tabelas.currentText()
        if not nome_tabela:
            QMessageBox.warning(self, "Aviso", "Selecione uma tabela.")
            return

        query = f"SELECT * FROM [{nome_tabela}]"
        df = pd.read_sql(query, self.conn)

        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar como", f"{nome_tabela}.xlsx", "Excel Files (*.xlsx)")
        if caminho:
            df.to_excel(caminho, index=False)
            QMessageBox.information(self, "Sucesso", f"Tabela exportada para {caminho}")

    def importar_do_excel(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo Excel", "", "Excel Files (*.xlsx *.xls)")
        if caminho:
            try:
                df = pd.read_excel(caminho, engine='openpyxl')
                model = PandasModel(df)                 # cria o model do pandas
                self.tableView_planilhas.setModel(model)  # seta o model na QTableView
                QMessageBox.information(self, "Importado", "Excel carregado e exibido com sucesso!")
            except Exception as e:
                print(f"Erro ao importar: {e}")
                QMessageBox.critical(self, "Erro", f"Erro ao importar: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlanilhasApp()
    window.show()
    sys.exit(app.exec_())