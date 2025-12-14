import streamlit as st
import pandas as pd
import os

ARQUIVO_DADOS = 'meus_gastos_casa.csv'
MORADORES = ["Eduardo", "Patricia", "Jefferson"] 

st.set_page_config(page_title="Controle Doméstico", page_icon="🏠", layout="centered")

def carregar_dados():
    """Lê o arquivo de dados. Se não existir ou estiver vazio, cria um DataFrame vazio."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            # Tenta ler. Se o arquivo existir mas estiver vazio, o Pandas gera o erro.
            return pd.read_csv(ARQUIVO_DADOS)
        except pd.errors.EmptyDataError:
            # Se der erro de "No columns to parse", retorna um DataFrame vazio.
            return pd.DataFrame(columns=["ID", "Data", "Pagador", "Descricao", "Valor"])
    else:
        # Se o arquivo nem existir, retorna um DataFrame vazio
        return pd.DataFrame(columns=["ID", "Data", "Pagador", "Descricao", "Valor"])

def salvar_dados(df):
    """Salva as alterações no arquivo CSV."""
    df.to_csv(ARQUIVO_DADOS, index=False)

# --- INTERFACE DO USUÁRIO E LÓGICA ---
st.title("🏠 Controle de Despesas da Casa")
st.caption(f"App privado compartilhado para {len(MORADORES)} pessoas.")

# 1. ÁREA DE LANÇAMENTO
st.container(border=True).markdown("### ➕ Lançar Novo Gasto")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    quem = st.selectbox("Quem pagou?", MORADORES)
with col2:
    desc = st.text_input("Descrição (Ex: Aluguel, Supermercado)")
with col3:
    val = st.number_input("Valor (R$)", min_value=0.00, format="%.2f")

if st.button("💾 Salvar Lançamento", type="primary"):
    if desc and val > 0:
        df = carregar_dados()
        # Cria um ID único para rastreamento
        novo_id = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        nova_linha = pd.DataFrame({
            "ID": [novo_id],
            "Data": [pd.Timestamp.now().strftime("%d/%m/%Y")],
            "Pagador": [quem],
            "Descricao": [desc],
            "Valor": [val]
        })
        df = pd.concat([df, nova_linha], ignore_index=True)
        salvar_dados(df)
        st.success("Lançamento salvo com sucesso!")
        st.rerun() # Recarrega para mostrar na tabela
    else:
        st.warning("Preencha a descrição e o valor.")

# 2. VISUALIZAÇÃO DOS DADOS
st.divider()
st.markdown("### 📝 Histórico de Lançamentos")
df = carregar_dados()

if not df.empty:
    # Mostra a tabela de forma limpa, sem a coluna ID
    st.dataframe(
        df[["Data", "Pagador", "Descricao", "Valor"]], 
        use_container_width=True,
        hide_index=True
    )

    # 3. RESULTADO FINANCEIRO (Cálculo do Saldo Líquido)
    st.divider()
    st.markdown("### 💰 Fechamento do Mês (Divisão por 3)")
    
    total = df["Valor"].sum()
    media = total / len(MORADORES)
    
    col_a, col_b = st.columns(2)
    col_a.metric("Total da Casa", f"R$ {total:,.2f}")
    col_b.metric("Valor Justo por Pessoa", f"R$ {media:,.2f}")
    
    st.subheader("Quem Deve a Quem?")
    
    pagos = df.groupby("Pagador")["Valor"].sum()
    
    for pessoa in MORADORES:
        pago_pela_pessoa = pagos.get(pessoa, 0.0)
        saldo = pago_pela_pessoa - media
        
        st.write(f"**👤 {pessoa}**")
        st.write(f"Pagou: R$ {pago_pela_pessoa:,.2f}")
        
        if saldo > 0.01:
            st.success(f"**RECEBE:** R$ {saldo:,.2f} (Pagou a mais)")
        elif saldo < -0.01:
            st.error(f"**PAGA:** R$ {abs(saldo):,.2f} (Precisa inteirar)")
        else:
            st.info("✅ Está ZERADO")
        st.markdown("---")
    
    # Botão para Zerar/Limpar o mês
    if st.button("🗑️ Zerar Todos os Dados (Fim do Mês)"):
        os.remove(ARQUIVO_DADOS)
        st.success("Dados apagados. O mês recomeça agora!")
        st.rerun()

else:
    st.info("Nenhum dado lançado. Use o formulário acima para começar a registrar as despesas.")