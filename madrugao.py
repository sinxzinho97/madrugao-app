import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Pelada Madrugão", page_icon="⚽", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
def get_connection():
    # Define o escopo de permissão
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Pega as credenciais que estarão salvas nos Segredos do Streamlit Cloud
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
    # Abre a planilha pelo nome
    return client.open("1OSxEwiE3voMOd-EI6CJ034torY-K7oFoz8EReyXkmPA")

# Função para ler dados de uma aba específica
def load_data(sheet_name, expected_cols):
    try:
        sh = get_connection()
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=expected_cols)
        return pd.DataFrame(data)
    except Exception as e:
        # Se a aba estiver vazia ou der erro, retorna vazio
        return pd.DataFrame(columns=expected_cols)

# Função para salvar dados (apaga tudo e reescreve - simples e seguro)
def save_data(df, sheet_name):
    sh = get_connection()
    try:
        worksheet = sh.worksheet(sheet_name)
    except:
        # Se a aba não existir, cria ela
        worksheet = sh.add_worksheet(title=sheet_name, rows=100, cols=20)
    
    worksheet.clear()
    # Adiciona cabeçalho + dados
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- LISTA PADRÃO (SE A PLANILHA ESTIVER VAZIA) ---
LISTA_PADRAO = [
    {"nome": "Alex", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Anderson", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Danoninho", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Duda", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Jailson", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Lázaro", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Leo", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Neguinho", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Neymar", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Péu", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Sr. Jailton", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "Val do Ferro", "time": "Verde", "tipo": "Mensalista"},
    {"nome": "André", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Berg", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Lucas", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Marcos", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Mudinho", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Renê", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Roberto", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Rodrigo", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Rômullo", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Ryan", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "The Bass", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Thiago G", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Will", "time": "Preto", "tipo": "Mensalista"},
    {"nome": "Rafa Mago", "time": "Preto", "tipo": "Mensalista"}, 
    {"nome": "Alysson", "time": "Ambos", "tipo": "Mensalista"},
    {"nome": "Belkior", "time": "Ambos", "tipo": "Mensalista"},
    {"nome": "Christopher", "time": "Ambos", "tipo": "Mensalista"},
    {"nome": "Helder", "time": "Ambos", "tipo": "Mensalista"},
    {"nome": "Sr. José", "time": "Ambos", "tipo": "Mensalista"},
    {"nome": "Sr. Vitor", "time": "Ambos", "tipo": "Mensalista"},
    {"nome": "Professor", "time": "Ambos", "tipo": "Mensalista"},
]

# Inicializa elenco se estiver vazio
def carregar_elenco():
    df = load_data("elenco", ["nome", "time", "tipo"])
    if df.empty:
        df = pd.DataFrame(LISTA_PADRAO)
        save_data(df, "elenco")
    return df

# --- LOGIN E SEGURANÇA ---
# Pega a senha dos segredos da nuvem (ou usa padrão local para teste)
SENHA_ADMIN = st.secrets.get("admin_password", "1234")

st.sidebar.title("🔒 Área Restrita")
senha_digitada = st.sidebar.text_input("Senha de Admin", type="password")
is_admin = senha_digitada == SENHA_ADMIN

if is_admin:
    st.sidebar.success("Modo Admin: ATIVADO")
else:
    st.sidebar.info("Modo Visitante")

st.title("⚽ Gestão Madrugão")

# --- DEBUG (Apagar depois que funcionar) ---
try:
    st.write("Tentando conectar com o e-mail:", st.secrets["gcp_service_account"]["client_email"])
except:
    st.error("Não consegui ler o e-mail dos segredos.")

# Carrega dados da nuvem
df_elenco = carregar_elenco()

# Controle de abas
if is_admin:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎲 Sorteio", "📝 Súmula", "👥 Elenco", "💰 Financeiro", "📊 Estatísticas", "⚙️ Ajustes"
    ])
else:
    st.info("Você está no modo visitante (Apenas Leitura).")
    tab5 = st.tabs(["📊 Estatísticas"])[0]
    tab1 = tab2 = tab3 = tab4 = tab6 = st.container()

# === ABA 1: SORTEIO ===
if is_admin:
    with tab1:
        st.header("Montar Times")
        col_input, col_result = st.columns([1, 2])
        with col_input:
            lista_nomes = df_elenco['nome'].tolist()
            lista_nomes.sort()
            presentes_mensalistas = st.multiselect("Selecione (Ordem de Chegada):", lista_nomes, key="t1_mens")
            diaristas_txt = st.text_area("Diaristas:", key="t1_diar")
        
        with col_result:
            if st.button("SORTEAR TIMES", type="primary"):
                st.session_state['mem_mens'] = presentes_mensalistas
                st.session_state['mem_diar'] = diaristas_txt
                
                lista_diar = [x.strip() for x in diaristas_txt.split('\n') if x.strip()]
                elenco_hoje = presentes_mensalistas + lista_diar
                
                if not elenco_hoje:
                    st.error("Ninguém selecionado!")
                else:
                    TITULARES_MAX = 20
                    titulares = elenco_hoje[:TITULARES_MAX]
                    reservas = elenco_hoje[TITULARES_MAX:]
                    
                    p_df = df_elenco[df_elenco['nome'].isin(titulares)]
                    verde_fixo = p_df[p_df['time'] == 'Verde']['nome'].tolist()
                    preto_fixo = p_df[p_df['time'] == 'Preto']['nome'].tolist()
                    coringas = p_df[p_df['time'] == 'Ambos']['nome'].tolist()
                    diar_tit = [x for x in titulares if x not in df_elenco['nome'].tolist()]
                    
                    todos_coringas = coringas + diar_tit
                    random.shuffle(todos_coringas)
                    
                    verde, preto = list(verde_fixo), list(preto_fixo)
                    for c in todos_coringas:
                        d_name = f"{c} (D)" if c in diar_tit else c
                        if len(verde) <= len(preto): verde.append(d_name)
                        else: preto.append(d_name)
                    
                    c1, c2 = st.columns(2)
                    c1.success(f"🟢 VERDE ({len(verde)})"); [c1.write(f"- {x}") for x in verde]
                    c2.error(f"⚫ PRETO ({len(preto)})"); [c2.write(f"- {x}") for x in preto]
                    
                    if reservas:
                        st.divider(); st.header("⏳ Reservas")
                        for i, r in enumerate(reservas):
                            idx_alvo = (TITULARES_MAX - 1) - i
                            if idx_alvo >= 0: st.write(f"**{TITULARES_MAX+i+1}º {r}** substitui **{titulares[idx_alvo]}**")

# === ABA 2: SÚMULA ===
if is_admin:
    with tab2:
        st.header("Registrar Jogo")
        data_jogo = st.date_input("Data", datetime.today())
        mensalistas = sorted(df_elenco['nome'].tolist())
        
        def_mens = [x for x in st.session_state.get('mem_mens', []) if x in mensalistas]
        def_diar = st.session_state.get('mem_diar', "")
        
        c1, c2 = st.columns(2)
        with c1:
            jogaram = st.multiselect("Jogaram:", mensalistas, default=def_mens)
            diar_txt = st.text_area("Diaristas (Súmula):", value=def_diar)
            l_diar = [x.strip() for x in diar_txt.split('\n') if x.strip()]
            if not l_diar: l_diar = [x.strip() for x in diar_txt.split(',') if x.strip()]
        with c2:
            justif = st.multiselect("Justificaram:", [m for m in mensalistas if m not in jogaram])
            
        st.divider()
        cr1, cr2 = st.columns(2)
        venc = cr1.radio("Resultado", ["Verde", "Preto", "Empate"], horizontal=True)
        
        with cr2:
            l_final = jogaram + l_diar
            gols_map = {}
            if l_final:
                quem_gol = st.multiselect("Artilheiros:", l_final)
                if quem_gol:
                    cg = st.columns(3)
                    for i, art in enumerate(quem_gol):
                        gols_map[art] = cg[i%3].number_input(f"{art}", 1, 20, 1, key=f"g_{art}")
        
        if st.button("💾 SALVAR NA NUVEM", type="primary"):
            try:
                df_hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
                gid = int(datetime.now().timestamp())
                novos = []
                for p in l_final:
                    novos.append({"id": gid, "data": str(data_jogo), "jogador": p, "tipo_registro": "Jogo", "gols": gols_map.get(p, 0), "vencedor": venc})
                for j in justif:
                    novos.append({"id": gid, "data": str(data_jogo), "jogador": j, "tipo_registro": "Justificado", "gols": 0, "vencedor": ""})
                
                save_data(pd.concat([df_hist, pd.DataFrame(novos)]), "jogos")
                st.toast("Salvo no Google Sheets!", icon="✅")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# === ABA 3: ELENCO ===
if is_admin:
    with tab3:
        st.header("Gerenciar Elenco")
        c1, c2 = st.columns(2)
        with c1:
            nn = st.text_input("Nome Novo")
            nt = st.selectbox("Time", ["Verde", "Preto", "Ambos"])
            ntp = st.selectbox("Tipo", ["Mensalista", "Diarista Frequente"])
            if st.button("Adicionar"):
                if nn and nn not in df_elenco['nome'].values:
                    novo = pd.DataFrame([{"nome": nn, "time": nt, "tipo": ntp}])
                    save_data(pd.concat([df_elenco, novo], ignore_index=True), "elenco")
                    st.rerun()
        with c2:
            sel = st.selectbox("Editar:", df_elenco['nome'].tolist())
            if sel:
                row = df_elenco[df_elenco['nome'] == sel].iloc[0]
                nnt = st.selectbox("Time:", ["Verde", "Preto", "Ambos"], index=["Verde", "Preto", "Ambos"].index(row['time']))
                nntp = st.selectbox("Tipo:", ["Mensalista", "Diarista Frequente"], index=0)
                cb1, cb2 = st.columns(2)
                if cb1.button("Salvar"):
                    df_elenco.loc[df_elenco['nome'] == sel, 'time'] = nnt
                    df_elenco.loc[df_elenco['nome'] == sel, 'tipo'] = nntp
                    save_data(df_elenco, "elenco")
                    st.rerun()
                if cb2.button("Excluir"):
                    save_data(df_elenco[df_elenco['nome'] != sel], "elenco")
                    st.rerun()

# === ABA 4: FINANCEIRO ===
if is_admin:
    with tab4:
        st.header("Financeiro")
        df_mens = df_elenco[df_elenco['tipo'] == 'Mensalista'][['nome']].sort_values('nome')
        cols_fin = ["nome", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        df_fin = load_data("financeiro", cols_fin)
        
        # Sincroniza nomes
        if not df_fin.empty:
            for nome in df_mens['nome']:
                if nome not in df_fin['nome'].values:
                    nova = {k: False for k in cols_fin if k != 'nome'}
                    nova['nome'] = nome
                    df_fin = pd.concat([df_fin, pd.DataFrame([nova])], ignore_index=True)
            df_fin = df_fin[df_fin['nome'].isin(df_mens['nome'])]
        else:
            df_fin = df_mens.copy()
            for c in cols_fin[1:]: df_fin[c] = False
            
        edited = st.data_editor(df_fin, use_container_width=True, hide_index=True)
        if st.button("Salvar Pagamentos"):
            save_data(edited, "financeiro")
            st.success("Salvo!")

# === ABA 5: ESTATÍSTICAS ===
with tab5:
    st.header("Estatísticas")
    df_hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
    if not df_hist.empty:
        vit = df_hist[['id', 'vencedor']].drop_duplicates()['vencedor'].value_counts()
        c1, c2, c3 = st.columns(3)
        c1.metric("Verde", vit.get("Verde", 0))
        c2.metric("Preto", vit.get("Preto", 0))
        c3.metric("Empates", vit.get("Empate", 0))
        
        ca, cf = st.columns(2)
        with ca:
            st.subheader("Artilharia")
            # Força conversão para numérico para evitar erro de string
            df_hist['gols'] = pd.to_numeric(df_hist['gols'], errors='coerce').fillna(0)
            g = df_hist[df_hist['gols'] > 0].groupby("jogador")['gols'].sum().sort_values(ascending=False).reset_index()
            st.dataframe(g, use_container_width=True)
        with cf:
            st.subheader("Presença")
            j = df_hist[df_hist['tipo_registro'] == 'Jogo'].groupby("jogador").size().rename("Jogos")
            ju = df_hist[df_hist['tipo_registro'] == 'Justificado'].groupby("jogador").size().rename("Justif.")
            final = pd.concat([j, ju], axis=1).fillna(0).astype(int)
            final['Total'] = final['Jogos'] + final['Justif.']
            st.dataframe(final.sort_values('Jogos', ascending=False), use_container_width=True)
    else:
        st.info("Sem dados na planilha ainda.")

# === ABA 6: AJUSTES ===
if is_admin:
    with tab6:
        st.header("Correção")
        df_hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
        if not df_hist.empty:
            jogos = df_hist.drop_duplicates(subset=['id'])[['id', 'data', 'vencedor']].sort_values('data', ascending=False)
            for i, row in jogos.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"📅 {row['data']} - {row['vencedor']}")
                if c2.button("Apagar", key=f"del_{row['id']}"):
                    df_novo = df_hist[df_hist['id'] != row['id']]
                    save_data(df_novo, "jogos")
                    st.rerun()