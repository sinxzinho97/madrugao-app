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

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔒 Área Restrita")

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
LISTA_PADRAO = [
    {"nome": "Alex", "time": "Verde", "tipo": "Mensalista", "punicao": "Não", "nivel": 2},
    {"nome": "Anderson", "time": "Verde", "tipo": "Mensalista", "punicao": "Não", "nivel": 2},
]

def carregar_elenco():
    df = load_data("elenco", ["nome", "time", "tipo", "punicao", "nivel"])
    if df.empty:
        df = pd.DataFrame(columns=["nome", "time", "tipo", "punicao", "nivel"])
        save_data(df, "elenco")
    
    if "punicao" not in df.columns: df["punicao"] = "Não"
    if "nivel" not in df.columns: df["nivel"] = 2
    
    return df

# --- LOGIN ---
SENHA_ADMIN = st.secrets.get("admin_password", "1234")
SENHA_FINANCEIRO = st.secrets.get("finance_password", "money")
senha_digitada = st.sidebar.text_input("Senha", type="password")

user_role = "visitor"
if senha_digitada == SENHA_ADMIN:
    user_role = "admin"
    st.sidebar.success("🔑 ADMIN")
elif senha_digitada == SENHA_FINANCEIRO:
    user_role = "finance"
    st.sidebar.warning("💰 TESOUREIRO")
else:
    user_role = "visitor"
    st.sidebar.info("👀 VISITANTE")

df_elenco = carregar_elenco()

# --- NAVEGAÇÃO ---
if user_role == "admin":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🎲 Sorteio", "📝 Súmula", "👥 Elenco", "💰 Financeiro", "🏦 Cofre", "📊 Estatísticas", "⚙️ Ajustes"])
elif user_role == "finance":
    tab4, tab5, tab6 = st.tabs(["💰 Financeiro", "🏦 Cofre", "📊 Estatísticas"])
    tab1=tab2=tab3=tab7=st.container()
else:
    tab6, tab4, tab5 = st.tabs(["📊 Estatísticas", "💰 Financeiro", "🏦 Cofre"])
    tab1=tab2=tab3=tab7=st.container()

# === ABA 1: SORTEIO ===
if user_role == "admin":
    with tab1:
        st.header("Montar Times")
        
        if 'temp_diaristas' not in st.session_state: st.session_state.temp_diaristas = []
        if 'resultado_sorteio' not in st.session_state: st.session_state.resultado_sorteio = {}
        if 'mapa_chegada' not in st.session_state: st.session_state.mapa_chegada = {}

        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("1. Diaristas")
            with st.form("form_add_diarista", clear_on_submit=True):
                novo_diarista = st.text_input("Nome:")
                # REMOVIDO: Seleção de Nível do Diarista
                add_btn = st.form_submit_button("➕ Adicionar")
                if add_btn and novo_diarista:
                    # Adiciona com Nível padrão 2 (Médio)
                    st.session_state.temp_diaristas.append({"nome": novo_diarista, "nivel": 2})
                    st.rerun()
            
            if st.session_state.temp_diaristas:
                st.caption("Lista de Diaristas:")
                # Exibição simplificada (Sem mostrar nível)
                lista_dia = [f"{i+1}. {d['nome']}" for i, d in enumerate(st.session_state.temp_diaristas)]
                render_html_list("Diaristas Adicionados", lista_dia, "box-azul", "#1F6FEB")
                
                if st.button("Limpar Lista"):
                    st.session_state.temp_diaristas = []; st.rerun()

        with c2:
            st.subheader("2. Mensalistas & Sorteio")
            with st.form("form_sorteio_geral"):
                nomes = sorted(df_elenco['nome'].astype(str).tolist()) if not df_elenco.empty else []
                punidos_nomes = df_elenco[df_elenco['punicao'] == 'Sim']['nome'].tolist()
                
                mens = st.multiselect("Presença (Selecione na ORDEM DE CHEGADA):", nomes, key="t1_m")
                
                if mens:
                    ordem_texto = ", ".join([f"{i+1}. {n}" for i, n in enumerate(mens)])
                    st.caption(f"🏁 **Ordem Atual:** {ordem_texto}")
                
                if punidos_nomes:
                    st.error(f"⚠️ Punições Pendentes: {', '.join(punidos_nomes)}")

                st.write("")
                submitted = st.form_submit_button("🎲 REALIZAR SORTEIO", type="primary")
                
                if submitted:
                    # Monta lista de objetos
                    pool_completo = []
                    
                    # Mensalistas
                    for m in mens:
                        row = df_elenco[df_elenco['nome'] == m].iloc[0]
                        pool_completo.append({
                            "nome": m,
                            "time_pref": row['time'],
                            "nivel": int(row['nivel']),
                            "tipo": "Mensalista"
                        })
                        
                    # Diaristas (Nível 2 fixo, sem input)
                    for d in st.session_state.temp_diaristas:
                        pool_completo.append({
                            "nome": f"{d['nome']} (D)",
                            "time_pref": "Ambos",
                            "nivel": int(d['nivel']),
                            "tipo": "Diarista"
                        })
                    
                    mapa_chegada = {p['nome'].replace(" (D)", ""): i+1 for i, p in enumerate(pool_completo)}
                    st.session_state.mapa_chegada = mapa_chegada
                    
                    if not pool_completo: st.error("Ninguém selecionado!")
                    else:
                        MAX = 20
                        titulares_objs = pool_completo[:MAX]
                        reservas_names = [p['nome'] for p in pool_completo[MAX:]]
                        
                        verde = []
                        preto = []
                        
                        fixos_verde = [p for p in titulares_objs if p['time_pref'] == 'Verde']
                        fixos_preto = [p for p in titulares_objs if p['time_pref'] == 'Preto']
                        flutuantes = [p for p in titulares_objs if p['time_pref'] == 'Ambos']
                        
                        verde.extend([p['nome'] for p in fixos_verde])
                        preto.extend([p['nome'] for p in fixos_preto])
                        
                        # Ordena flutuantes por Nível para balancear (mas sem mostrar o nível)
                        flutuantes.sort(key=lambda x: x['nivel']) 
                        
                        for p in flutuantes:
                            if len(verde) <= len(preto): verde.append(p['nome'])
                            else: preto.append(p['nome'])
                        
                        st.session_state.resultado_sorteio = {"verde": verde, "preto": preto, "reservas": reservas_names}

        if 'resultado_sorteio' in st.session_state and st.session_state.resultado_sorteio:
            res_data = st.session_state.resultado_sorteio
            st.divider()
            
            def formatar_jogador(nome):
                clean = nome.replace(" (D)", "")
                ordem = st.session_state.mapa_chegada.get(clean, "?")
                prefixo = f"<b style='color:#8B949E'>{ordem}º</b> "
                status = ""
                if clean in punidos_nomes:
                    if len(res_data['reservas']) > 0: status = " <span style='color:#F85149; font-weight:bold'>🟥 (Sai)</span>"
                    else: status = " <span style='color:#D29922; font-weight:bold'>⚠️ (Joga)</span>"
                return f"{prefixo}{nome}{status}"

            ca, cb = st.columns(2)
            
            with ca:
                lista_verde = [formatar_jogador(x) for x in res_data['verde']]
                render_html_list(f"VERDE ({len(res_data['verde'])})", lista_verde, "box-verde", "#2e7d32")

            with cb:
                lista_preto = [formatar_jogador(x) for x in res_data['preto']]
                render_html_list(f"PRETO ({len(res_data['preto'])})", lista_preto, "box-preto", "#F0F6FC")
            
            if res_data['reservas']:
                st.divider()
                col_res, col_sai = st.columns(2)
                
                with col_res:
                    lista_res = []
                    for i, r in enumerate(res_data['reservas']):
                        ordem_reserva = st.session_state.mapa_chegada.get(r.replace(" (D)", ""), "?")
                        lista_res.append((f"<b>{i+1}.</b> {r}", f"Chegada: {ordem_reserva}º"))
                    render_html_list("⏱️ Reservas (Fila)", lista_res, "box-ouro", "#D29922")
                
                with col_sai:
                    titulares_todos = res_data['verde'] + res_data['preto']
                    lista_saida_objs = []
                    for p in titulares_todos:
                        clean = p.replace(" (D)", "")
                        num_chegada = st.session_state.mapa_chegada.get(clean, 0)
                        is_punido = clean in punidos_nomes
                        time_icon = "🟢" if p in res_data['verde'] else "⚫"
                        lista_saida_objs.append({"nome": p, "num": num_chegada, "punido": is_punido, "icon": time_icon})
                    
                    lista_saida_objs.sort(key=lambda x: (x['punido'], x['num']), reverse=True)
                    qtd_reservas = len(res_data['reservas'])
                    
                    lista_sai_fmt = []
                    for k in range(min(qtd_reservas, len(lista_saida_objs))):
                        alvo = lista_saida_objs[k]
                        motivo = "<b style='color:#F85149'>🟥 PUNIÇÃO</b>" if alvo['punido'] else f"Chegada Nº {alvo['num']}"
                        lista_sai_fmt.append((f"<b>{k+1}. {alvo['nome']}</b> {alvo['icon']}", motivo))
                    
                    render_html_list("🚨 Sugestão de Saída", lista_sai_fmt, "box-vermelho", "#F85149")

            st.divider()
            if st.button("📂 CARREGAR ESTES TIMES NA SÚMULA", type="secondary", use_container_width=True):
                todos = res_data['verde'] + res_data['preto'] + res_data['reservas']
                m_sum = []
                d_sum = []
                nomes_bd = df_elenco['nome'].values.tolist()
                for nome in todos:
                    clean = nome.replace(" (D)", "").replace(" 🟥 (Sai)", "").replace(" ⚠️ (Joga)", "")
                    if clean in nomes_bd: m_sum.append(clean)
                    else: d_sum.append(clean)
                st.session_state['import_sumula_mens'] = m_sum
                st.session_state['import_sumula_diar'] = d_sum
                st.success("✅ Enviado para a Súmula!")

# === ABA 2: SÚMULA (MODO TABELA) ===
if user_role == "admin":
    with tab2:
        st.header("Súmula")
        
        mens_list = sorted(df_elenco['nome'].astype(str).tolist())
        imp_mens = st.session_state.get('import_sumula_mens', [])
        imp_diar = st.session_state.get('import_sumula_diar', [])
        
        todos_nomes = mens_list + imp_diar
        todos_nomes = list(dict.fromkeys(todos_nomes))
        
        df_sumula = pd.DataFrame({'Atleta': todos_nomes})
        df_sumula['Jogou'] = df_sumula['Atleta'].apply(lambda x: x in imp_mens or x in imp_diar)
        df_sumula['Gols'] = 0
        df_sumula['Justificou'] = False
        
        df_sumula = df_sumula.sort_values(by='Jogou', ascending=False).reset_index(drop=True)

        with st.form("form_sumula_tabela"):
            dt = st.date_input("Data do Jogo:", datetime.today())
            v = st.radio("Vencedor:", ["Verde", "Preto", "Empate"], horizontal=True)
            
            st.write("📝 **Marque quem jogou e digite os gols:**")
            
            edited_df = st.data_editor(
                df_sumula,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Atleta": st.column_config.TextColumn("Atleta", disabled=True),
                    "Jogou": st.column_config.CheckboxColumn("Jogou?", help="Marque se esteve presente"),
                    "Gols": st.column_config.NumberColumn("Gols", min_value=0, max_value=20, step=1),
                    "Justificou": st.column_config.CheckboxColumn("Justificou Faltas?", help="Marque se não foi mas avisou")
                },
                height=600
            )
            
            submitted_sumula = st.form_submit_button("💾 SALVAR SÚMULA E APLICAR PUNIÇÕES", type="primary")
            
            if submitted_sumula:
                jogaram_df = edited_df[edited_df['Jogou'] == True]
                justificaram_df = edited_df[edited_df['Justificou'] == True]
                gols_df = edited_df[edited_df['Gols'] > 0]
                
                jogaram_lista = jogaram_df['Atleta'].tolist()
                justificaram_lista = justificaram_df['Atleta'].tolist()
                gm = dict(zip(gols_df['Atleta'], gols_df['Gols']))
                
                score_verde = 0; score_preto = 0
                for atleta, qtd in gm.items():
                    t_jog = "Verde"
                    row = df_elenco[df_elenco['nome'] == atleta]
                    if not row.empty: t_jog = row.iloc[0]['time']
                    if t_jog == "Verde": score_verde += qtd
                    elif t_jog == "Preto": score_preto += qtd
                    else: score_verde += qtd 
                
                hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
                gid = int(datetime.now().timestamp())
                nv = []
                for p in jogaram_lista:
                    nv.append({"id": gid, "data": str(dt), "jogador": p, "tipo_registro": "Jogo", "gols": gm.get(p,0), "vencedor": v})
                for j in justificaram_lista:
                    nv.append({"id": gid, "data": str(dt), "jogador": j, "tipo_registro": "Justificado", "gols": 0, "vencedor": ""})
                
                if save_data(pd.concat([hist, pd.DataFrame(nv)]), "jogos"):
                    st.toast("Súmula Salva!", icon="✅")
                    
                    df_elenco_atual = carregar_elenco()
                    alterou_elenco = False
                    mensalistas_nomes = df_elenco_atual[df_elenco_atual['tipo'] == 'Mensalista']['nome'].tolist()
                    faltosos = [m for m in mensalistas_nomes if m not in jogaram_lista and m not in justificaram_lista]
                    
                    for i, row in df_elenco_atual.iterrows():
                        nome = row['nome']
                        if nome in faltosos:
                            if row['punicao'] != "Sim":
                                df_elenco_atual.at[i, 'punicao'] = "Sim"
                                alterou_elenco = True
                        elif nome in jogaram_lista:
                            if row['punicao'] != "Não":
                                df_elenco_atual.at[i, 'punicao'] = "Não"
                                alterou_elenco = True
                    
                    if alterou_elenco:
                        save_data(df_elenco_atual, "elenco")
                        if faltosos: st.error(f"🚨 Punição aplicada para: {', '.join(faltosos)}")
                    
                    st.session_state['ultimo_placar_dados'] = (score_verde, score_preto, gm, str(dt))
                    if 'import_sumula_mens' in st.session_state: del st.session_state['import_sumula_mens']
                    if 'import_sumula_diar' in st.session_state: del st.session_state['import_sumula_diar']

        if 'ultimo_placar_dados' in st.session_state:
            sv, sp, sgm, sdt = st.session_state['ultimo_placar_dados']
            st.divider()
            
            c_res_v, c_res_p = st.columns(2)
            with c_res_v:
                render_html_list(f"VERDE: {sv}", [f"{k}: {v} Gols" for k, v in sgm.items() if df_elenco[df_elenco['nome']==k]['time'].values[0] == 'Verde' if not df_elenco[df_elenco['nome']==k].empty], "box-verde", "#2e7d32")
            with c_res_p:
                render_html_list(f"PRETO: {sp}", [f"{k}: {v} Gols" for k, v in sgm.items() if df_elenco[df_elenco['nome']==k]['time'].values[0] == 'Preto' if not df_elenco[df_elenco['nome']==k].empty], "box-preto", "#F0F6FC")

            st.divider()
            img_card = gerar_card_jogo(sdt, sv, sp, sgm, df_elenco)
            st.download_button("📸 Baixar Card do Jogo", img_card, f"jogo_{sdt}.png", "image/png")

# === ABA 3: ELENCO ===
if user_role == "admin":
    with tab3:
        st.header("Gerenciar Elenco")
        with st.expander("✏️ Edição Rápida (Tabela Completa)", expanded=True):
            with st.form("form_elenco_massa"):
                df_editor = st.data_editor(
                    df_elenco,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "nome": st.column_config.TextColumn("Nome", disabled=True),
                        "time": st.column_config.SelectboxColumn("Time", options=["Verde", "Preto", "Ambos"], required=True),
                        "tipo": st.column_config.SelectboxColumn("Tipo", options=["Mensalista", "Diarista Frequente"], required=True),
                        "punicao": st.column_config.SelectboxColumn("Punição", options=["Não", "Sim"], required=True),
                        "nivel": st.column_config.SelectboxColumn("Nível (1=Craque)", options=[1, 2, 3], required=True)
                    },
                    height=400
                )
                if st.form_submit_button("💾 SALVAR ALTERAÇÕES NA TABELA"):
                    save_data(df_editor, "elenco")
                    st.success("Elenco atualizado com sucesso!")
                    st.rerun()
        
        st.divider()
        st.subheader("📋 Visualização Rápida (ADM)")
        cv, cp = st.columns(2)
        with cv:
            verde_list = []
            for _, r in df_elenco[df_elenco['time'] == 'Verde'].iterrows():
                verde_list.append(f"{r['nome']} (Nv {r['nivel']})")
            render_html_list("ELENCO VERDE", sorted(verde_list), "box-verde", "#2e7d32")
        with cp:
            preto_list = []
            for _, r in df_elenco[df_elenco['time'] == 'Preto'].iterrows():
                preto_list.append(f"{r['nome']} (Nv {r['nivel']})")
            render_html_list("ELENCO PRETO", sorted(preto_list), "box-preto", "#F0F6FC")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("➕ Adicionar Novo")
            with st.form("form_add_jogador", clear_on_submit=True):
                n = st.text_input("Nome").strip()
                t = st.selectbox("Time", ["Verde", "Preto", "Ambos"])
                tp = st.selectbox("Tipo", ["Mensalista", "Diarista Frequente"])
                nv = st.selectbox("Nível (1=Craque)", [1, 2, 3], index=1)
                
                submitted_add = st.form_submit_button("Adicionar Jogador")
                if submitted_add:
                    if n and n not in df_elenco['nome'].values:
                        novo_df = pd.concat([df_elenco, pd.DataFrame([{"nome":n,"time":t,"tipo":tp,"punicao":"Não", "nivel": nv}])], ignore_index=True)
                        if save_data(novo_df, "elenco"): st.success(f"{n} Adicionado!"); st.rerun()
                    elif n in df_elenco['nome'].values:
                        st.error("Nome já existe!")
        
        with c2:
            st.subheader("🗑️ Excluir")
            s_del = st.selectbox("Selecione para excluir:", sorted(df_elenco['nome'].astype(str).tolist()))
            if st.button("Excluir Jogador"):
                if s_del:
                    save_data(df_elenco[df_elenco['nome']!=s_del], "elenco")
                    st.rerun()

# === ABA 4: FINANCEIRO ===
with tab4:
    st.header("💰 Controle de Pagamentos")
    cols_status = ["nome", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    df_checks = load_data("financeiro", cols_status)
    if not df_elenco.empty:
        df_mens = df_elenco[df_elenco['tipo'] == 'Mensalista'][['nome']].sort_values('nome')
        if not df_checks.empty:
            for nm in df_mens['nome']:
                if nm not in df_checks['nome'].values:
                    nv = {k: False for k in cols_status if k!='nome'}; nv['nome'] = nm
                    df_checks = pd.concat([df_checks, pd.DataFrame([nv])], ignore_index=True)
            df_checks = df_checks[df_checks['nome'].isin(df_mens['nome'])]
        else:
            df_checks = df_mens.copy(); 
            for c in cols_status[1:]: df_checks[c] = False
    
    for c in cols_status[1:]: df_checks[c] = df_checks[c].astype(str).str.upper() == 'TRUE'

    hoje = datetime.today()
    meses_map = {1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"}
    mes_atual = meses_map[hoje.month]
    pagos_count = df_checks[df_checks[mes_atual] == True].shape[0]
    total_atletas = df_checks.shape[0]
    pendentes_count = df_checks[df_checks[mes_atual] == False].shape[0]
    
    c_f1, c_f2 = st.columns(2)
    c_f1.info(f"Mês Atual ({mes_atual}): {pagos_count} pagos de {total_atletas}")
    if hoje.day > 20 and (total_atletas - pagos_count) > 0: c_f2.error(f"🚨 Pendentes: {total_atletas - pagos_count}")
    else: c_f2.warning(f"🕒 Pendentes: {total_atletas - pagos_count}")

    st.divider()

    if user_role in ["admin", "finance"]:
        st.write("Marque quem está em dia:")
        with st.form("form_financeiro_checks"):
            edited_checks = st.data_editor(df_checks, use_container_width=True, hide_index=True, key="editor_fin")
            if st.form_submit_button("💾 SALVAR LISTA (CONFIRMAR)"):
                save_data(edited_checks, "financeiro"); st.success("Atualizado!"); st.rerun()
    
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class='stat-card' style='border-left: 5px solid #2e7d32;'>
                <span class='destaque-titulo' style='color:#2e7d32'>✅ JÁ PAGARAM</span>
                <span class='destaque-valor'>{pagos_count}</span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='stat-card' style='border-left: 5px solid #d32f2f;'>
                <span class='destaque-titulo' style='color:#d32f2f'>🕒 PENDENTES</span>
                <span class='destaque-valor'>{pendentes_count}</span>
            </div>
            """, unsafe_allow_html=True)

# === ABA 5: COFRE ===
with tab5:
    st.header("🏦 Cofre do Madrugão")
    cols_mov = ["Data", "Descricao", "Valor"]
    df_mov = load_data("saidas", cols_mov)
    if not df_mov.empty: df_mov["Valor"] = pd.to_numeric(df_mov["Valor"], errors='coerce').fillna(0)

    total_entradas = df_mov[df_mov["Valor"] > 0]["Valor"].sum()
    total_saidas = abs(df_mov[df_mov["Valor"] < 0]["Valor"].sum())
    saldo_caixa = total_entradas - total_saidas

    k1, k2, k3 = st.columns(3)
    k1.metric("Entradas", f"R$ {total_entradas:,.2f}")
    k2.metric("Saídas", f"R$ {total_saidas:,.2f}")
    k3.metric("SALDO", f"R$ {saldo_caixa:,.2f}", delta="Caixa")
    
    st.divider()

    if user_role in ["admin", "finance"]:
        with st.expander("➕ Adicionar Novo Lançamento", expanded=True):
            with st.form("form_cofre", clear_on_submit=True):
                c_g1, c_g2, c_g3, c_g4 = st.columns([1, 2, 1, 1])
                d_data = c_g1.date_input("Data", datetime.today(), key="cofre_data")
                d_desc = c_g2.text_input("Descrição", key="cofre_desc")
                d_valor = c_g3.number_input("Valor", min_value=0.0, step=10.0, key="cofre_valor")
                d_tipo = c_g4.radio("Tipo:", ["Entrada (+)", "Saída (-)"], horizontal=True, key="cofre_tipo")
                if st.form_submit_button("💾 REGISTRAR"):
                    if d_desc and d_valor > 0:
                        valor_final = d_valor if "Entrada" in d_tipo else -d_valor
                        nova_mov = pd.DataFrame([{"Data": str(d_data), "Descricao": d_desc, "Valor": valor_final}])
                        df_mov = pd.concat([df_mov, nova_mov], ignore_index=True)
                        save_data(df_mov, "saidas"); st.success("Registrado!"); st.rerun()
        
        st.write("📝 **Histórico (Edição em Lote):**")
        if not df_mov.empty:
            df_mov['Data'] = pd.to_datetime(df_mov['Data'], errors='coerce')
            
            with st.form("form_cofre_tabela"):
                edited_df = st.data_editor(
                    df_mov,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="dynamic",
                    column_config={
                        "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
                        "Data": st.column_config.DateColumn(format="DD/MM/YYYY")
                    },
                    key="editor_cofre"
                )
                if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    edited_df['Data'] = edited_df['Data'].astype(str)
                    save_data(edited_df, "saidas"); st.success("Atualizado!"); st.rerun()
            
            with st.expander("🗑️ Apagar Movimentação (Modo Lista)"):
                df_temp = df_mov.copy().sort_values("Data", ascending=False)
                opcoes_exclusao = []
                for idx, row in df_temp.iterrows():
                    dt_str = row['Data'].strftime('%d/%m/%Y') if pd.notnull(row['Data']) else "Data Inválida"
                    opcoes_exclusao.append(f"[{idx}] {dt_str} | {row['Descricao']} | R$ {row['Valor']:.2f}")
                
                if opcoes_exclusao:
                    selecionado = st.selectbox("Selecione para excluir:", options=opcoes_exclusao, key="sel_del_cofre")
                    if st.button("🗑️ EXCLUIR ITEM", key="btn_del_cofre"):
                        idx_to_drop = int(selecionado.split("]")[0].replace("[", ""))
                        df_novo = df_mov.drop(idx_to_drop)
                        df_novo['Data'] = df_novo['Data'].astype(str)
                        save_data(df_novo, "saidas"); st.success("Apagado!"); st.rerun()
    else:
        st.info("ℹ️ Detalhes restritos à administração.")

# === ABA 6: ESTATÍSTICAS (VISUAL ZEBRADO) ===
with tab6:
    st.header("📊 Estatísticas")
    hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
    if not hist.empty:
        vt = hist[['id','vencedor']].drop_duplicates()['vencedor'].value_counts()
        c1,c2,c3 = st.columns(3)
        c1.metric("Verde 🦉 💚", vt.get("Verde",0))
        c2.metric("Preto 🦉 🖤", vt.get("Preto",0))
        c3.metric("Empates", vt.get("Empate",0))
        
        ca, cb = st.columns(2)
        with ca:
            hist['gols'] = pd.to_numeric(hist['gols'], errors='coerce').fillna(0)
            g = hist[hist['gols']>0].groupby("jogador")['gols'].sum().sort_values(ascending=False).reset_index()
            
            artilharia_html = []
            if not g.empty:
                max_gols = g['gols'].max()
                for i, r in g.iterrows():
                    icone = "🥇" if r['gols'] == max_gols else f"{i+1}º"
                    artilharia_html.append((f"{icone} {r['jogador']}", f"{int(r['gols'])} Gols"))
            
            render_html_list("⚽ ARTILHARIA", artilharia_html, "box-ouro", "#fbc02d")
            
            g_print = g.copy(); g_print.columns = ["ATLETA", "GOLS"]
            st.download_button("📸 Baixar Imagem", gerar_imagem_bonita(g_print, "ARTILHARIA"), "artilharia.png", "image/png")

        with cb:
            j = hist[hist['tipo_registro']=='Jogo'].groupby("jogador").size().sort_values(ascending=False)
            presenca_html = []
            for jogador, qtd in j.items():
                presenca_html.append((jogador, f"{qtd} Jogos"))
            render_html_list("📅 PRESENÇA", presenca_html, "box-azul", "#1565c0")

        st.divider(); st.subheader("📈 Corrida da Artilharia")
        df_gols = hist[(hist['tipo_registro'] == 'Jogo')]
        if not df_gols.empty:
            pivot = df_gols.pivot_table(index='data', columns='jogador', values='gols', aggfunc='sum').fillna(0)
            st.line_chart(pivot.cumsum())
        else: st.info("Sem dados.")
    else: st.info("Sem dados.")

# === ABA 7: AJUSTES ===
if user_role == "admin":
    with tab7:
        st.header("Ajustes")
        hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
        if not hist.empty:
            jg = hist.drop_duplicates(subset=['id'])[['id','data','vencedor']].sort_values('data', ascending=False)
            for i, r in jg.iterrows():
                c1,c2 = st.columns([4,1])
                c1.write(f"📅 {r['data']} - {r['vencedor']}")
                if c2.button("Apagar", key=f"d_{r['id']}"):
                    save_data(hist[hist['id']!=r['id']], "jogos"); st.rerun()

st.write(""); st.write(""); st.divider()
st.markdown("""<div style='text-align: center; color: grey; font-size: 14px;'>Desenvolvido por <b>Lucas Guilherme</b> | 📱 (81) 99964-4971 (wpp)</div>""", unsafe_allow_html=True)
