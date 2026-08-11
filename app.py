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

# Descobre o IPv4 público exato e válido do servidor na nuvem
try:
    server_ip = requests.get('https://v4.ident.me', timeout=5).text.strip()
except Exception:
    try:
        server_ip = requests.get('https://api4.ipify.org', timeout=5).text.strip()
    except Exception:
        server_ip = "Indisponível"

# Carrega a chave de API (.env para local, Secrets para a nuvem)
load_dotenv()
API_KEY = os.getenv('CLASH_ROYALE_API_KEY')

# Título da aplicação
st.title("👑 Clash Royale - Dashboard de Jogador")
st.markdown("Insira a **Tag do Jogador** para visualizar o perfil, tempo de conta e estatísticas.")

# Exibe o IPv4 verificado para cadastrar no portal da Supercell
st.info(f"🌐 **IPv4 do seu servidor:** `{server_ip}` — *Cadastre este IP no portal de desenvolvedores da Supercell.*")

# Campo de busca no topo
player_tag_input = st.text_input("Tag do Jogador:", value="#P9RV222GG", help="Exemplo: #P9RV222GG ou P9RV222GG")

if st.button("Buscar Dados", type="primary") or player_tag_input:
    if not API_KEY:
        st.error("Erro: Chave de API não encontrada no arquivo .env ou nos Secrets do Streamlit!")
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

                # --- 1. LÓGICA DE TEMPO DE CONTA ---
                years_played = "Não identificado"

                badges = data.get('badges', [])
                for badge in badges:
                    badge_name = badge.get('name', '')
                    if 'Years' in badge_name or 'years' in badge_name or 'Played' in badge_name:
                        val = badge.get('progress', badge.get('level', 0))
                        if val > 100:
                            anos = val // 365
                            meses = (val % 365) // 30
                            years_played = f"{anos}a {meses}m ({val}d)"
                        else:
                            years_played = f"{val} anos"
                        break

                if years_played == "Não identificado":
                    achievements = data.get('achievements', [])
                    for ach in achievements:
                        ach_name = ach.get('name', '')
                        if 'Years' in ach_name or 'Poker' in ach_name:
                            val = ach.get('value', 0)
                            if val > 100:
                                anos = val // 365
                                years_played = f"{anos} anos"
                            else:
                                years_played = f"{val} anos"
                            break

                # --- 2. CABEÇALHO DO JOGADOR ---
                st.divider()
                st.header(f"🎮 {data.get('name')} ({data.get('tag')})")
                
                clan_name = data['clan']['name'] if 'clan' in data else 'Sem Clã'
                st.caption(f"🛡️ Clã: **{clan_name}** | Nível do Rei: **{data.get('expLevel')}** | ⏳ Tempo de Jogo: **{years_played}**")

                # --- 3. CÁLCULO DE ESTATÍSTICAS ---
                wins = data.get('wins', 0)
                losses = data.get('losses', 0)
                battle_count = data.get('battleCount', wins + losses)
                
                winrate = (wins / battle_count * 100) if battle_count > 0 else 0.0

                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.metric("Troféus Atuais", data.get('trophies', 0))
                col2.metric("Recorde Troféus", data.get('bestTrophies', 0))
                col3.metric("Vitórias", wins)
                col4.metric("Derrotas 💔", losses)
                col5.metric("Winrate", f"{winrate:.1f}%")
                col6.metric("Tempo de Conta", years_played)

                st.divider()

                # --- 4. DECK ATUAL (VISUAL HUMANIZADO) ---
                st.subheader("⚔️ Deck Batalha Atual")

                with st.popover("ℹ️ Como os níveis das cartas são calculados?"):
                    st.markdown("""
                    Dentro do Clash Royale, cada raridade de carta começa em um nível base diferente na API:
                    
                    * ⚪ **Comum:** Nível inicial 1
                    * 🟠 **Rara:** Nível inicial 3
                    * 🟣 **Épica:** Nível inicial 6
                    * 🟡 **Lendária:** Nível inicial 9
                    * 🔴 **Campeão:** Nível inicial 11
                    
                    Nosso sistema converte o nível interno da API para o **Nível de Batalha Real (1 ao 15)**.
                    """)

                current_deck = data.get('currentDeck', [])
                if current_deck:
                    cols = st.columns(8)
                    for idx, card in enumerate(current_deck):
                        with cols[idx]:
                            icon_url = card.get('iconUrls', {}).get('medium', '')
                            if icon_url:
                                st.image(icon_url, use_container_width=True)
                            
                            raw_level = card.get('level', 1)
                            max_level = card.get('maxLevel', 15)
                            real_level = 15 - (max_level - raw_level)
                            
                            min_level = max_level - 14
                            rarity_map = {
                                1: "⚪ Comum",
                                3: "🟠 Rara",
                                6: "🟣 Épica",
                                9: "🟡 Lendária",
                                11: "🔴 Campeão"
                            }
                            rarity_label = rarity_map.get(min_level, "Carta")

                            st.markdown(f"**{card.get('name')}**")
                            
                            if real_level == 15:
                                st.markdown("👑 **Nível 15** *(Elite)*")
                            else:
                                st.markdown(f"⭐ **Nível {real_level}**")
                                
                            st.caption(rarity_label)
                else:
                    st.info("Nenhum deck atual encontrado para este jogador.")

                st.divider()

                # --- 5. INSÍGNIAS E BADGES ---
                with st.expander("🏅 Ver Badges / Insígnias do Jogador"):
                    if badges:
                        badge_data = [{
                            "Nome": b.get('name'),
                            "Nível / Progresso": b.get('progress', b.get('level', 0)),
                            "Max": b.get('max', '-')
                        } for b in badges]
                        st.dataframe(pd.DataFrame(badge_data), use_container_width=True)

                # --- 6. TODAS AS CARTAS DESBLOQUEADAS ---
                with st.expander("📚 Ver todas as cartas da coleção do jogador"):
                    cards_data = []
                    for card in data.get('cards', []):
                        cards_data.append({
                            "Nome da Carta": card.get('name'),
                            "Nível": card.get('level'),
                            "Nível Máximo": card.get('maxLevel'),
                            "Contagem de Cartas": card.get('count', 0)
                        })
                    
                    df_cards = pd.DataFrame(cards_data)
                    st.dataframe(df_cards, use_container_width=True)

            except requests.exceptions.HTTPError as err:
                if response.status_code == 404:
                    st.error("Jogador não encontrado. Verifique a Tag informada.")
                elif response.status_code == 403:
                    st.error(f"Erro 403: Chave de API recusada. Verifique se o IP `{server_ip}` está cadastrado no portal da Supercell.")
                else:
                    st.error(f"Erro na requisição: {err}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")