# 🧾 Sistema de Compras - Fiocruz

Este projeto é um sistema desktop desenvolvido em **Python + PyQt5** com banco de dados **SQL Server**, voltado para a **gestão de pedidos, entregas e controle de compras** da Fiocruz.  
O objetivo é centralizar e digitalizar os processos de requisição e recebimento de materiais de forma segura e organizada.

---

## 🚀 Tecnologias Utilizadas

- Python 3.10+
- PyQt5
- SQL Server
- PyInstaller
- Inno Setup
- Pandas / PyODBC

---

## 📁 Estrutura do Projeto

Sistema_Fiocruz_Compras/
├── src/ # Código-fonte Python
├── interface/ # Telas Qt Designer (.ui)
├── sql/ # Scripts SQL (tabelas, inserts)
├── docs/ # Documentação
│ ├── Passo a Passo - PyInstaller.docx
│ ├── Passo a Passo - Inno Setup.docx
│ └── diagrama_inicial_sem_relacionamentos.png (opcional)
├── instalador.iss # Script Inno Setup para gerar instalador
├── .gitignore # Arquivos/pastas ignorados
└── README.md # Este arquivo


---

## ⚙️ Instalação e Uso

### 🔧 1. Geração do Executável
Utilize o **PyInstaller** para compilar o sistema `.py` em `.exe`  
> Veja o documento: `docs/Passo a Passo - PyInstaller.docx`

### 🧩 2. Criação do Instalador
Utilize o **Inno Setup** para criar o instalador profissional `.exe`  
> Veja: `docs/Passo a Passo - Inno Setup.docx`

---

## 🗂️ Banco de Dados

- O sistema usa SQL Server como base de dados
- A estrutura do banco deve ser criada com os scripts em `sql/`
- A conexão com o banco é feita via ODBC (Driver 17)
- **⚠️ O sistema exige a configuração da instância do SQL Server local**

---

## 📌 Observações

- O banco de dados real com informações da Fiocruz **não está incluído no repositório** por motivos de privacidade e conformidade com a LGPD
- O sistema pode ser adaptado para outras instituições com ajustes mínimos no banco de dados e layout

---

## 🤝 Contribuição

Este projeto foi desenvolvido com foco organizacional e pode ser estendido para outras áreas ou demandas.  
Colaborações são bem-vindas para melhorias, relatórios e integração com outros sistemas.

---

## 🛡️ Licença

Este projeto é de uso interno da Fiocruz.  
Caso deseje adaptar para uso externo, entre em contato com o autor.
