import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random
import matplotlib.pyplot as plt
import io
import os

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Pelada Madrugão", page_icon="🦉", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.write("")
    st.title("🔒 Acesso")

# --- TÍTULO ---
st.title("Pelada Madrugão 🦉 💚 🖤")

# --- CONEXÃO ---
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
        st.error(f"Erro ao ler dados ({sheet_name}): {e}")
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

# --- CARREGAMENTO GLOBAL DE DADOS FINANCEIROS ---
# 1. Checks
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

# 2. Movimentações (Cofre)
cols_mov = ["Data", "Descricao", "Valor"]
df_mov = load_data("saidas", cols_mov)
if not df_mov.empty: df_mov["Valor"] = pd.to_numeric(df_mov["Valor"], errors='coerce').fillna(0)

# Cálculos do Cofre
total_entradas = df_mov[df_mov["Valor"] > 0]["Valor"].sum()
total_saidas = abs(df_mov[df_mov["Valor"] < 0]["Valor"].sum())
saldo_caixa = total_entradas - total_saidas

# --- NAVEGAÇÃO (ABAS) ---
if user_role == "admin":
    # 7 Abas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🎲 Sorteio", "📝 Súmula", "👥 Elenco", "💰 Financeiro", "🏦 Cofre", "📊 Estatísticas", "⚙️ Ajustes"])
elif user_role == "finance":
    # 3 Abas
    tab4, tab5, tab6 = st.tabs(["💰 Financeiro", "🏦 Cofre", "📊 Estatísticas"])
    tab1=tab2=tab3=tab7=st.container()
else:
    # 3 Abas (Visualização)
    tab6, tab4, tab5 = st.tabs(["📊 Estatísticas", "💰 Financeiro", "🏦 Cofre"])
    tab1=tab2=tab3=tab7=st.container()

# === ABA 1: SORTEIO ===
if user_role == "admin":
    with tab1:
        st.header("Montar Times")
        c1, c2 = st.columns([1, 2])
        with c1:
            if not df_elenco.empty:
                nomes = sorted(df_elenco['nome'].astype(str).tolist())
                mens = st.multiselect("Presença:", nomes, key="t1_m")
                diar = st.text_area("Diaristas:", key="t1_d")
            else: mens, diar = [], ""
        with c2:
            if st.button("SORTEAR", type="primary"):
                st.session_state['mem_m'] = mens; st.session_state['mem_d'] = diar
                l_diar = [x.strip() for x in diar.split('\n') if x.strip()]
                elenco = mens + l_diar
                if not elenco: st.error("Ninguém selecionado!")
                else:
                    MAX = 20
                    tit = elenco[:MAX]; res = elenco[MAX:]
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
if user_role == "admin":
    with tab2:
        st.header("Súmula")
        dt = st.date_input("Data", datetime.today())
        mens_list = sorted(df_elenco['nome'].astype(str).tolist()) if not df_elenco.empty else []
        def_m = [x for x in st.session_state.get('mem_m', []) if x in mens_list]
        def_d = st.session_state.get('mem_d', "")
        
        c1, c2 = st.columns(2)
        with c1:
            jog = st.multiselect("Jogaram:", mens_list, default=def_m)
            dtx = st.text_area("Diaristas:", value=def_d)
            ld = [x.strip() for x in dtx.split('\n') if x.strip()]
            if not ld: ld = [x.strip() for x in dtx.split(',') if x.strip()]
        with c2: just = st.multiselect("Justificaram:", [m for m in mens_list if m not in jog])
        
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
                        if not df_elenco.empty:
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
                st.session_state['ultimo_placar'] = (score_verde, score_preto, gm)

        if gm:
            with c_print:
                placar_v_man = st.number_input("Verde", value=score_verde, min_value=0)
                placar_p_man = st.number_input("Preto", value=score_preto, min_value=0)
                img_card = gerar_card_jogo(str(dt), placar_v_man, placar_p_man, gm, df_elenco)
                st.download_button("📸 Card do Jogo", img_card, f"jogo_{dt}.png", "image/png")

# === ABA 3: ELENCO ===
if user_role == "admin":
    with tab3:
        st.header("Gerenciar Elenco")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("➕ Adicionar")
            n = st.text_input("Nome").strip()
            t = st.selectbox("Time", ["Verde", "Preto", "Ambos"])
            tp = st.selectbox("Tipo", ["Mensalista", "Diarista Frequente"])
            if st.button("Adicionar"):
                if n and n not in df_elenco['nome'].values:
                    novo_df = pd.concat([df_elenco, pd.DataFrame([{"nome":n,"time":t,"tipo":tp}])], ignore_index=True)
                    if save_data(novo_df, "elenco"): st.rerun()
        with c2:
            st.subheader("✏️ Editar")
            if not df_elenco.empty:
                def formatar_nome_display(nome_original):
                    row = df_elenco[df_elenco['nome'] == nome_original]
                    if not row.empty:
                        time = row.iloc[0]['time']
                        if time == 'Verde': return f"{nome_original} 💚"
                        elif time == 'Preto': return f"{nome_original} 🖤"
                        elif time == 'Ambos': return f"{nome_original} (C)"
                    return nome_original
                s = st.selectbox("Selecione:", sorted(df_elenco['nome'].astype(str).tolist()), format_func=formatar_nome_display)
                if s:
                    r = df_elenco[df_elenco['nome']==s].iloc[0]
                    try: ix = ["Verde","Preto","Ambos"].index(r['time'])
                    except: ix = 0
                    try: ixp = ["Mensalista","Diarista Frequente"].index(r['tipo'])
                    except: ixp = 0
                    nt = st.selectbox("Novo Time:", ["Verde","Preto","Ambos"], index=ix)
                    ntp = st.selectbox("Novo Tipo:", ["Mensalista","Diarista Frequente"], index=ixp)
                    c_bt1, c_bt2 = st.columns(2)
                    if c_bt1.button("Salvar"):
                        df_elenco.loc[df_elenco['nome']==s, 'time'] = nt; df_elenco.loc[df_elenco['nome']==s, 'tipo'] = ntp
                        save_data(df_elenco, "elenco"); st.rerun()
                    if c_bt2.button("Excluir"):
                        save_data(df_elenco[df_elenco['nome']!=s], "elenco"); st.rerun()

# === ABA 4: FINANCEIRO (LISTA DE CHECKS) ===
with tab4:
    st.header("💰 Controle de Pagamentos")
    
    # Inadimplência Visual
    hoje = datetime.today()
    meses_map = {1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"}
    mes_atual = meses_map[hoje.month]
    pagos_count = df_checks[df_checks[mes_atual] == True].shape[0]
    total_atletas = df_checks.shape[0]
    inadimplentes = total_atletas - pagos_count
    
    # Mini Dashboard
    c_f1, c_f2 = st.columns(2)
    c_f1.info(f"Mês Atual ({mes_atual}): {pagos_count} pagos de {total_atletas}")
    if hoje.day > 20 and inadimplentes > 0:
        c_f2.error(f"🚨 {inadimplentes} pendentes (Atrasados)")
    else:
        c_f2.warning(f"🕒 {inadimplentes} pendentes")

    st.divider()

    if user_role in ["admin", "finance"]:
        st.write("Marque quem está em dia (Controle Visual):")
        edited_checks = st.data_editor(df_checks, use_container_width=True, hide_index=True)
        if st.button("SALVAR LISTA"):
            save_data(edited_checks, "financeiro"); st.success("Atualizado!"); st.rerun()
    else:
        # Visitante
        st.write("Lista de Mensalistas Ativos:")
        st.dataframe(df_checks[['nome']].rename(columns={"nome": "Atleta"}), use_container_width=True, hide_index=True)

# === ABA 5: COFRE (LIVRO CAIXA REAL) ===
with tab5:
    st.header("🏦 Cofre do Madrugão")
    
    # Dashboard para todos (Transparência)
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Arrecadado (+)", f"R$ {total_entradas:,.2f}")
    k2.metric("Total Despesas (-)", f"R$ {total_saidas:,.2f}")
    k3.metric("SALDO ATUAL 🏦", f"R$ {saldo_caixa:,.2f}", delta="Em Caixa")
    
    st.divider()

    # Área de Lançamento (Só Admin/Finance)
    if user_role in ["admin", "finance"]:
        st.write("**Registrar Movimentação (Livro Caixa):**")
        c_g1, c_g2, c_g3, c_g4 = st.columns([1, 2, 1, 1])
        d_data = c_g1.date_input("Data", datetime.today())
        d_desc = c_g2.text_input("Descrição (Ex: Mensalidades 10/01)")
        d_valor = c_g3.number_input("Valor (R$)", min_value=0.0, step=10.0)
        d_tipo = c_g4.radio("Tipo:", ["Entrada ( + )", "Saída ( - )"], horizontal=True)
        
        if st.button("💾 SALVAR NO COFRE"):
            if d_desc and d_valor > 0:
                valor_final = d_valor if "Entrada" in d_tipo else -d_valor
                nova_mov = pd.DataFrame([{"Data": str(d_data), "Descricao": d_desc, "Valor": valor_final}])
                df_mov = pd.concat([df_mov, nova_mov], ignore_index=True)
                save_data(df_mov, "saidas"); st.success("Registrado!"); st.rerun()
        
        if not df_mov.empty:
            st.divider(); st.subheader("Extrato Detalhado")
            df_show = df_mov.sort_values("Data", ascending=False).copy()
            def color_negative_red(val):
                color = 'red' if val < 0 else 'green'
                return f'color: {color}'
            st.dataframe(df_show.style.map(color_negative_red, subset=['Valor']).format({"Valor": "R$ {:.2f}"}), use_container_width=True, hide_index=True)
            
            if user_role == "admin":
                with st.expander("🗑️ Área de Correção"):
                    idx_del = st.selectbox("Apagar item:", df_mov['Descricao'].unique())
                    if st.button("Apagar Selecionado"):
                            df_mov = df_mov[df_mov['Descricao'] != idx_del]
                            save_data(df_mov, "saidas"); st.rerun()
    else:
        st.info("ℹ️ Os detalhes das movimentações são restritos à administração. O saldo acima é o valor real disponível.")

# === ABA 6: ESTATÍSTICAS ===
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
            st.subheader("Artilharia")
            hist['gols'] = pd.to_numeric(hist['gols'], errors='coerce').fillna(0)
            g = hist[hist['gols']>0].groupby("jogador")['gols'].sum().sort_values(ascending=False).reset_index()
            
            g_site = g.copy()
            if not g_site.empty:
                max_gols = g_site['gols'].max()
                g_site['jogador'] = g_site.apply(lambda x: f"🥇 {x['jogador']}" if x['gols'] == max_gols else x['jogador'], axis=1)
            st.dataframe(g_site, use_container_width=True, hide_index=True)
            
            g_print = g.copy(); g_print.columns = ["ATLETA", "GOLS"]
            st.download_button("📸 Baixar Artilharia", gerar_imagem_bonita(g_print, "ARTILHARIA"), "artilharia.png", "image/png")

        with cb:
            st.subheader("Presença")
            j = hist[hist['tipo_registro']=='Jogo'].groupby("jogador").size().rename("Jogos")
            ju = hist[hist['tipo_registro']=='Justificado'].groupby("jogador").size().rename("Justif.")
            f = pd.concat([j,ju], axis=1).fillna(0).astype(int)
            f['Total'] = f['Jogos'] + f['Justif.']
            st.dataframe(f.sort_values('Jogos', ascending=False), use_container_width=True)

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
