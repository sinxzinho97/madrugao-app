import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random
import matplotlib.pyplot as plt
import io
import os
import time

# --- CONFIGURAÇÕES DE PÁGINA ---
icone_aba = "logo.png" if os.path.exists("logo.png") else "🦉"
st.set_page_config(
    page_title="Pelada Madrugão", 
    page_icon=icone_aba, 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- NOVO DESIGN PROFISSIONAL (CSS) ---
st.markdown("""
    <style>
    /* Importação de Fonte */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Esconder Menu Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Background e Cards */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Estilização das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161B22;
        padding: 10px 15px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 8px;
        color: #8B949E;
        border: none;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: white !important;
    }

    /* Container de Lista Profissional */
    .zebra-row {
        padding: 12px 18px;
        margin-bottom: 8px;
        border-radius: 10px;
        background: #161B22;
        border-left: 4px solid transparent;
        transition: 0.3s;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .zebra-row:hover {
        transform: translateX(5px);
        background: #1C2128;
    }
    
    /* Variantes de Borda por Time/Status */
    .box-verde { border-left-color: #238636; }
    .box-preto { border-left-color: #30363D; }
    .box-ouro { border-left-color: #D29922; }
    .box-azul { border-left-color: #1F6FEB; }
    .box-vermelho { border-left-color: #F85149; }

    /* Estilo dos Botões */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: 0.3s;
    }
    
    /* Títulos e Destaques */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#238636, #42b883);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    
    .stat-card {
        background: #161B22;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #30363D;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE RENDERIZAÇÃO ATUALIZADA ---
def render_html_list(titulo, items, cor_classe="box-padrao", cor_titulo="#FFF"):
    st.markdown(f"<h3 style='color:{cor_titulo}; font-size: 1.2rem; margin-bottom:15px;'>{titulo}</h3>", unsafe_allow_html=True)
    html = "<div style='margin-bottom: 30px;'>"
    for item in items:
        if isinstance(item, tuple):
            texto, valor = item
            html += f"""
            <div class='zebra-row {cor_classe}'>
                <span style='color:#C9D1D9'>{texto}</span>
                <span style='color:white; font-weight:bold; background:#30363D; padding: 2px 8px; border-radius:5px;'>{valor}</span>
            </div>"""
        else:
            html += f"<div class='zebra-row {cor_classe}'><span style='color:#C9D1D9'>{item}</span></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# --- HEADER CUSTOMIZADO ---
c_title, c_logo = st.columns([4, 1])
with c_title:
    st.markdown("<h1 class='main-title'>Pelada Madrugão 🦉</h1>", unsafe_allow_html=True)
with c_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)

# (Mantenha o restante das funções de conexão e lógica do sistema como estão...)
