# 👑 Clash Royale Dashboard

Dashboard em Streamlit para consultar estatísticas de jogadores do Clash Royale e comparar dois jogadores lado a lado, usando a API oficial da Supercell através de um proxy próprio.

## 📝 Requisitos para Rodar

🧾 Para executar o **Clash Royale Dashboard**, são necessários:

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python Badge"> Linguagem usada no projeto. **[Python 3.11+](https://www.python.org/downloads/)**

<img src="https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white"> Editor de código recomendado. **[Visual Studio Code](https://code.visualstudio.com/)**

<img src="https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white">  Para clonar o repositório. **[Git](https://git-scm.com/downloads)**

![key](https://www.readmecodegen.com/api/social-icon?name=key&size=16) Um **token de acesso** ao proxy da API, fornecido pelo administrador do projeto.

## ⚙️ Como Executar

**Repositório:**
```
https://github.com/Xitao70/clash-royale-dashboard.git
```

1. Clone o repositório ou baixe o ZIP na aba **Code**.
2. Abra a pasta do projeto no Visual Studio Code.
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```
4. Crie a pasta `.streamlit` na raiz do projeto e, dentro dela, o arquivo `secrets.toml`:
   ```toml
   PROXY_API_URL = "endereco-do-proxy"
   PROXY_SECRET = "seu-token-de-acesso"
   ```
5. No terminal, rode:
   ```bash
   streamlit run app.py
   ```
6. O navegador abre automaticamente em `localhost:8501`.

## ![bug](https://www.readmecodegen.com/api/social-icon?name=bug&size=32&color=%23ef4444) Checklist de Erros Solucionados

- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) Os ícones do menu de navegação apareciam duplicados ("👑 👑 Dashboard").
- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) A busca era disparada automaticamente ao abrir a página, sem precisar clicar em "Buscar Dados".
- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) O indicador de carregamento ("spinner") continuava girando mesmo depois de a mensagem de erro já ter aparecido.
- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) Buscas repetidas rápidas podiam gerar erro 429 (limite de requisições) sem aviso claro — agora existe cooldown e cache.
- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) A validação de TAG aceitava qualquer tamanho de caracteres, incluindo tags claramente inválidas.
- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) Um valor nulo vindo da API podia travar o cálculo do "Tempo de Conta".
- ![check](https://www.readmecodegen.com/api/social-icon?name=check&size=16) O arquivo `requirements.txt` estava salvo com encoding incompatível (UTF-16 em vez de UTF-8).

## 📂 Estrutura do Sistema

```
clash-royale-dashboard/
├── app.py                        # Ponto de entrada e navegação
├── clash_api.py                  # Cliente da API (cache, validação, cooldown)
├── card_roles.py                 # Classificação de funções das cartas
├── counter_engine.py             # Lógica de cobertura de ameaças
├── pages/
│   ├── 1_Dashboard.py            # Estatísticas de um jogador
│   └── 2_Jogador_vs_Jogador.py   # Comparação entre dois jogadores
├── .streamlit/
│   └── secrets.toml              # Credenciais locais (não versionado)
└── requirements.txt
```

## 🔧 Tecnologias

- [Streamlit](https://streamlit.io/)
- [Requests](https://docs.python-requests.org/)
- API oficial do [Clash Royale](https://developer.clashroyale.com/)

---
*Projeto de participação fechada — acesso e contribuições apenas por convite.*
