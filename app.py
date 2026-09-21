import os
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Jogador vs Jogador",
    page_icon="⚔️",
    layout="wide"
)


# ============================================================
# CONFIGURAÇÃO DO PROXY
# ============================================================

load_dotenv()


def get_config(name):
    """
    Primeiro tenta ler dos Secrets do Streamlit.
    Se não encontrar, tenta variável de ambiente local.
    """
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name)


PROXY_API_URL = get_config("PROXY_API_URL")
PROXY_SECRET = get_config("PROXY_SECRET")


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .titulo-principal {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        text-align: center;
        opacity: 0.7;
        margin-bottom: 2rem;
    }

    .nome-jogador {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .tag-jogador {
        text-align: center;
        opacity: 0.65;
        margin-bottom: 1rem;
    }

    .deck-titulo {
        text-align: center;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .nome-carta {
        text-align: center;
        font-size: 0.80rem;
        font-weight: 700;
        min-height: 38px;
        margin-top: 4px;
    }

    .nivel-carta {
        text-align: center;
        font-size: 0.78rem;
        margin-top: 2px;
    }

    .raridade-carta {
        text-align: center;
        font-size: 0.70rem;
        opacity: 0.65;
    }

    .vs-central {
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        padding-top: 10px;
    }

    .secao-titulo {
        text-align: center;
        font-size: 1.7rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }

    .indicador {
        text-align: center;
        font-size: 1.6rem;
        padding-top: 32px;
    }

    </style>
    """,
    unsafe_allow_html=True
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


def formatar_numero(valor):
    """
    Exemplo:
    12345 -> 12.345
    """

    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def buscar_jogador(tag):
    """
    Consulta o nosso proxy.
    A página nunca acessa diretamente a API da Supercell.
    """

    if not PROXY_API_URL:
        return None, (
            "PROXY_API_URL não encontrada nos Secrets "
            "do Streamlit ou nas variáveis de ambiente."
        )

    if not PROXY_SECRET:
        return None, (
            "PROXY_SECRET não encontrada nos Secrets "
            "do Streamlit ou nas variáveis de ambiente."
        )

    tag = normalizar_tag(tag)

    if not tag or tag == "#":
        return None, "Informe uma TAG válida."

    encoded_tag = quote(tag, safe="")

    url = (
        f"{PROXY_API_URL.rstrip('/')}"
        f"/v1/players/{encoded_tag}"
    )

    headers = {
        "Accept": "application/json",
        "X-Proxy-Token": PROXY_SECRET
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code == 200:

            try:
                return response.json(), None

            except ValueError:
                return None, (
                    "O servidor respondeu, mas os dados "
                    "recebidos não são JSON válido."
                )

        if response.status_code == 404:
            return None, (
                f"Jogador {tag} não encontrado. "
                "Confira a TAG informada."
            )

        if response.status_code == 401:
            return None, (
                "O proxy recusou a autenticação. "
                "Verifique o PROXY_SECRET."
            )

        if response.status_code == 403:
            return None, (
                "A requisição foi recusada. "
                "Verifique o PROXY_SECRET ou a configuração "
                "da chave da Supercell na VM."
            )

        if response.status_code == 429:
            return None, (
                "Muitas consultas foram realizadas em pouco tempo. "
                "Tente novamente em alguns instantes."
            )

        if response.status_code >= 500:
            return None, (
                f"O servidor proxy retornou o erro "
                f"{response.status_code}."
            )

        return None, (
            f"A consulta retornou o erro HTTP "
            f"{response.status_code}."
        )

    except requests.exceptions.Timeout:

        return None, (
            "A comunicação com o servidor demorou "
            "mais que o esperado."
        )

    except requests.exceptions.ConnectionError:

        return None, (
            "Não foi possível conectar ao servidor proxy."
        )

    except requests.exceptions.RequestException as erro:

        return None, (
            f"Erro de comunicação com o servidor: {erro}"
        )

    except Exception as erro:

        return None, (
            f"Ocorreu um erro inesperado: {erro}"
        )


# ============================================================
# TEMPO DE CONTA
# ============================================================

def calcular_tempo_conta(jogador):

    years_played = "Não identificado"

    badges = jogador.get("badges", [])

    for badge in badges:

        badge_name = badge.get("name", "")

        if (
            "Years" in badge_name
            or "years" in badge_name
            or "Played" in badge_name
        ):

            valor = badge.get(
                "progress",
                badge.get("level", 0)
            )

            try:
                valor = int(valor)
            except (TypeError, ValueError):
                valor = 0

            if valor > 100:

                anos = valor // 365
                meses = (valor % 365) // 30

                years_played = (
                    f"{anos}a {meses}m"
                )

            elif valor > 0:

                years_played = (
                    f"{valor} anos"
                )

            break

    if years_played == "Não identificado":

        achievements = jogador.get(
            "achievements",
            []
        )

        for achievement in achievements:

            nome = achievement.get("name", "")

            if (
                "Years" in nome
                or "Poker" in nome
            ):

                valor = achievement.get(
                    "value",
                    0
                )

                try:
                    valor = int(valor)
                except (TypeError, ValueError):
                    valor = 0

                if valor > 100:

                    anos = valor // 365

                    years_played = (
                        f"{anos} anos"
                    )

                elif valor > 0:

                    years_played = (
                        f"{valor} anos"
                    )

                break

    return years_played


# ============================================================
# DADOS DO JOGADOR
# ============================================================

def obter_nome_arena(jogador):

    arena = jogador.get("arena")

    if isinstance(arena, dict):
        return arena.get(
            "name",
            "Não informado"
        )

    return "Não informado"


def obter_nome_cla(jogador):

    clan = jogador.get("clan")

    if isinstance(clan, dict):

        return clan.get(
            "name",
            "Sem Clã"
        )

    return "Sem Clã"


def calcular_winrate(jogador):

    wins = jogador.get("wins", 0) or 0
    losses = jogador.get("losses", 0) or 0

    total = wins + losses

    if total == 0:
        return 0.0

    return wins / total * 100


# ============================================================
# CARTAS
# ============================================================

def calcular_nivel_real(card):
    """
    Converte o nível interno retornado pela API
    para o nível de batalha real.
    """

    raw_level = card.get(
        "level",
        1
    )

    max_level = card.get(
        "maxLevel",
        15
    )

    try:

        raw_level = int(raw_level)
        max_level = int(max_level)

        real_level = (
            15 - (
                max_level - raw_level
            )
        )

        return real_level

    except (TypeError, ValueError):

        return raw_level


def obter_raridade(card):

    max_level = card.get(
        "maxLevel",
        15
    )

    try:
        max_level = int(max_level)
    except (TypeError, ValueError):
        return "Carta"

    min_level = max_level - 14

    rarity_map = {
        1: "⚪ Comum",
        3: "🟠 Rara",
        6: "🟣 Épica",
        9: "🟡 Lendária",
        11: "🔴 Campeão"
    }

    return rarity_map.get(
        min_level,
        "Carta"
    )


def obter_imagem_carta(card):

    icon_urls = card.get(
        "iconUrls",
        {}
    )

    if not isinstance(icon_urls, dict):
        return None

    return (
        icon_urls.get("medium")
        or icon_urls.get("evolutionMedium")
    )


# ============================================================
# ELIXIR
# ============================================================

def calcular_elixir_medio(deck):

    if not deck:
        return None

    custos = []

    for carta in deck:

        custo = carta.get(
            "elixirCost"
        )

        if isinstance(
            custo,
            (int, float)
        ):

            custos.append(custo)

    if not custos:
        return None

    return (
        sum(custos)
        / len(custos)
    )


# ============================================================
# PERFIL DO JOGADOR
# ============================================================

def mostrar_perfil(jogador):

    nome = jogador.get(
        "name",
        "Jogador"
    )

    tag = jogador.get(
        "tag",
        ""
    )

    trofeus = jogador.get(
        "trophies",
        0
    )

    recorde = jogador.get(
        "bestTrophies",
        0
    )

    nivel = jogador.get(
        "expLevel",
        "-"
    )

    wins = jogador.get(
        "wins",
        0
    )

    losses = jogador.get(
        "losses",
        0
    )

    batalhas = jogador.get(
        "battleCount",
        wins + losses
    )

    arena = obter_nome_arena(
        jogador
    )

    cla = obter_nome_cla(
        jogador
    )

    winrate = calcular_winrate(
        jogador
    )

    tempo_conta = calcular_tempo_conta(
        jogador
    )

    st.markdown(
        f"""
        <div class="nome-jogador">
            {nome}
        </div>

        <div class="tag-jogador">
            {tag}
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🏆 Troféus",
            formatar_numero(
                trofeus
            )
        )

        st.metric(
            "⚔️ Vitórias",
            formatar_numero(
                wins
            )
        )

        st.metric(
            "🎮 Batalhas",
            formatar_numero(
                batalhas
            )
        )

    with col2:

        st.metric(
            "🏅 Recorde",
            formatar_numero(
                recorde
            )
        )

        st.metric(
            "💔 Derrotas",
            formatar_numero(
                losses
            )
        )

        st.metric(
            "📊 Winrate",
            f"{winrate:.1f}%"
        )

    st.markdown(
        f"👑 **Nível do Rei:** {nivel}"
    )

    st.markdown(
        f"🏟️ **Arena:** {arena}"
    )

    st.markdown(
        f"🛡️ **Clã:** {cla}"
    )

    st.markdown(
        f"⏳ **Tempo de conta:** {tempo_conta}"
    )


# ============================================================
# DECK
# ============================================================

def mostrar_deck(jogador):

    deck = jogador.get(
        "currentDeck",
        []
    )

    if not deck:

        st.info(
            "Nenhum deck atual encontrado "
            "para este jogador."
        )

        return

    st.markdown(
        '<div class="deck-titulo">🃏 Deck Atual</div>',
        unsafe_allow_html=True
    )

    primeira_linha = deck[:4]
    segunda_linha = deck[4:8]

    for linha in [
        primeira_linha,
        segunda_linha
    ]:

        cols = st.columns(4)

        for coluna, carta in zip(
            cols,
            linha
        ):

            with coluna:

                imagem = obter_imagem_carta(
                    carta
                )

                if imagem:

                    st.image(
                        imagem,
                        use_container_width=True
                    )

                nome = carta.get(
                    "name",
                    "Carta"
                )

                nivel_real = calcular_nivel_real(
                    carta
                )

                raridade = obter_raridade(
                    carta
                )

                st.markdown(
                    f"""
                    <div class="nome-carta">
                        {nome}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if nivel_real == 15:

                    st.markdown(
                        """
                        <div class="nivel-carta">
                            👑 <b>Nível 15</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div class="nivel-carta">
                            ⭐ <b>Nível {nivel_real}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f"""
                    <div class="raridade-carta">
                        {raridade}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    elixir = calcular_elixir_medio(
        deck
    )

    if elixir is not None:

        st.metric(
            "💧 Elixir médio",
            f"{elixir:.1f}"
        )

    else:

        st.caption(
            "💧 Custo médio de elixir ainda "
            "não disponível nesta resposta da API."
        )


# ============================================================
# COMPARAÇÃO DIRETA
# ============================================================

def indicador_comparacao(
    valor1,
    valor2
):

    if valor1 > valor2:
        return "⬅️"

    if valor2 > valor1:
        return "➡️"

    return "🤝"


def mostrar_comparacao(
    jogador1,
    jogador2
):

    nome1 = jogador1.get(
        "name",
        "Jogador 1"
    )

    nome2 = jogador2.get(
        "name",
        "Jogador 2"
    )

    dados = [

        (
            "Troféus",
            jogador1.get(
                "trophies",
                0
            ),
            jogador2.get(
                "trophies",
                0
            ),
            "numero"
        ),

        (
            "Recorde de Troféus",
            jogador1.get(
                "bestTrophies",
                0
            ),
            jogador2.get(
                "bestTrophies",
                0
            ),
            "numero"
        ),

        (
            "Vitórias",
            jogador1.get(
                "wins",
                0
            ),
            jogador2.get(
                "wins",
                0
            ),
            "numero"
        ),

        (
            "Nível do Rei",
            jogador1.get(
                "expLevel",
                0
            ),
            jogador2.get(
                "expLevel",
                0
            ),
            "numero"
        ),

        (
            "Winrate",
            calcular_winrate(
                jogador1
            ),
            calcular_winrate(
                jogador2
            ),
            "percentual"
        )
    ]

    st.markdown(
        """
        <div class="secao-titulo">
            📊 Comparação Direta
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [2, 1, 2]
    )

    with col1:

        st.markdown(
            f"### {nome1}"
        )

    with col2:

        st.markdown(
            """
            <div class="vs-central">
                VS
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"### {nome2}"
        )

    for (
        titulo,
        valor1,
        valor2,
        formato
    ) in dados:

        esquerda, centro, direita = (
            st.columns(
                [2, 1, 2]
            )
        )

        if formato == "percentual":

            texto1 = (
                f"{valor1:.1f}%"
            )

            texto2 = (
                f"{valor2:.1f}%"
            )

        else:

            texto1 = formatar_numero(
                valor1
            )

            texto2 = formatar_numero(
                valor2
            )

        with esquerda:

            st.metric(
                titulo,
                texto1
            )

        with centro:

            indicador = (
                indicador_comparacao(
                    valor1,
                    valor2
                )
            )

            st.markdown(
                f"""
                <div class="indicador">
                    {indicador}
                </div>
                """,
                unsafe_allow_html=True
            )

        with direita:

            st.metric(
                titulo,
                texto2
            )


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="titulo-principal">
        ⚔️ Jogador X Jogador
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitulo">
        Compare dois jogadores de Clash Royale,
        suas estatísticas e seus decks.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# VERIFICAÇÃO DA CONFIGURAÇÃO
# ============================================================

if not PROXY_API_URL:

    st.error(
        "PROXY_API_URL não foi encontrada. "
        "Verifique os Secrets do Streamlit."
    )

    st.stop()


if not PROXY_SECRET:

    st.error(
        "PROXY_SECRET não foi encontrada. "
        "Verifique os Secrets do Streamlit."
    )

    st.stop()


# ============================================================
# FORMULÁRIO
# ============================================================

with st.form(
    "form_comparacao"
):

    col_tag1, col_tag2 = (
        st.columns(2)
    )

    with col_tag1:

        tag1 = st.text_input(
            "TAG do Jogador 1",
            value="#P9RV222GG",
            help=(
                "Exemplo: #P9RV222GG "
                "ou P9RV222GG"
            )
        )

    with col_tag2:

        tag2 = st.text_input(
            "TAG do Jogador 2",
            placeholder="#XXXXXXXXX",
            help=(
                "Informe a TAG do segundo jogador."
            )
        )

    comparar = st.form_submit_button(
        "⚔️ Comparar Jogadores",
        type="primary",
        use_container_width=True
    )


# ============================================================
# PROCESSAMENTO
# ============================================================

if comparar:

    if not tag1 or not tag2:

        st.warning(
            "Informe as duas TAGs "
            "para realizar a comparação."
        )

        st.stop()

    tag1_normalizada = (
        normalizar_tag(
            tag1
        )
    )

    tag2_normalizada = (
        normalizar_tag(
            tag2
        )
    )

    if (
        tag1_normalizada
        == tag2_normalizada
    ):

        st.warning(
            "Informe duas TAGs diferentes."
        )

        st.stop()

    with st.spinner(
        "Buscando os dois jogadores..."
    ):

        jogador1, erro1 = (
            buscar_jogador(
                tag1_normalizada
            )
        )

        jogador2, erro2 = (
            buscar_jogador(
                tag2_normalizada
            )
        )

    if erro1:

        st.error(
            f"Jogador 1: {erro1}"
        )

    if erro2:

        st.error(
            f"Jogador 2: {erro2}"
        )

    if erro1 or erro2:

        st.stop()


    # ========================================================
    # PERFIS
    # ========================================================

    st.divider()

    coluna1, coluna2 = (
        st.columns(
            2,
            gap="large"
        )
    )

    with coluna1:

        mostrar_perfil(
            jogador1
        )

    with coluna2:

        mostrar_perfil(
            jogador2
        )


    # ========================================================
    # DECK X DECK
    # ========================================================

    st.divider()

    st.markdown(
        """
        <div class="secao-titulo">
            🃏 Deck X Deck
        </div>
        """,
        unsafe_allow_html=True
    )

    deck1, deck2 = st.columns(
        2,
        gap="large"
    )

    with deck1:

        st.markdown(
            f"### {jogador1.get('name', 'Jogador 1')}"
        )

        mostrar_deck(
            jogador1
        )

    with deck2:

        st.markdown(
            f"### {jogador2.get('name', 'Jogador 2')}"
        )

        mostrar_deck(
            jogador2
        )


    # ========================================================
    # COMPARAÇÃO ESTATÍSTICA
    # ========================================================

    st.divider()

    mostrar_comparacao(
        jogador1,
        jogador2
    )


    # ========================================================
    # PRÓXIMA EVOLUÇÃO
    # ========================================================

    st.divider()

    with st.expander(
        "🧠 Próxima etapa: Inteligência de Deck"
    ):

        st.markdown(
            """
            A próxima evolução desta tela será analisar
            automaticamente os dois decks e mostrar:

            - condição de vitória;
            - custo médio de elixir;
            - ciclo;
            - tropas;
            - feitiços;
            - construções;
            - defesa aérea;
            - dano em área;
            - cartas de reset;
            - counters entre os decks;
            - principais ameaças;
            - vantagens e vulnerabilidades de cada deck.
            """
        )
