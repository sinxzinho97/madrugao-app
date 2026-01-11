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

# --- CSS PROFISSIONAL (DARK MODE & MODERN UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #0E1117;
    }
    
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
    
    .box-verde { border-left-color: #238636; }
    .box-preto { border-left-color: #F0F6FC; }
    .box-ouro { border-left-color: #D29922; }
    .box-azul { border-left-color: #1F6FEB; }
    .box-vermelho { border-left-color: #F85149; }

    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: 0.3s;
    }
    
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
    
    .destaque-titulo {
        color: #8B949E;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: block;
    }
    
    .destaque-valor {
        color: white;
        font-size: 2rem;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE RENDERIZAÇÃO ---
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

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# --- HEADER ---
c_title, c_logo = st.columns([4, 1])
with c_title:
    st.markdown("<h1 class='main-title'>Pelada Madrugão 🦉</h1>", unsafe_allow_html=True)

# --- CONEXÃO INTELIGENTE (CACHE) ---
@st.cache_resource
def get_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
    return client.open_by_key("1OSxEwiE3voMOd-EI6CJ034torY-K7oFoz8EReyXkmPA")

# --- LEITURA DE DADOS (CACHE) ---
@st.cache_data(ttl=60)
def load_data(sheet_name, expected_cols):
    try:
        sh = get_connection()
        try:
            worksheet = sh.worksheet(sheet_name)
        except:
            return pd.DataFrame(columns=expected_cols) 
        data = worksheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=expected_cols)
        df = pd.DataFrame(data)
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        
        # --- CORREÇÃO DO BUG "NONE" ---
        if "time" in df.columns: df["time"] = df["time"].replace("", "Ambos").fillna("Ambos")
        if "tipo" in df.columns: df["tipo"] = df["tipo"].replace("", "Mensalista").fillna("Mensalista")
        if "punicao" in df.columns: df["punicao"] = df["punicao"].replace("", "Não").fillna("Não")
        if "nivel" in df.columns: 
            df["nivel"] = pd.to_numeric(df["nivel"], errors='coerce').fillna(2).astype(int)
            
        return df
    except Exception as e:
        if "429" in str(e):
            time.sleep(2)
            st.warning("Muitos acessos. Aguardando Google liberar...")
            try:
                return load_data.__wrapped__(sheet_name, expected_cols)
            except:
                return pd.DataFrame(columns=expected_cols)
        st.error(f"Erro ao ler dados ({sheet_name}): {e}")
        return pd.DataFrame(columns=expected_cols)

# --- SALVAR DADOS ---
def save_data(df, sheet_name):
    try:
        sh = get_connection()
        try:
            worksheet = sh.worksheet(sheet_name)
        except:
            worksheet = sh.add_worksheet(title=sheet_name, rows=100, cols=20)
        
        worksheet.clear()
        dados = [df.columns.values.tolist()] + df.values.tolist()
        worksheet.update(range_name='A1', values=dados)
        time.sleep(2) 
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar ({sheet_name}): {e}")
        return False

# --- FUNÇÕES VISUAIS DE GERAÇÃO DE IMAGEM ---
def gerar_imagem_bonita(df, titulo="Relatório"):
    cor_cabecalho = '#1b5e20' 
    cor_texto_cabecalho = 'white'
    cor_linha_par = '#f1f8e9' 
    cor_linha_impar = 'white'
    
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.8 + 2)) 
    ax.axis('tight')
    ax.axis('off')
    
    plt.title(titulo.upper(), fontsize=20, weight='bold', color='#1b5e20', pad=25)
    tabela = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    tabela.auto_set_font_size(False); tabela.set_fontsize(14); tabela.scale(1.2, 2.0)
    
    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('#cfd8dc'); cell.set_linewidth(1)
        if row == 0:
            cell.set_facecolor(cor_cabecalho); cell.set_text_props(color=cor_texto_cabecalho, weight='bold'); cell.set_height(0.12)
        else:
            cell.set_height(0.1)
            if row % 2 == 0: cell.set_facecolor(cor_linha_par)
            else: cell.set_facecolor(cor_linha_impar)
    
    buf = io.BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', dpi=300, transparent=False); buf.seek(0)
    return buf

def gerar_card_jogo(data_jogo, placar_verde, placar_preto, gols_map, df_elenco):
    art_verde = []; art_preto = []
    for jogador, gols in gols_map.items():
        if gols > 0:
            time_jogador = "Indefinido"
            if not df_elenco.empty:
                row = df_elenco[df_elenco['nome'] == jogador]
                if not row.empty: time_jogador = row.iloc[0]['time']
            txt = f"{jogador}" if gols == 1 else f"{jogador} ({gols})"
            if time_jogador == 'Verde': art_verde.append(txt)
            else: art_preto.append(txt)

    fig, ax = plt.subplots(figsize=(10, 8)); ax.axis('off'); fig.patch.set_facecolor('#f8f9fa')
    plt.text(0.5, 0.95, "RESULTADO FINAL", ha='center', va='center', fontsize=22, weight='bold', color='#333')
    plt.text(0.5, 0.88, f"{data_jogo}", ha='center', va='center', fontsize=12, color='#666')
    plt.text(0.25, 0.75, "VERDE", ha='center', fontsize=18, weight='bold', color='#2E7D32')
    plt.text(0.75, 0.75, "PRETO", ha='center', fontsize=18, weight='bold', color='#212121')
    plt.text(0.5, 0.65, f"{placar_verde}  x  {placar_preto}", ha='center', va='center', fontsize=50, weight='bold')
    plt.plot([0.1, 0.9], [0.55, 0.55], color='#ddd', lw=2)
    plt.text(0.5, 0.50, "GOLS", ha='center', fontsize=14, color='#888')
    y = 0.45
    for a in art_verde: plt.text(0.25, y, a, ha='center', fontsize=12, color='#2E7D32'); y -= 0.05
    y = 0.45
    for a in art_preto: plt.text(0.75, y, a, ha='center', fontsize=12, color='#212121'); y -= 0.05
    plt.text(0.5, 0.05, "PELADA MADRUGAO", ha='center', fontsize=10, color='#aaa', style='italic')
    buf = io.BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#f8f9fa'); buf.seek(0)
    return buf

# --- DADOS PADRÃO ---
def carregar_elenco():
    df = load_data("elenco", ["nome", "time", "tipo", "punicao", "nivel"])
    if df.empty:
        df = pd.DataFrame(columns=["nome", "time", "tipo", "punicao", "nivel"])
        save_data(df, "elenco")
    
    if "punicao" not in df.columns: df["punicao"] = "Não"
    if "nivel" not in df.columns: df["nivel"] = 2
    
    return df

# --- LOGIN (ATUALIZADO COM BOTÃO ENTRAR) ---
SENHA_ADMIN = st.secrets.get("admin_password", "1234")
SENHA_MODERADOR = st.secrets.get("moderator_password", "bola") 
SENHA_FINANCEIRO = st.secrets.get("finance_password", "money")

# Formulário para login
with st.sidebar.form(key="login_form"):
    st.markdown("### 🔐 Acesso Restrito")
    senha_digitada = st.text_input("Senha de Acesso", type="password", placeholder="Digite a credencial")
    btn_entrar = st.form_submit_button("ENTRAR 🔓", type="primary", use_container_width=True)

user_role = "visitor"

if senha_digitada == SENHA_ADMIN:
    user_role = "admin"
    st.sidebar.success("🔑 ADMIN MASTER")
elif senha_digitada == SENHA_MODERADOR:
    user_role = "moderator"
    st.sidebar.success("🛡️ MODERADOR")
elif senha_digitada == SENHA_FINANCEIRO:
    user_role = "finance"
    st.sidebar.warning("💰 TESOUREIRO")
else:
    user_role = "visitor"
    if senha_digitada:
        st.sidebar.error("❌ Senha Incorreta")
    else:
        st.sidebar.info("👀 MODO VISITANTE")

df_elenco = carregar_elenco()

# --- DAQUI PARA BAIXO O CÓDIGO CONTINUA IGUAL (NAVEGAÇÃO, ABAS, ETC) ---
