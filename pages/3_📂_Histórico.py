import streamlit as st
import pandas as pd
import os
import io

# --- SIDEBAR CUSTOMIZADA (MANTIDA) ---
st.sidebar.image("imagem.png") 
st.sidebar.title("CONTABILIDADE AYRES")
st.sidebar.markdown("---")

# --- CONFIGURAÇÕES E FUNÇÕES AUXILIARES ---
st.set_page_config(page_title="Histórico", layout="wide")
DATA_DIR = "datasetssalvos"

def get_saved_files():
    files = [f for f in os.listdir(DATA_DIR) if "resultado" in f]
    return sorted(files, key=parse_filename, reverse=True)

def parse_filename(filename):
    try:
        parts = filename.split('_')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except: return (0, 0, 0)

def to_excel(df_to_download):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_download.to_excel(writer, index=False, sheet_name='Relatorio', float_format="%.2f")
    return output.getvalue()

def to_csv(df_to_download):
    return df_to_download.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
    
def display_filters_and_downloads(df, base_filename):
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.markdown("---")
    
    st.subheader("🔍 Analisar e Baixar Dados do Mês Selecionado")
    
    df['pagou?'] = df['pagou?'].astype(str)
    opcao_filtro = st.radio("Mostrar:", ["Resultado Completo", "Apenas Pagantes", "Apenas Não Pagantes"], horizontal=True, key=f"radio_{base_filename}")
    
    df_filtrado = pd.DataFrame()
    nome_sufixo_arquivo = ""
    if opcao_filtro == "Apenas Pagantes":
        df_filtrado = df[df['pagou?'].str.contains('x', case=False, na=False)]
        nome_sufixo_arquivo = "pagantes"
    elif opcao_filtro == "Apenas Não Pagantes":
        df_filtrado = df[~df['pagou?'].str.contains('x', case=False, na=False)]
        nome_sufixo_arquivo = "nao_pagantes"
    else:
        df_filtrado = df
        nome_sufixo_arquivo = "completo"
    
    st.dataframe(df_filtrado, hide_index=True, use_container_width=True)

    if not df_filtrado.empty:
        dl_btn_col1, dl_btn_col2 = st.columns(2)
        dl_btn_col1.download_button(
            label=f"📥 Baixar '{opcao_filtro}' (.xlsx)", data=to_excel(df_filtrado),
            file_name=f"{base_filename}_{nome_sufixo_arquivo}.xlsx"
        )
        dl_btn_col2.download_button(
            label=f"📥 Baixar '{opcao_filtro}' (.csv)", data=to_csv(df_filtrado),
            file_name=f"{base_filename}_{nome_sufixo_arquivo}.csv"
        )

# --- PÁGINA DE HISTÓRICO ---
st.title("📂 Histórico de Resultados")
st.caption("Selecione um mês salvo para visualizar os detalhes, filtrar os dados e baixar relatórios.")

files = get_saved_files()

with st.container(border=True):
    if not files:
        st.warning("Nenhum arquivo no histórico.")
    else:
        selected_file = st.selectbox("Selecione um mês para visualizar em detalhes:", files)
        
        base_filename_hist = selected_file.replace("_resultado.csv", "")
        
        with st.spinner("Carregando dados do mês selecionado..."):
            df_hist = pd.read_csv(os.path.join(DATA_DIR, selected_file), sep=';', decimal=',')
        
        display_filters_and_downloads(df_hist, base_filename_hist)

        # >>> SEÇÃO DE TOTAIS ADICIONADA AQUI <<<
        st.markdown("---")
        st.subheader("📄 Resumo dos Totais do Mês Selecionado")

        # Cálculos dos totais para o dataframe histórico selecionado
        total_honorarios = df_hist['honorarios do mes'].sum()
        total_devendo = df_hist['devendo'].sum()
        total_recebido = df_hist[df_hist['pagou?'].astype(str).str.contains('x', case=False, na=False)]['honorarios do mes'].sum()
        
        # Criação da tabela de resumo
        summary_data = {
            "Descrição": ["Total Honorários do Mês", "Total Devendo (Acumulado)", "Total Recebido no Mês"],
            "Valor": [total_honorarios, total_devendo, total_recebido]
        }
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, hide_index=True, use_container_width=True)

        # Botões de download para o resumo
        summary_dl_col1, summary_dl_col2 = st.columns(2)
        with summary_dl_col1:
            st.download_button(
                label="📥 Baixar Resumo (.xlsx)", data=to_excel(df_summary),
                file_name=f"{base_filename_hist}_resumo_totais.xlsx"
            )
        with summary_dl_col2:
            st.download_button(
                label="📥 Baixar Resumo (.csv)", data=to_csv(df_summary),
                file_name=f"{base_filename_hist}_resumo_totais.csv"
            )
        # >>> FIM DA NOVA SEÇÃO <<<