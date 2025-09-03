# Desafio Faturas RPA

Este projeto realiza a leitura de faturas disponíveis no endpoint do desafio RPA Challenge, baixa apenas as faturas vencidas ou que vencem hoje, salva em PDF e registra todas as informações em um CSV. Além disso, mantém logs detalhados de execução.

---

## 🚀 Funcionalidades

- Extrai **ID da fatura**, **Due Date** e **URL da fatura** do endpoint `/seed`.
- Baixa apenas faturas vencidas ou vencendo hoje.
- Salva faturas em **PDF** na pasta `downloads/`.
- Atualiza um **CSV** (`data/faturas.csv`) com todas as faturas processadas.
- Mantém logs detalhados da execução em **logs/**.
- Permite auditoria completa do processo, com acompanhamento de falhas.

---

## 📦 Estrutura do Projeto

```graphql
faturas_rpa/
│
├── main.py # Código principal do projeto
├── requirements.txt # Dependências do projeto
├── data/
│ └── faturas.csv # CSV com faturas processadas
├── downloads/ # PDFs baixados
├── logs/ # Logs detalhados de execução
└── README.md # Documentação do projeto
```


---

## ⚡ Pré-requisitos

- Python 3.10+  
- `pip` instalado

---

## 🐍 Configuração do Ambiente Virtual

A criação de um **venv** é altamente recomendada para manter o projeto isolado:

```bash
# Criar venv
python -m venv .venv

# Ativar no Windows
.venv\Scripts\activate

# Ativar no Linux/macOS
source .venv/bin/activate
```

## Por que usar venv?
* Isolamento de dependências: cada projeto mantém suas bibliotecas sem conflitos.
* Evita poluição do Python global: mantém o Python global limpo e seguro.
* Reprodutibilidade: garante que o código funcione da mesma forma em qualquer máquina.
* Segurança e controle de versões: você escolhe a versão das bibliotecas e do Python.

## 📥 Instalação das Dependências:

```bash
pip install -r requirements.txt
```
## ▶️ Executando o Projeto
```bash
python main.py
```

* O script irá criar as pastas necessárias (```downloads```, ```data```, ```logs```) caso não existam.
* O CSV será atualizado automaticamente.
* Logs de execução serão salvos em ```logs/```.

## 🤔 Decisões Técnicas

* Requests + Pillow: Para baixar imagens e converter para PDF quando necessário.
* Requisição POST ao endpoint /seed: Evita depender de OCR ou scraping dinâmico do site.
* Controle de retries (3 tentativas): Garante robustez em caso de falhas de rede.
* Filtros de Data: Somente faturas vencidas ou vencendo hoje são baixadas.
* CSV incremental: Atualiza o arquivo à medida que faturas são processadas, permitindo reinício do script sem duplicar dados.

## 📝 Resumo de Logs (Exemplo)

| Categoria              | Quantidade | Exemplos de Faturas                                                                 |
|------------------------|------------|------------------------------------------------------------------------------------|
| ✅ Faturas baixadas     | 6          | mtc8kshsq8qoqf2clfhap.pdf, j3drljaeckd8xpucocp6lc.pdf                              |
| ⏭ Faturas ignoradas    | 4          | 4hs6bwyrhz7b3o47gxgaeo (2025-09-23), 09s1rpdbv4pgk3sv9va8xl (2025-10-15)          |
| ❌ Faturas com falha   | 1          | nrfmmfdr9jnnuua4omrs1.pdf                                                          |

> Observação: Os números e exemplos da tabela mudam dinamicamente dependendo da data atual e das faturas retornadas pelo endpoint `/seed`.

## 💡 Benefícios desta abordagem

* Permite auditoria completa do processo.
* Garante que apenas faturas vencidas ou vencendo hoje sejam baixadas.
* Facilita acompanhamento de falhas sem depender do terminal.
* Documentação limpa e clara para entrega.
