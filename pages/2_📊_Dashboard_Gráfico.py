import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- SIDEBAR CUSTOMIZADA (MANTIDA) ---
st.sidebar.image("imagem.png") 
st.sidebar.title("CONTABILIDADE AYRES")
st.sidebar.markdown("---")

# --- CONFIGURAÇÕES E FUNÇÕES AUXILIARES ---
st.set_page_config(page_title="Dashboard Gráfico", layout="wide")
DATA_DIR = "datasetssalvos"

def get_saved_files():
    files = [f for f in os.listdir(DATA_DIR) if "resultado" in f]
    return sorted(files, key=parse_filename, reverse=True)

def parse_filename(filename):
    try:
        parts = filename.split('_')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except: return (0, 0, 0)

# --- PÁGINA DE GRÁFICOS ---
st.title("📊 Dashboard Gráfico")

files = get_saved_files()
if not files:
    st.warning("Nenhum dado encontrado para gerar gráficos. Vá para a página 'Operações' para fazer o primeiro envio.")
    st.stop()

df_historico = pd.DataFrame() # Inicializa o dataframe
# >>> SUGESTÃO APLICADA: Spinner para feedback de carregamento <<<
with st.spinner("Carregando e processando o histórico de dados..."):
    historico_data = []
    for f in reversed(files):
        _, year, month = parse_filename(f)
        df = pd.read_csv(os.path.join(DATA_DIR, f), sep=';', decimal=',')
        total_recebido = df[df['pagou?'].astype(str).str.contains('x', case=False, na=False)]['honorarios do mes'].sum()
        total_devendo = df['devendo'].sum()
        historico_data.append({
            "Mês": f"{year}-{month:02d}",
            "Recebido no Mês": total_recebido,
            "Dívida Acumulada": total_devendo
        })
    df_historico = pd.DataFrame(historico_data)

# >>> SUGESTÃO APLICADA: Organização em Container <<<
with st.container(border=True):
    st.subheader("📈 Evolução Histórica")
    st.caption("Receita mensal vs. Dívida total acumulada ao longo do tempo.")
    if not df_historico.empty:
        df_historico = df_historico.set_index("Mês")
        # >>> SUGESTÃO APLICADA: Cores personalizadas no gráfico <<<
        st.line_chart(df_historico, color=["#009E73", "#D55E00"]) # Verde para Recebido, Laranja/Vermelho para Dívida

st.markdown("<br>", unsafe_allow_html=True)

# >>> SUGESTÃO APLICADA: Organização em Container <<<
with st.container(border=True):
    st.subheader("🔍 Análise Detalhada por Mês")
    selected_file = st.selectbox("Selecione um mês para analisar:", files)
    df_selected = pd.read_csv(os.path.join(DATA_DIR, selected_file), sep=';', decimal=',')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Composição da Receita")
        total_recebido_mes = df_selected[df_selected['pagou?'].astype(str).str.contains('x', case=False, na=False)]['honorarios do mes'].sum()
        total_honorarios_mes = df_selected['honorarios do mes'].sum()
        a_receber = total_honorarios_mes - total_recebido_mes
        
        # Define as cores para o gráfico
        colors = ['#009E73', '#D55E00'] # Verde e Laranja/Vermelho

        fig_donut = go.Figure(data=[go.Pie(
            labels=['Recebido', 'A Receber'], 
            values=[total_recebido_mes, a_receber], 
            hole=.4,
            marker_colors=colors
        )])
        fig_donut.update_layout(margin=dict(l=20, r=20, t=30, b=20), legend_orientation="h")
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        st.subheader("🏆 Top 5 Devedores")
        df_devedores = df_selected[df_selected['devendo'] > 0].sort_values(by='devendo', ascending=False).head(5)
        if not df_devedores.empty:
            df_devedores = df_devedores.set_index('nome')
            st.bar_chart(df_devedores['devendo'], color="#0072B2") # Cor azul para as barras
        else:
            st.success("🎉 Nenhum devedor encontrado neste mês!")