import streamlit as st
import requests

st.set_page_config(
    page_title="Jogador vs Jogador",
    page_icon="⚔️",
    layout="wide"
)

st.title("⚔️ Jogador X Jogador")
st.caption("Compare dois jogadores e seus decks lado a lado.")

col_tag1, col_tag2 = st.columns(2)

with col_tag1:
    tag1 = st.text_input(
        "TAG do Jogador 1",
        placeholder="#P9RV222GG"
    )

with col_tag2:
    tag2 = st.text_input(
        "TAG do Jogador 2",
        placeholder="#XXXXXXXXX"
    )

comparar = st.button(
    "🔎 Comparar jogadores",
    use_container_width=True,
    type="primary"
)
