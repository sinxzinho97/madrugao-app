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

# --- CONFIGURAÇÕES ---
icone_aba = "logo.png" if os.path.exists("logo.png") else "🦉"
st.set_page_config(page_title="Pelada Madrugão", page_icon=icone_aba, layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.write("")
    st.title("🔒 Acesso")

# --- TÍTULO ---
st.title("Pelada Madrugão 🦉 💚 🖤")

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

# --- FUNÇÕES VISUAIS ---
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
    {"nome": "Alex", "time": "Verde", "tipo": "Mensalista", "nivel": 2, "punicao": "Não"},
    {"nome": "Anderson", "time": "Verde", "tipo": "Mensalista", "nivel": 2, "punicao": "Não"},
]

def carregar_elenco():
    df = load_data("elenco", ["nome", "time", "tipo", "nivel", "punicao"])
    if df.empty:
        df = pd.DataFrame(columns=["nome", "time", "tipo", "nivel", "punicao"])
        save_data(df, "elenco")
    
    if "nivel" not in df.columns: df["nivel"] = 2
    if "punicao" not in df.columns: df["punicao"] = "Não"
    df["nivel"] = pd.to_numeric(df["nivel"], errors='coerce').fillna(2).astype(int)
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

# --- NAVEGAÇÃO OTIMIZADA ---
abas_admin = ["🎲 Sorteio", "📝 Súmula", "📢 Resumo Semanal", "👥 Elenco", "💰 Financeiro", "🏦 Cofre", "📊 Estatísticas", "⚙️ Ajustes"]
abas_fin = ["💰 Financeiro", "🏦 Cofre", "📊 Estatísticas"]
abas_vis = ["📢 Resumo Semanal", "📊 Estatísticas", "💰 Financeiro", "🏦 Cofre"]

if user_role == "admin":
    tabs = st.tabs(abas_admin)
    (t_sorteio, t_sumula, t_resumo, t_elenco, t_fin, t_cofre, t_estat, t_ajustes) = tabs
elif user_role == "finance":
    tabs = st.tabs(abas_fin)
    t_fin, t_cofre, t_estat = tabs
    t_sorteio=t_resumo=t_sumula=t_elenco=t_ajustes=st.container()
else:
    tabs = st.tabs(abas_vis)
    t_resumo, t_estat, t_fin, t_cofre = tabs
    t_sorteio=t_sumula=t_elenco=t_ajustes=st.container()

# === ABA 1: SORTEIO INTELIGENTE (MENSALISTA FIRST) ===
if user_role == "admin":
    with t_sorteio:
        st.header("Montar Times & Auditoria")
        
        # Inicializa variáveis de sessão
        if 'lista_diaristas' not in st.session_state: st.session_state.lista_diaristas = []
        if 'reservas_vivos' not in st.session_state: st.session_state.reservas_vivos = []
        if 'lista_zap_cache' not in st.session_state: st.session_state.lista_zap_cache = ""
        
        # 1. CHECKLIST ZAP
        with st.expander("📋 CHECKLIST: Colar lista do WhatsApp aqui", expanded=False):
            st.info("Cole a lista do grupo aqui. O sistema vai avisar quem prometeu e não veio.")
            lista_zap_texto = st.text_area("Lista do Zap:", height=150, value=st.session_state.lista_zap_cache)
            if lista_zap_texto: st.session_state.lista_zap_cache = lista_zap_texto # Salva pra não sumir
        
        st.divider()
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.subheader("1. Presença (Mensalistas)")
            if not df_elenco.empty:
                nomes_mensalistas = sorted(df_elenco[df_elenco['tipo'] == 'Mensalista']['nome'].astype(str).tolist())
                
                # SELEÇÃO APENAS MENSALISTAS
                mens_presentes = st.multiselect(
                    "Selecione os Mensalistas presentes:", 
                    nomes_mensalistas, 
                    key="t1_mensalistas",
                    help="Marque todos os mensalistas que chegaram."
                )
            else: mens_presentes = []
            
            st.markdown("---")
            st.subheader("2. Diaristas")
            with st.form("add_diarista_form", clear_on_submit=True):
                novo_diarista = st.text_input("Nome:")
                nivel_diarista = st.selectbox("Nível:", [1, 2, 3], index=1)
                if st.form_submit_button("➕ Adicionar Diarista"):
                    if novo_diarista:
                        st.session_state.lista_diaristas.append({
                            "nome": novo_diarista, 
                            "nivel": nivel_diarista
                        })
                        st.rerun()
            
            if st.session_state.lista_diaristas:
                st.caption("Diaristas na lista:")
                for i, d in enumerate(st.session_state.lista_diaristas):
                    st.text(f"{i+1}. {d['nome']} (Nv {d['nivel']})")
                if st.button("Limpar Diaristas"):
                    st.session_state.lista_diaristas = []
                    st.rerun()

        with c2:
            st.subheader("3. Realizar Sorteio")
            st.info("Regra: Mensalistas têm prioridade nos 20 primeiros. Diaristas só entram se sobrar vaga.")
            
            if st.button("🎲 SORTEAR TIMES (1º QUADRO)", type="primary"):
                # --- LÓGICA DE PRIORIDADE ---
                pool_titulares = []
                pool_reservas = [] # Vai virar a lista de espera
                
                # 1. Mensalistas (Prioridade Absoluta)
                # Separa quem tem punição para o fim, se quiser, mas a regra aqui é Mensalista > Diarista
                for nome in mens_presentes:
                    d = df_elenco[df_elenco['nome'] == nome].iloc[0]
                    # Verifica punição se quiser jogar pro final da fila de mensalistas
                    # Mas por enquanto, vamos assumir ordem de seleção como chegada
                    p_obj = {"nome": nome, "nivel": d['nivel'], "tipo": "Mensalista"}
                    
                    if len(pool_titulares) < 20:
                        pool_titulares.append(p_obj)
                    else:
                        pool_reservas.append(p_obj) # Mensalista que chegou tarde vai pra reserva
                
                # 2. Diaristas (Só entra se tiver vaga < 20)
                for d in st.session_state.lista_diaristas:
                    p_obj = {"nome": f"{d['nome']} (D)", "nivel": d['nivel'], "tipo": "Diarista"}
                    
                    if len(pool_titulares) < 20:
                        pool_titulares.append(p_obj)
                    else:
                        pool_reservas.append(p_obj) # Sem vaga, vai pra reserva
                
                # 3. Sorteio Equilibrado dos Titulares
                random.shuffle(pool_titulares)
                pool_titulares = sorted(pool_titulares, key=lambda x: x['nivel']) # Agrupa por nivel
                
                verde = []
                preto = []
                
                # Algoritmo Snake
                niveis = sorted(list(set([p['nivel'] for p in pool_titulares])))
                for nv in niveis:
                    jogs = [p for p in pool_titulares if p['nivel'] == nv]
                    random.shuffle(jogs)
                    for j in jogs:
                        if len(verde) <= len(preto): verde.append(j['nome'])
                        else: preto.append(j['nome'])
                
                # Salva na Sessão (Congela os times)
                st.session_state['time_verde'] = verde
                st.session_state['time_preto'] = preto
                
                # Inicia a fila de espera viva com quem sobrou
                st.session_state['reservas_vivos'] = [p['nome'] for p in pool_reservas]
                st.rerun()

            # --- EXIBIÇÃO E FILA VIVA ---
            if 'time_verde' in st.session_state:
                st.divider()
                st.subheader("⚽ Times em Campo")
                ca, cb = st.columns(2)
                ca.success(f"VERDE ({len(st.session_state['time_verde'])})")
                for x in st.session_state['time_verde']: ca.write(f"- {x}")
                
                cb.error(f"PRETO ({len(st.session_state['time_preto'])})")
                for x in st.session_state['time_preto']: cb.write(f"- {x}")
                
                st.divider()
                st.subheader("⏱️ Banco de Reservas / Fila de Espera")
                st.warning("Adicione aqui quem chegar DEPOIS do sorteio.")
                
                # Fila Viva
                if st.session_state['reservas_vivos']:
                    for i, r in enumerate(st.session_state['reservas_vivos']):
                        st.write(f"**{i+1}º** {r}")
                else:
                    st.write("Banco vazio.")
                
                # Adicionar Atrasado na Fila
                c_late1, c_late2 = st.columns([2, 1])
                with c_late1:
                    atrasado_nome = st.text_input("Nome do Atrasado:")
                with c_late2:
                    if st.button("Adicionar na Fila"):
                        if atrasado_nome:
                            st.session_state['reservas_vivos'].append(f"{atrasado_nome} (Atrasado)")
                            st.rerun()
                
                # AUDITORIA FINAL (VERIFICAR FALTOSOS)
                if lista_zap_texto:
                    st.divider()
                    st.subheader("🔍 Auditoria de Faltosos")
                    todos_no_app = st.session_state['time_verde'] + st.session_state['time_preto'] + st.session_state['reservas_vivos']
                    # Limpa sufixos (D) e (Atrasado) para comparar
                    todos_limpos = [n.split(" (")[0].strip().lower() for n in todos_no_app]
                    
                    # Verifica quem do elenco está no zap mas não no app
                    faltosos = []
                    nomes_elenco = sorted(df_elenco['nome'].astype(str).tolist())
                    
                    for n in nomes_elenco:
                        if n.lower() in lista_zap_texto.lower() and n.lower() not in todos_limpos:
                            faltosos.append(n)
                    
                    if faltosos:
                        st.error(f"🚨 FALTOSOS DETECTADOS ({len(faltosos)}):")
                        st.write(", ".join(faltosos))
                        st.session_state['lista_faltosos'] = faltosos # Salva para o resumo
                    else:
                        st.success("✅ Todos compareceram!")

# === ABA 2: SÚMULA (INTEGRADA) ===
if user_role == "admin":
    with t_sumula:
        st.header("Súmula")
        dt = st.date_input("Data", datetime.today(), key="data_sumula")
        
        # PREENCHIMENTO AUTOMÁTICO (INTEGRAÇÃO)
        # Se houve sorteio, pega todo mundo que está nos times + reservas
        pre_selecionados = []
        if 'time_verde' in st.session_state:
            # Remove sufixos (D) ou (Atrasado) para bater com a lista de nomes do elenco se possível, 
            # mas o multiselect precisa do valor exato.
            # Como a lista de sorteio tem sufixos e a do elenco não, vamos manter os nomes crus para mensalistas
            # e adicionar os "estranhos" no campo de diaristas.
            
            todos_sorteio = st.session_state.get('time_verde',[]) + st.session_state.get('time_preto',[])
            
            mensalistas_sorteio = [n for n in todos_sorteio if " (D)" not in n and " (Atrasado)" not in n]
            pre_selecionados = mensalistas_sorteio
        
        mens_list = sorted(df_elenco['nome'].astype(str).tolist()) if not df_elenco.empty else []
        
        # Usa sessão se disponível, senão vazio
        def_m = [x for x in pre_selecionados if x in mens_list]
        
        c1, c2 = st.columns(2)
        with c1:
            jog = st.multiselect("Jogaram (Mensalistas):", mens_list, default=def_m)
            
            # Monta texto padrão para diaristas/atrasados com base no sorteio
            texto_diaristas_auto = ""
            if 'time_verde' in st.session_state:
                todos_sorteio = st.session_state.get('time_verde',[]) + st.session_state.get('time_preto',[]) + st.session_state.get('reservas_vivos',[])
                extras = [n for n in todos_sorteio if " (D)" in n or " (Atrasado)" in n]
                texto_diaristas_auto = "\n".join(extras)
            
            dtx = st.text_area("Diaristas / Atrasados:", value=texto_diaristas_auto, height=150)
            ld = [x.strip() for x in dtx.split('\n') if x.strip()]
        with c2: 
            just = st.multiselect("Justificaram:", [m for m in mens_list if m not in jog])
        
        st.divider(); r1, r2 = st.columns(2)
        v = r1.radio("Vencedor", ["Verde", "Preto", "Empate"], horizontal=True)
        with r2:
            lf = jog + ld
            gm = {}; score_verde = 0; score_preto = 0
            if lf:
                qg = st.multiselect("Gols:", lf)
                if qg:
                    cols = st.columns(3)
                    for i, a in enumerate(qg):
                        t_jog = "Verde"
                        # Tenta descobrir o time automaticamente pelo sorteio
                        if 'time_preto' in st.session_state and a in st.session_state['time_preto']:
                            t_jog = "Preto"
                        elif not df_elenco.empty: # Fallback cadastro
                            row = df_elenco[df_elenco['nome'] == a]
                            if not row.empty: t_jog = row.iloc[0]['time']
                        
                        gols = cols[i%3].number_input(f"{a}", 1, 20, 1, key=f"g_{a}")
                        gm[a] = gols
                        if t_jog == "Verde": score_verde += gols
                        elif t_jog == "Preto": score_preto += gols

        c_save, c_print = st.columns([1, 1])
        if c_save.button("💾 SALVAR SÚMULA", type="primary"):
            hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
            gid = int(datetime.now().timestamp())
            nv = []
            for p in lf: nv.append({"id": gid, "data": str(dt), "jogador": p, "tipo_registro": "Jogo", "gols": gm.get(p,0), "vencedor": v})
            for j in just: nv.append({"id": gid, "data": str(dt), "jogador": j, "tipo_registro": "Justificado", "gols": 0, "vencedor": ""})
            
            if save_data(pd.concat([hist, pd.DataFrame(nv)]), "jogos"):
                st.toast("Súmula Salva!", icon="✅")
                
                # --- GERAÇÃO AUTOMÁTICA DO RESUMO DA SEMANA NO SAVE ---
                texto_resumo = f"📢 **RESUMO DA RODADA** - {datetime.today().strftime('%d/%m')}\n\n"
                
                if 'time_verde' in st.session_state:
                    titulares = st.session_state['time_verde'] + st.session_state['time_preto']
                    texto_resumo += f"⚽ **1º Tempo (Titulares - {len(titulares)}):**\n"
                    texto_resumo += ", ".join(titulares) + "\n\n"
                    
                    # Quem jogou (Súmula) MAS não era titular = Entrou depois
                    entrou_depois = [p for p in lf if p not in titulares]
                    if entrou_depois:
                        texto_resumo += f"🔄 **Entraram no decorrer (2º Tempo):**\n"
                        for p in entrou_depois: texto_resumo += f"- {p}\n"
                
                if 'lista_faltosos' in st.session_state and st.session_state['lista_faltosos']:
                    texto_resumo += f"\n🚨 **Faltosos (Lista do Zap):**\n"
                    texto_resumo += ", ".join(st.session_state['lista_faltosos'])
                
                save_data(pd.DataFrame([{"texto": texto_resumo}]), "resumo_semana")

        if gm:
            with c_print:
                placar_v_man = st.number_input("Verde", value=score_verde, min_value=0, key="pv_man")
                placar_p_man = st.number_input("Preto", value=score_preto, min_value=0, key="pp_man")
                img_card = gerar_card_jogo(str(dt), placar_v_man, placar_p_man, gm, df_elenco)
                st.download_button("📸 Card do Jogo", img_card, f"jogo_{dt}.png", "image/png")

# === ABA 3: RESUMO SEMANAL (PÚBLICO) ===
with t_resumo:
    st.header("📢 Resumo da Rodada")
    df_resumo = load_data("resumo_semana", ["texto"])
    texto_atual = df_resumo.iloc[0]['texto'] if not df_resumo.empty else "Resumo será gerado após salvar a súmula."
    
    if user_role == "admin":
        st.write("Edite o resumo se houver mudanças manuais:")
        with st.form("edit_resumo"):
            novo_texto = st.text_area("Texto do Resumo", value=texto_atual, height=300)
            if st.form_submit_button("Salvar Resumo"):
                save_data(pd.DataFrame([{"texto": novo_texto}]), "resumo_semana")
                st.success("Atualizado!")
                st.rerun()
    else:
        st.info("Informações oficiais pós-jogo.")
        st.markdown(texto_atual)

# === ABA 4: ELENCO ===
if user_role == "admin":
    with t_elenco:
        st.header("Gerenciar Elenco")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("➕ Adicionar")
            with st.form("form_add_jogador", clear_on_submit=True):
                n = st.text_input("Nome").strip()
                t = st.selectbox("Time", ["Verde", "Preto", "Ambos"])
                tp = st.selectbox("Tipo", ["Mensalista", "Diarista Frequente"])
                nv = st.selectbox("Nível (1=Craque, 3=Iniciante)", [1, 2, 3], index=1)
                
                submitted_add = st.form_submit_button("Adicionar Jogador")
                if submitted_add:
                    if n and n not in df_elenco['nome'].values:
                        novo_df = pd.concat([df_elenco, pd.DataFrame([{"nome":n,"time":t,"tipo":tp, "nivel": nv, "punicao": "Não"}])], ignore_index=True)
                        if save_data(novo_df, "elenco"): st.success(f"{n} Adicionado!"); st.rerun()
                    elif n in df_elenco['nome'].values:
                        st.error("Nome já existe!")
                    else:
                        st.warning("Digite um nome!")

        with c2:
            st.subheader("✏️ Editar")
            if not df_elenco.empty:
                def formatar_nome_display(nome_original):
                    row = df_elenco[df_elenco['nome'] == nome_original]
                    if not row.empty:
                        time = row.iloc[0]['time']
                        nivel = row.iloc[0]['nivel']
                        pun = " (Punido)" if row.iloc[0]['punicao'] == "Sim" else ""
                        return f"{nome_original} - Nv {nivel}{pun}"
                    return nome_original
                
                s = st.selectbox("Selecione:", sorted(df_elenco['nome'].astype(str).tolist()), format_func=formatar_nome_display)
                
                if s:
                    r = df_elenco[df_elenco['nome']==s].iloc[0]
                    with st.form("form_edit_jogador"):
                        try: ix = ["Verde","Preto","Ambos"].index(r['time'])
                        except: ix = 0
                        try: ixp = ["Mensalista","Diarista Frequente"].index(r['tipo'])
                        except: ixp = 0
                        try: ixn = [1, 2, 3].index(int(r['nivel']))
                        except: ixn = 1
                        try: ixpuni = ["Não", "Sim"].index(r['punicao'])
                        except: ixpuni = 0
                        
                        nt = st.selectbox("Time:", ["Verde","Preto","Ambos"], index=ix)
                        ntp = st.selectbox("Tipo:", ["Mensalista","Diarista Frequente"], index=ixp)
                        nnv = st.selectbox("Nível:", [1, 2, 3], index=ixn)
                        npuni = st.selectbox("⚠️ Punição (Faltou):", ["Não", "Sim"], index=ixpuni)
                        
                        c_bt1, c_bt2 = st.columns(2)
                        save_btn = c_bt1.form_submit_button("💾 SALVAR")
                        del_btn = c_bt2.form_submit_button("🗑️ EXCLUIR")
                        
                        if save_btn:
                            df_elenco.loc[df_elenco['nome']==s, 'time'] = nt
                            df_elenco.loc[df_elenco['nome']==s, 'tipo'] = ntp
                            df_elenco.loc[df_elenco['nome']==s, 'nivel'] = nnv
                            df_elenco.loc[df_elenco['nome']==s, 'punicao'] = npuni
                            save_data(df_elenco, "elenco"); st.rerun()
                        if del_btn:
                            save_data(df_elenco[df_elenco['nome']!=s], "elenco"); st.rerun()

# === ABA 5: FINANCEIRO ===
with t_fin:
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
    
    st.info(f"Mês Atual ({mes_atual}): {pagos_count} pagos de {total_atletas}")

    if user_role in ["admin", "finance"]:
        with st.form("form_financeiro_checks"):
            edited_checks = st.data_editor(df_checks, use_container_width=True, hide_index=True, key="editor_fin")
            if st.form_submit_button("💾 SALVAR LISTA (CONFIRMAR)"):
                save_data(edited_checks, "financeiro"); st.success("Atualizado!"); st.rerun()
    else:
        st.dataframe(df_checks[['nome']].rename(columns={"nome": "Atleta"}), use_container_width=True, hide_index=True)

# === ABA 6: COFRE ===
with t_cofre:
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
        with st.expander("➕ Novo Lançamento", expanded=True):
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
                        save_data(df_mov, "saidas"); st.success("Ok!"); st.rerun()
        
        if not df_mov.empty:
            df_mov['Data'] = pd.to_datetime(df_mov['Data'], errors='coerce')
            with st.form("form_cofre_tabela"):
                edited_df = st.data_editor(
                    df_mov,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="dynamic",
                    column_config={"Valor": st.column_config.NumberColumn(format="R$ %.2f"), "Data": st.column_config.DateColumn(format="DD/MM/YYYY")},
                    key="editor_cofre"
                )
                if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    edited_df['Data'] = edited_df['Data'].astype(str)
                    save_data(edited_df, "saidas"); st.success("Atualizado!"); st.rerun()
            
            with st.expander("🗑️ Excluir"):
                df_temp = df_mov.copy().sort_values("Data", ascending=False)
                opcoes = [f"[{i}] {r['Descricao']} (R$ {r['Valor']})" for i, r in df_temp.iterrows()]
                sel = st.selectbox("Item:", options=opcoes, key="sel_del")
                if st.button("🗑️ EXCLUIR", key="btn_del"):
                    idx = int(sel.split("]")[0].replace("[", ""))
                    df_novo = df_mov.drop(idx)
                    df_novo['Data'] = df_novo['Data'].astype(str)
                    save_data(df_novo, "saidas"); st.success("Feito!"); st.rerun()

# === ABA 7: ESTATÍSTICAS ===
with t_estat:
    st.header("📊 Estatísticas")
    hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
    if not hist.empty:
        ca, cb = st.columns(2)
        with ca:
            st.subheader("Artilharia")
            hist['gols'] = pd.to_numeric(hist['gols'], errors='coerce').fillna(0)
            g = hist[hist['gols']>0].groupby("jogador")['gols'].sum().sort_values(ascending=False).reset_index()
            st.dataframe(g, use_container_width=True, hide_index=True)
            st.download_button("📸 Baixar", gerar_imagem_bonita(g.rename(columns={"jogador":"ATLETA", "gols":"GOLS"}), "ARTILHARIA"), "artilharia.png")
        with cb:
            st.subheader("Presença")
            j = hist[hist['tipo_registro']=='Jogo'].groupby("jogador").size().rename("Jogos")
            st.dataframe(j.sort_values(ascending=False), use_container_width=True)

# === ABA 8: AJUSTES (ADMIN) ===
if user_role == "admin":
    with t_ajustes:
        st.header("Ajustes")
        st.info("Para punir um jogador (Lista Negra), vá na aba 'Elenco', clique em Editar e mude Punição para 'Sim'.")
        
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
