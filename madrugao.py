import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Pelada Madrugão", page_icon="⚽", layout="wide")

st.title("⚽ Gestão Madrugão")

# --- CONEXÃO COM GOOGLE SHEETS ---
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
    # ID DA PLANILHA
    return client.open_by_key("1OSxEwiE3voMOd-EI6CJ034torY-K7oFoz8EReyXkmPA")

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
        return pd.DataFrame(data)
    except:
        return pd.DataFrame(columns=expected_cols)

def save_data(df, sheet_name):
    sh = get_connection()
    try:
        worksheet = sh.worksheet(sheet_name)
    except:
        worksheet = sh.add_worksheet(title=sheet_name, rows=100, cols=20)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- LISTA PADRÃO ---
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

def carregar_elenco():
    df = load_data("elenco", ["nome", "time", "tipo"])
    if df.empty:
        df = pd.DataFrame(LISTA_PADRAO)
        try: save_data(df, "elenco")
        except: pass
    return df

# --- LOGIN ---
SENHA_ADMIN = st.secrets.get("admin_password", "1234")

st.sidebar.title("🔒 Área Restrita")
senha_digitada = st.sidebar.text_input("Senha de Admin", type="password")
is_admin = senha_digitada == SENHA_ADMIN

if is_admin:
    st.sidebar.success("Modo Admin: ATIVADO")
else:
    st.sidebar.info("Modo Visitante")

df_elenco = carregar_elenco()

# --- DEFINIÇÃO DAS ABAS (ADMIN VS VISITANTE) ---
if is_admin:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎲 Sorteio", "📝 Súmula", "👥 Elenco", "💰 Financeiro", "📊 Estatísticas", "⚙️ Ajustes"
    ])
else:
    # Visitante agora vê Estatísticas E Financeiro
    tab5, tab4 = st.tabs(["📊 Estatísticas", "💰 Financeiro"])
    # As outras abas ficam vazias
    tab1 = tab2 = tab3 = tab6 = st.container()

# === ABA 1: SORTEIO (SÓ ADMIN) ===
if is_admin:
    with tab1:
        st.header("Montar Times")
        c1, c2 = st.columns([1, 2])
        with c1:
            if not df_elenco.empty:
                nomes = sorted(df_elenco['nome'].tolist())
                mens = st.multiselect("Presença (Ordem):", nomes, key="t1_m")
                diar = st.text_area("Diaristas:", key="t1_d")
            else:
                mens, diar = [], ""
        with c2:
            if st.button("SORTEAR", type="primary"):
                st.session_state['mem_m'] = mens
                st.session_state['mem_d'] = diar
                l_diar = [x.strip() for x in diar.split('\n') if x.strip()]
                elenco = mens + l_diar
                if not elenco:
                    st.error("Vazio!")
                else:
                    MAX = 20
                    tit = elenco[:MAX]
                    res = elenco[MAX:]
                    p_df = df_elenco[df_elenco['nome'].isin(tit)]
                    vd = p_df[p_df['time']=='Verde']['nome'].tolist()
                    pt = p_df[p_df['time']=='Preto']['nome'].tolist()
                    cor = p_df[p_df['time']=='Ambos']['nome'].tolist()
                    d_tit = [x for x in tit if x not in df_elenco['nome'].tolist()]
                    pool = cor + d_tit
                    random.shuffle(pool)
                    verde, preto = list(vd), list(pt)
                    for c in pool:
                        dn = f"{c} (D)" if c in d_tit else c
                        if len(verde) <= len(preto): verde.append(dn)
                        else: preto.append(dn)
                    ca, cb = st.columns(2)
                    ca.success(f"VERDE ({len(verde)})"); [ca.write(f"- {x}") for x in verde]
                    cb.error(f"PRETO ({len(preto)})"); [cb.write(f"- {x}") for x in preto]
                    if res:
                        st.divider(); st.write("**Reservas:**")
                        for i, r in enumerate(res):
                            idx = (MAX-1)-i
                            if idx>=0: st.write(f"{MAX+i+1}º {r} entra por {tit[idx]}")

# === ABA 2: SÚMULA (SÓ ADMIN) ===
if is_admin:
    with tab2:
        st.header("Súmula")
        dt = st.date_input("Data", datetime.today())
        mens_list = sorted(df_elenco['nome'].tolist()) if not df_elenco.empty else []
        def_m = [x for x in st.session_state.get('mem_m', []) if x in mens_list]
        def_d = st.session_state.get('mem_d', "")
        
        c1, c2 = st.columns(2)
        with c1:
            jog = st.multiselect("Jogaram:", mens_list, default=def_m)
            dtx = st.text_area("Diaristas Súmula:", value=def_d)
            ld = [x.strip() for x in dtx.split('\n') if x.strip()]
            if not ld: ld = [x.strip() for x in dtx.split(',') if x.strip()]
        with c2:
            just = st.multiselect("Justificaram:", [m for m in mens_list if m not in jog])
        
        st.divider()
        r1, r2 = st.columns(2)
        v = r1.radio("Vencedor", ["Verde", "Preto", "Empate"], horizontal=True)
        with r2:
            lf = jog + ld
            gm = {}
            if lf:
                qg = st.multiselect("Gols:", lf)
                if qg:
                    cols = st.columns(3)
                    for i, a in enumerate(qg):
                        gm[a] = cols[i%3].number_input(f"{a}", 1, 20, 1, key=f"g_{a}")
        
        if st.button("💾 SALVAR", type="primary"):
            try:
                hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
                gid = int(datetime.now().timestamp())
                nv = []
                for p in lf: nv.append({"id": gid, "data": str(dt), "jogador": p, "tipo_registro": "Jogo", "gols": gm.get(p,0), "vencedor": v})
                for j in just: nv.append({"id": gid, "data": str(dt), "jogador": j, "tipo_registro": "Justificado", "gols": 0, "vencedor": ""})
                save_data(pd.concat([hist, pd.DataFrame(nv)]), "jogos")
                st.toast("Salvo!", icon="✅")
            except Exception as e: st.error(str(e))

# === ABA 3: ELENCO (SÓ ADMIN) ===
if is_admin:
    with tab3:
        st.header("Elenco")
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nome")
            t = st.selectbox("Time", ["Verde", "Preto", "Ambos"])
            tp = st.selectbox("Tipo", ["Mensalista", "Diarista Frequente"])
            if st.button("Add"):
                if n and n not in df_elenco['nome'].values:
                    save_data(pd.concat([df_elenco, pd.DataFrame([{"nome":n,"time":t,"tipo":tp}])], ignore_index=True), "elenco")
                    st.rerun()
        with c2:
            if not df_elenco.empty:
                s = st.selectbox("Edit:", df_elenco['nome'].tolist())
                if s:
                    r = df_elenco[df_elenco['nome']==s].iloc[0]
                    try: ix = ["Verde","Preto","Ambos"].index(r['time'])
                    except: ix = 0
                    nt = st.selectbox("Novo Time:", ["Verde","Preto","Ambos"], index=ix)
                    ntp = st.selectbox("Novo Tipo:", ["Mensalista","Diarista Frequente"], index=0)
                    if st.button("Salvar Edit"):
                        df_elenco.loc[df_elenco['nome']==s, 'time'] = nt
                        df_elenco.loc[df_elenco['nome']==s, 'tipo'] = ntp
                        save_data(df_elenco, "elenco")
                        st.rerun()
                    if st.button("Del"):
                        save_data(df_elenco[df_elenco['nome']!=s], "elenco")
                        st.rerun()

# === ABA 4: FINANCEIRO (MISTO) ===
# Essa aba agora carrega para todo mundo, mas exibe diferente
with tab4:
    st.header("💰 Financeiro")
    
    # Lógica de Carregamento (Igual para os dois)
    if not df_elenco.empty:
        df_mens = df_elenco[df_elenco['tipo'] == 'Mensalista'][['nome']].sort_values('nome')
        cols = ["nome", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        df_fin = load_data("financeiro", cols)
        
        # Sincronia
        if not df_fin.empty:
            for nm in df_mens['nome']:
                if nm not in df_fin['nome'].values:
                    nv = {k: False for k in cols if k!='nome'}
                    nv['nome'] = nm
                    df_fin = pd.concat([df_fin, pd.DataFrame([nv])], ignore_index=True)
            df_fin = df_fin[df_fin['nome'].isin(df_mens['nome'])]
        else:
            df_fin = df_mens.copy()
            for c in cols[1:]: df_fin[c] = False
    
        # === A DIFERENÇA VEM AQUI ===
        if is_admin:
            # Admin: Pode editar e salvar
            st.info("Modo Admin: Você pode alterar os pagamentos.")
            edited = st.data_editor(df_fin, use_container_width=True, hide_index=True)
            if st.button("💾 SALVAR PAGAMENTOS"):
                save_data(edited, "financeiro")
                st.success("Financeiro Atualizado!")
        else:
            # Visitante: Só vê a tabela travada
            st.info("Transparência: Acompanhe quem já realizou o pagamento.")
            st.dataframe(df_fin, use_container_width=True, hide_index=True)
    else:
        st.warning("Cadastre jogadores para ver o financeiro.")

# === ABA 5: ESTATÍSTICAS (PÚBLICO) ===
with tab5:
    st.header("📊 Estatísticas")
    hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
    if not hist.empty:
        vt = hist[['id','vencedor']].drop_duplicates()['vencedor'].value_counts()
        c1,c2,c3 = st.columns(3)
        c1.metric("Verde", vt.get("Verde",0))
        c2.metric("Preto", vt.get("Preto",0))
        c3.metric("Empates", vt.get("Empate",0))
        
        ca, cb = st.columns(2)
        with ca:
            st.subheader("Artilharia")
            hist['gols'] = pd.to_numeric(hist['gols'], errors='coerce').fillna(0)
            g = hist[hist['gols']>0].groupby("jogador")['gols'].sum().sort_values(ascending=False).reset_index()
            st.dataframe(g, use_container_width=True)
        with cb:
            st.subheader("Presença")
            j = hist[hist['tipo_registro']=='Jogo'].groupby("jogador").size().rename("Jogos")
            ju = hist[hist['tipo_registro']=='Justificado'].groupby("jogador").size().rename("Justif.")
            f = pd.concat([j,ju], axis=1).fillna(0).astype(int)
            f['Total'] = f['Jogos'] + f['Justif.']
            st.dataframe(f.sort_values('Jogos', ascending=False), use_container_width=True)
    else:
        st.info("Sem dados.")

# === ABA 6: AJUSTES (SÓ ADMIN) ===
if is_admin:
    with tab6:
        st.header("Ajustes")
        hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
        if not hist.empty:
            jg = hist.drop_duplicates(subset=['id'])[['id','data','vencedor']].sort_values('data', ascending=False)
            for i, r in jg.iterrows():
                c1,c2 = st.columns([4,1])
                c1.write(f"📅 {r['data']} - {r['vencedor']}")
                if c2.button("Apagar", key=f"d_{r['id']}"):
                    save_data(hist[hist['id']!=r['id']], "jogos")
                    st.rerun()
