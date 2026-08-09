import os
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Clash Royale Dashboard",
    page_icon="👑",
    layout="wide"
)

# Carrega a chave de API do .env
load_dotenv()
API_KEY = os.getenv('CLASH_ROYALE_API_KEY')

# Título da aplicação
st.title("👑 Clash Royale - Dashboard de Jogador")
st.markdown("Insira a **Tag do Jogador** para visualizar o perfil, estatísticas e deck atual.")

# Campo de busca no topo
player_tag_input = st.text_input("Tag do Jogador:", value="#P9RV222GG", help="Exemplo: #P9RV222GG ou P9RV222GG")

if st.button("Buscar Dados", type="primary") or player_tag_input:
    if not API_KEY:
        st.error("Erro: Chave de API não encontrada no arquivo .env!")
    else:
        # Tratamento da Tag (# -> %23)
        formatted_tag = player_tag_input.strip()
        if not formatted_tag.startswith("#"):
            formatted_tag = "#" + formatted_tag
        encoded_tag = formatted_tag.replace("#", "%23")

        # Requisição para a API
        url = f"https://api.clashroyale.com/v1/players/{encoded_tag}"
        headers = {
            "Accept": "application/json",
            "authorization": f"Bearer {API_KEY}"
        }

        with st.spinner("Buscando dados na API do Clash Royale..."):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                # --- 1. CABEÇALHO DO JOGADOR ---
                st.divider()
                st.header(f"🎮 {data.get('name')} ({data.get('tag')})")
                
                clan_name = data['clan']['name'] if 'clan' in data else 'Sem Clã'
                st.caption(f"🛡️ Clã: **{clan_name}** | Nível do Rei: **{data.get('expLevel')}**")

                # --- 2. MÉTRICAS PRINCIPAIS (Cartões) ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Troféus Atuais", data.get('trophies', 0))
                col2.metric("Recorde de Troféus", data.get('bestTrophies', 0))
                col3.metric("Vitórias", data.get('wins', 0))
                col4.metric("Vitórias em 3 Coroas", data.get('threeCrownWins', 0))

                # --- 3. CARTAS / DECK DO JOGADOR ---
                st.subheader("🃏 Deck Atual e Cartas")
                
                cards_data = []
                for card in data.get('cards', []):
                    cards_data.append({
                        "Nome da Carta": card.get('name'),
                        "Nível": card.get('level'),
                        "Nível Máximo": card.get('maxLevel'),
                        "Contagem de Cartas": card.get('count', 0)
                    })
                
                # Exibe como uma tabela limpa e interativa
                df_cards = pd.DataFrame(cards_data)
                st.dataframe(df_cards, use_container_width=True)

            except requests.exceptions.HTTPError as err:
                if response.status_code == 404:
                    st.error("Jogador não encontrado. Verifique a Tag informada.")
                elif response.status_code == 403:
                    st.error("Erro 403: Chave de API recusada. Verifique seu IP no portal de desenvolvedores do Clash Royale.")
                else:
                    st.error(f"Erro na requisição: {err}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")