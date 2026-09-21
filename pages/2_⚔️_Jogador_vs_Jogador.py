import os
from urllib.parse import quote

import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Jogador vs Jogador",
    page_icon="⚔️",
    layout="wide",
)


# ============================================================
# NAVEGAÇÃO PRINCIPAL
# ============================================================

nav_dashboard, nav_comparacao = st.columns(2)

with nav_dashboard:
    st.page_link(
        "app.py",
        label="👑 Dashboard"
    )

with nav_comparacao:
    st.page_link(
        "pages/2_⚔️_Jogador_vs_Jogador.py",
        label="⚔️ Jogador vs Jogador"
    )

st.divider()


# ============================================================
# CONFIGURAÇÃO DO PROXY
# ============================================================

def get_config(nome, padrao=None):
    """
    Procura primeiro em st.secrets e depois nas variáveis de ambiente.
    """

    try:
        if nome in st.secrets:
            return st.secrets[nome]
    except Exception:
        pass

    return os.getenv(nome, padrao)


PROXY_API_URL = get_config("PROXY_API_URL")
PROXY_SECRET = get_config("PROXY_SECRET")


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        opacity: 0.70;
        margin-bottom: 2rem;
    }

    .player-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .player-name {
        text-align: center;
        font-size: 1.7rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .player-tag {
        text-align: center;
        opacity: 0.65;
        margin-bottom: 12px;
    }

    .deck-title {
        font-size: 1.3rem;
        font-weight: 700;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .card-name {
        font-size: 0.78rem;
        text-align: center;
        font-weight: 600;
        min-height: 35px;
    }

    .card-level {
        text-align: center;
        font-size: 0.72rem;
        opacity: .75;
    }

    .comparison-title {
        text-align:center;
        font-weight:800;
        font-size:1.4rem;
        margin-top:25px;
        margin-bottom:15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def normalizar_tag(tag):
    """
    Aceita:
    P9RV222GG
    #P9RV222GG

    Retorna:
    #P9RV222GG
    """

    if not tag:
        return ""

    tag = tag.strip().upper().replace(" ", "")

    if not tag.startswith("#"):
        tag = "#" + tag

    return tag


def buscar_jogador(tag):
    """
    Consulta o seu proxy, nunca diretamente a API da Supercell.
    """

    if not PROXY_SECRET:
        return None, (
            "PROXY_SECRET não foi encontrado. "
            "Configure-o nos Secrets do Streamlit ou nas variáveis de ambiente."
        )

    tag = normalizar_tag(tag)

    if not tag or tag == "#":
        return None, "Informe uma TAG válida."

    tag_codificada = quote(tag, safe="")

    if not PROXY_API_URL:
        return None, (
            "PROXY_API_URL não foi encontrada nos Secrets do Streamlit "
            "ou nas variáveis de ambiente."
        )

    url = f"{PROXY_API_URL.rstrip('/')}/v1/players/{tag_codificada}"

    headers = {
        "X-Proxy-Token": PROXY_SECRET,
        "Accept": "application/json",
    }

    try:
        resposta = requests.get(
            url,
            headers=headers,
            timeout=15
        )

    except requests.exceptions.Timeout:
        return None, "O servidor demorou demais para responder."

    except requests.exceptions.ConnectionError:
        return None, "Não foi possível conectar ao servidor proxy."

    except requests.exceptions.RequestException as erro:
        return None, f"Erro de comunicação: {erro}"

    if resposta.status_code == 200:
        try:
            return resposta.json(), None
        except ValueError:
            return None, "O servidor retornou uma resposta inválida."

    if resposta.status_code == 401:
        return None, "Acesso não autorizado ao proxy."

    if resposta.status_code == 403:
        return None, "Acesso negado pelo proxy."

    if resposta.status_code == 404:
        return None, "Jogador não encontrado. Confira a TAG."

    if resposta.status_code == 429:
        return None, "Muitas consultas em pouco tempo. Tente novamente em alguns instantes."

    if resposta.status_code >= 500:
        return None, f"O servidor apresentou erro {resposta.status_code}."

    return None, f"Erro HTTP {resposta.status_code}."


def obter_nome_arena(jogador):
    arena = jogador.get("arena")

    if isinstance(arena, dict):
        return arena.get("name", "Não informado")

    return "Não informado"


def obter_nome_cla(jogador):
    cla = jogador.get("clan")

    if isinstance(cla, dict):
        return cla.get("name", "Sem clã")

    return "Sem clã"


def calcular_taxa_vitoria(jogador):
    wins = jogador.get("wins", 0) or 0
    losses = jogador.get("losses", 0) or 0

    total = wins + losses

    if total == 0:
        return 0

    return (wins / total) * 100


def calcular_elixir_medio(deck):
    if not deck:
        return 0

    custos = []

    for carta in deck:
        custo = carta.get("elixirCost")

        if isinstance(custo, (int, float)):
            custos.append(custo)

    if not custos:
        return 0

    return sum(custos) / len(custos)


def obter_url_imagem(carta):
    """
    A API normalmente fornece iconUrls.medium.
    """

    icon_urls = carta.get("iconUrls", {})

    if not isinstance(icon_urls, dict):
        return None

    return (
        icon_urls.get("medium")
        or icon_urls.get("evolutionMedium")
    )


def numero(valor):
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


# ============================================================
# EXIBIÇÃO DO PERFIL
# ============================================================

def mostrar_perfil(jogador):

    nome = jogador.get("name", "Jogador")
    tag = jogador.get("tag", "")
    trofeus = jogador.get("trophies", 0)
    melhor = jogador.get("bestTrophies", 0)
    nivel = jogador.get("expLevel", "-")
    wins = jogador.get("wins", 0)
    losses = jogador.get("losses", 0)
    battles = jogador.get("battleCount", 0)

    arena = obter_nome_arena(jogador)
    cla = obter_nome_cla(jogador)
    winrate = calcular_taxa_vitoria(jogador)

    st.markdown(
        f"""
        <div class="player-card">
            <div class="player-name">{nome}</div>
            <div class="player-tag">{tag}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🏆 Troféus", numero(trofeus))
        st.metric("⚔️ Vitórias", numero(wins))
        st.metric("🎮 Batalhas", numero(battles))

    with col2:
        st.metric("🏅 Recorde", numero(melhor))
        st.metric("💀 Derrotas", numero(losses))
        st.metric("📊 Taxa de vitória", f"{winrate:.1f}%")

    st.write(f"👑 **Nível:** {nivel}")
    st.write(f"🏟️ **Arena:** {arena}")
    st.write(f"🛡️ **Clã:** {cla}")


# ============================================================
# EXIBIÇÃO DO DECK
# ============================================================

def mostrar_deck(jogador):

    deck = jogador.get("currentDeck", [])

    if not deck:
        st.warning("Deck atual não disponível.")
        return

    elixir = calcular_elixir_medio(deck)

    st.markdown(
        '<div class="deck-title">🃏 Deck atual</div>',
        unsafe_allow_html=True
    )

    primeira_linha = deck[:4]
    segunda_linha = deck[4:8]

    for linha in [primeira_linha, segunda_linha]:

        cols = st.columns(4)

        for coluna, carta in zip(cols, linha):

            with coluna:

                imagem = obter_url_imagem(carta)

                if imagem:
                    st.image(
                        imagem,
                        use_container_width=True
                    )

                nome = carta.get("name", "Carta")
                nivel = carta.get("level", "?")
                max_level = carta.get("maxLevel")

                st.markdown(
                    f'<div class="card-name">{nome}</div>',
                    unsafe_allow_html=True
                )

                texto_nivel = f"Nível {nivel}"

                if max_level:
                    texto_nivel += f" / {max_level}"

                st.markdown(
                    f'<div class="card-level">{texto_nivel}</div>',
                    unsafe_allow_html=True
                )

    st.metric(
        "💧 Elixir médio",
        f"{elixir:.1f}"
    )


# ============================================================
# COMPARAÇÕES
# ============================================================

def vencedor_visual(valor1, valor2):

    if valor1 > valor2:
        return "⬅️"

    if valor2 > valor1:
        return "➡️"

    return "🤝"


def mostrar_comparacao(j1, j2):

    st.markdown(
        '<div class="comparison-title">📊 Comparação direta</div>',
        unsafe_allow_html=True
    )

    dados = [
        (
            "Troféus",
            j1.get("trophies", 0),
            j2.get("trophies", 0)
        ),
        (
            "Recorde de troféus",
            j1.get("bestTrophies", 0),
            j2.get("bestTrophies", 0)
        ),
        (
            "Vitórias",
            j1.get("wins", 0),
            j2.get("wins", 0)
        ),
        (
            "Nível",
            j1.get("expLevel", 0),
            j2.get("expLevel", 0)
        ),
        (
            "Taxa de vitória",
            calcular_taxa_vitoria(j1),
            calcular_taxa_vitoria(j2)
        ),
    ]

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    col_nome1, col_indicador, col_nome2 = st.columns(
        [2, 1, 2]
    )

    with col_nome1:
        st.markdown(f"### {nome1}")

    with col_indicador:
        st.markdown("### VS")

    with col_nome2:
        st.markdown(f"### {nome2}")

    for titulo, valor1, valor2 in dados:

        c1, meio, c2 = st.columns([2, 1, 2])

        if titulo == "Taxa de vitória":

            texto1 = f"{valor1:.1f}%"
            texto2 = f"{valor2:.1f}%"

        else:

            texto1 = numero(valor1)
            texto2 = numero(valor2)

        with c1:
            st.metric(titulo, texto1)

        with meio:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:1.6rem;
                    padding-top:32px;
                ">
                    {vencedor_visual(valor1, valor2)}
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.metric(titulo, texto2)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="main-title">⚔️ Jogador X Jogador</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Compare dois jogadores de Clash Royale e seus decks lado a lado.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FORMULÁRIO
# ============================================================

with st.form("comparacao_jogadores"):

    coluna1, coluna2 = st.columns(2)

    with coluna1:

        tag1 = st.text_input(
            "TAG do Jogador 1",
            placeholder="#P9RV222GG",
        )

    with coluna2:

        tag2 = st.text_input(
            "TAG do Jogador 2",
            placeholder="#XXXXXXXXX",
        )

    comparar = st.form_submit_button(
        "⚔️ COMPARAR JOGADORES",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# PROCESSAMENTO
# ============================================================

if comparar:

    if not tag1 or not tag2:

        st.warning(
            "Informe as duas TAGs para realizar a comparação."
        )

        st.stop()

    tag1_normalizada = normalizar_tag(tag1)
    tag2_normalizada = normalizar_tag(tag2)

    if tag1_normalizada == tag2_normalizada:

        st.warning(
            "Informe duas TAGs diferentes para realizar a comparação."
        )

        st.stop()

    with st.spinner("Buscando os dois jogadores..."):

        jogador1, erro1 = buscar_jogador(tag1_normalizada)
        jogador2, erro2 = buscar_jogador(tag2_normalizada)

    if erro1:

        st.error(
            f"Erro ao consultar Jogador 1: {erro1}"
        )

    if erro2:

        st.error(
            f"Erro ao consultar Jogador 2: {erro2}"
        )

    if erro1 or erro2:
        st.stop()

    # ========================================================
    # VISUALIZAÇÃO EM ABAS
    # ========================================================

    st.divider()

    nome1 = jogador1.get("name", "Jogador 1")
    nome2 = jogador2.get("name", "Jogador 2")

    aba_jogador1, aba_jogador2, aba_comparacao = st.tabs(
        [
            f"👤 {nome1}",
            f"👤 {nome2}",
            "⚔️ Comparação"
        ]
    )

    # --------------------------------------------------------
    # ABA JOGADOR 1
    # --------------------------------------------------------

    with aba_jogador1:

        mostrar_perfil(jogador1)

        st.divider()

        mostrar_deck(jogador1)

    # --------------------------------------------------------
    # ABA JOGADOR 2
    # --------------------------------------------------------

    with aba_jogador2:

        mostrar_perfil(jogador2)

        st.divider()

        mostrar_deck(jogador2)

    # --------------------------------------------------------
    # ABA COMPARAÇÃO
    # --------------------------------------------------------

    with aba_comparacao:

        mostrar_comparacao(
            jogador1,
            jogador2
        )

        st.divider()

        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:1.5rem;
                font-weight:800;
                margin-bottom:20px;
            ">
                🃏 Deck X Deck
            </div>
            """,
            unsafe_allow_html=True
        )

        coluna_deck1, coluna_deck2 = st.columns(
            2,
            gap="large"
        )

        with coluna_deck1:

            st.markdown(
                f"### {nome1}"
            )

            mostrar_deck(jogador1)

        with coluna_deck2:

            st.markdown(
                f"### {nome2}"
            )

            mostrar_deck(jogador2)

        st.divider()

        st.info(
            "💡 Próxima evolução: analisar automaticamente os dois decks, "
            "identificar counters, condições de vitória, defesa aérea, "
            "ciclo, feitiços, construções e vantagem de matchup."
        )
