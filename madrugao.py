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
        df = pd.DataFrame(data)
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception as e:
        st.error(f"Erro ao ler dados: {e}")
        return pd.DataFrame(columns=expected_cols)

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
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

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
        save_data(df, "elenco")
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

if is_admin:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎲 Sorteio", "📝 Súmula", "👥 Elenco", "💰 Financeiro", "📊 Estatísticas", "⚙️ Ajustes"
    ])
else:
    tab5, tab4 = st.tabs(["📊 Estatísticas", "💰 Financeiro"])
    tab1 = tab2 = tab3 = tab6 = st.container()

# === ABA 1: SORTEIO ===
if is_admin:
    with tab1:
        st.header("Montar Times")
        c1, c2 = st.columns([1, 2])
        with c1:
            if not df_elenco.empty:
                nomes = sorted(df_elenco['nome'].astype(str).tolist())
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
                    st.error("Ninguém selecionado!")
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

# === ABA 2: SÚMULA ===
if is_admin:
    with tab2:
        st.header("Súmula")
        dt = st.date_input("Data", datetime.today())
        mens_list = sorted(df_elenco['nome'].astype(str).tolist()) if not df_elenco.empty else []
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
        
        if st.button("💾 SALVAR SÚMULA", type="primary"):
            hist = load_data("jogos", ["id", "data", "jogador", "tipo_registro", "gols", "vencedor"])
            gid = int(datetime.now().timestamp())
            nv = []
            for p in lf: nv.append({"id": gid, "data": str(dt), "jogador": p, "tipo_registro": "Jogo", "gols": gm.get(p,0), "vencedor": v})
            for j in just: nv.append({"id": gid, "data": str(dt), "jogador": j, "tipo_registro": "Justificado", "gols": 0, "vencedor": ""})
            
            if save_data(pd.concat([hist, pd.DataFrame(nv)]), "jogos"):
                st.toast("Súmula Salva!", icon="✅")

# === ABA 3: ELENCO ===
if is_admin:
    with tab3:
        st.header("Gerenciar Elenco")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("➕ Adicionar Novo")
            n = st.text_input("Nome").strip()
            t = st.selectbox("Time", ["Verde", "Preto", "Ambos"])
            tp = st.selectbox("Tipo", ["Mensalista", "Diarista Frequente"])
            
            if st.button("Adicionar Jogador"):
                if not n:
                    st.warning("Digite um nome!")
                elif n in df_elenco['nome'].values:
                    st.error("Esse nome já existe!")
                else:
                    novo_df = pd.concat([df_elenco, pd.DataFrame([{"nome":n,"time":t,"tipo":tp}])], ignore_index=True)
                    if save_data(novo_df, "elenco"):
                        st.success(f"{n} adicionado!")
                        st.rerun()

        with c2:
            st.subheader("✏️ Editar / Remover")
            if not df_elenco.empty:
                def formatar_nome_display(nome_original):
                    row = df_elenco[df_elenco['nome'] == nome_original]
                    if not row.empty:
                        time = row.iloc[0]['time']
                        if time == 'Verde': return f"{nome_original} 💚"
                        elif time == 'Preto': return f"{nome_original} 🖤"
                        elif time == 'Ambos': return f"{nome_original} (C)"
                    return nome_original

                nomes_lista = sorted(df_elenco['nome'].astype(str).tolist())
                s = st.selectbox("Selecione:", nomes_lista, format_func=formatar_nome_display)
                
                if s:
                    r = df_elenco[df_elenco['nome']==s].iloc[0]
                    try: ix = ["Verde","Preto","Ambos"].index(r['time'])
                    except: ix = 0
                    try: ixp = ["Mensalista","Diarista Frequente"].index(r['tipo'])
                    except: ixp = 0
                    nt = st.selectbox("Novo Time:", ["Verde","Preto","Ambos"], index=ix, key="edit_time")
                    ntp = st.selectbox("Novo Tipo:", ["Mensalista","Diarista Frequente"], index=ixp, key="edit_tipo")
                    
                    cb1, cb2 = st.columns(2)
                    if cb1.button("💾 SALVAR ALTERAÇÃO"):
                        df_elenco.loc[df_elenco['nome']==s, 'time'] = nt
                        df_elenco.loc[df_elenco['nome']==s, 'tipo'] = ntp
                        if save_data(df_elenco, "elenco"):
                            st.success("Alteração salva!")
                            st.rerun()
                    if cb2.button("🗑️ EXCLUIR"):
                        novo_df = df_elenco[df_elenco['nome']!=s]
                        if save_data(novo_df, "elenco"):
                            st.warning(f"{s} removido!")
                            st.rerun()

# === ABA 4: FINANCEIRO (RESUMO SÓ PARA ADMIN) ===
with tab4:
    st.header("💰 Financeiro")
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
        
        # SEPARAÇÃO DO QUE CADA UM VÊ
        if is_admin:
            # --- DASHBOARD (EXCLUSIVO ADMIN) ---
            hoje = datetime.today()
            meses_map = {1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"}
            mes_atual = meses_map[hoje.month]
            dia_hoje = hoje.day

            pagos = df_fin[df_fin[mes_atual].apply(lambda x: x == True or str(x).upper() == "TRUE")].shape[0]
            total = df_fin.shape[0]
            faltam = total - pagos
            inadimplentes = faltam if dia_hoje > 20 else 0

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Atletas", total)
            k2.metric(f"Pagos ({mes_atual})", pagos)
            k3.metric("Faltam Pagar", faltam)
            
            if inadimplentes > 0:
                k4.metric("🚨 Inadimplentes", inadimplentes, delta="-Atrasados", delta_color="inverse")
            else:
                k4.metric("Inadimplentes", "0", delta="No prazo")

            st.divider()
            st.info("Modo Admin: Edite e salve.")
            edited = st.data_editor(df_fin, use_container_width=True, hide_index=True)
            if st.button("SALVAR PAGAMENTOS"):
                if save_data(edited, "financeiro"):
                    st.success("Financeiro Atualizado!")
                    st.rerun()
        else:
            # --- VISITANTE (SÓ VÊ A TABELA, SEM DASHBOARD) ---
            st.info("Transparência: Confira abaixo a lista de pagamentos.")
            st.dataframe(df_fin, use_container_width=True, hide_index=True)
    else:
        st.warning("Sem dados.")

# === ABA 5: ESTATÍSTICAS ===
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
        st.info("Sem dados ainda.")

# === ABA 6: AJUSTES ===
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
                    if save_data(hist[hist['id']!=r['id']], "jogos"):
                        st.rerun()
