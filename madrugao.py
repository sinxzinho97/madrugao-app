# --- LOGIN (ATUALIZADO COM MODERADOR) ---
SENHA_ADMIN = st.secrets.get("admin_password", "1234")
SENHA_MODERADOR = st.secrets.get("moderator_password", "bola") 
SENHA_FINANCEIRO = st.secrets.get("finance_password", "money")

# --- MODIFICAÇÃO AQUI: USO DE FORMULÁRIO PARA O BOTÃO ---
with st.sidebar.form(key="login_form"):
    st.markdown("### 🔐 Acesso Restrito")
    # O campo de senha fica dentro do form
    senha_digitada = st.text_input("Senha de Acesso", type="password", placeholder="Digite a credencial")
    # O botão de submit serve como o botão "Entrar"
    btn_entrar = st.form_submit_button("ENTRAR 🔓", type="primary", use_container_width=True)

# Lógica de verificação (O Streamlit mantém o valor de senha_digitada após o submit)
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
    if senha_digitada: # Só avisa erro se o usuário tentou digitar algo
        st.sidebar.error("❌ Senha Incorreta")
    else:
        st.sidebar.info("👀 MODO VISITANTE")

df_elenco = carregar_elenco()
