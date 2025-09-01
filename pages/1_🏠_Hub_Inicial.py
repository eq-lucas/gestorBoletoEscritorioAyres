import streamlit as st
import pandas as pd
import os
import io

# --- SIDEBAR CUSTOMIZADA (MANTIDA 100% COMO VOCÊ PEDIU) ---
st.sidebar.image("imagem.png") 
st.sidebar.title("CONTABILIDADE AYRES")
st.sidebar.markdown("---")

# --- CONFIGURAÇÕES E FUNÇÕES AUXILIARES (MANTIDAS) ---
st.set_page_config(page_title="Hub Inicial", layout="wide")
DATA_DIR = "datasetssalvos"

def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_saved_files():
    files = [f for f in os.listdir(DATA_DIR) if "resultado" in f]
    return sorted(files, key=parse_filename, reverse=True)

def parse_filename(filename):
    try:
        parts = filename.split('_')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except: return (0, 0, 0)

def get_latest_file_path():
    files = get_saved_files()
    return os.path.join(DATA_DIR, files[0]) if files else None

def to_excel(df_to_download):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_download.to_excel(writer, index=False, sheet_name='Relatorio', float_format="%.2f")
    return output.getvalue()

def to_csv(df_to_download):
    return df_to_download.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

def display_filters_and_downloads(df, base_filename):
    df['pagou?'] = df['pagou?'].astype(str)
    opcao_filtro = st.radio("Mostrar:", ["Resultado Completo", "Apenas Pagantes", "Apenas Não Pagantes"], horizontal=True, key=f"radio_{base_filename}")
    
    df_filtrado = pd.DataFrame()
    nome_sufixo_arquivo = ""
    if opcao_filtro == "Apenas Pagantes":
        df_filtrado = df[df['pagou?'].str.contains('x', case=False, na=False)]; nome_sufixo_arquivo = "pagantes"
    elif opcao_filtro == "Apenas Não Pagantes":
        df_filtrado = df[~df['pagou?'].str.contains('x', case=False, na=False)]; nome_sufixo_arquivo = "nao_pagantes"
    else:
        df_filtrado = df; nome_sufixo_arquivo = "completo"
    
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

# --- PÁGINA PRINCIPAL DO HUB ---
st.title("🏠 Hub Inicial")

latest_file = get_latest_file_path()

if not latest_file:
    st.warning("Nenhum dado encontrado. Por favor, vá para a página 'Operações' para fazer o primeiro envio.")
else:
    base_filename_hub = os.path.basename(latest_file).replace('_resultado.csv', '')
    _, year, month = parse_filename(os.path.basename(latest_file))
    st.header(f"Resumo do Último Mês Salvo: {month}/{year}")

    df_latest = pd.read_csv(latest_file, sep=';', decimal=',')
    
    total_honorarios = df_latest['honorarios do mes'].sum()
    total_devendo = df_latest['devendo'].sum()
    total_recebido = df_latest[df_latest['pagou?'].astype(str).str.contains('x', case=False, na=False)]['honorarios do mes'].sum()

    # >>> ALTERAÇÃO AQUI: Voltando para os totais coloridos, dentro do container <<<
    with st.container(border=True):
        st.markdown(f"""
        <div style="display: flex; justify-content: space-around; gap: 10px; padding: 10px;">
            <div style="text-align: center;">
                <span style="font-size: 1rem; color: #0072B2; font-weight: bold;">Total Honorários do Mês</span>
                <p style="font-size: 1.75rem; font-weight: bold; margin-top: 5px;">{format_currency(total_honorarios)}</p>
            </div>
            <div style="text-align: center;">
                <span style="font-size: 1rem; color: #D55E00; font-weight: bold;">Total Devendo (Acumulado)</span>
                <p style="font-size: 1.75rem; font-weight: bold; margin-top: 5px;">{format_currency(total_devendo)}</p>
            </div>
            <div style="text-align: center;">
                <span style="font-size: 1rem; color: #009E73; font-weight: bold;">Total Recebido no Mês</span>
                <p style="font-size: 1.75rem; font-weight: bold; margin-top: 5px;">{format_currency(total_recebido)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("📋 Analisar e Baixar Detalhes")
        display_filters_and_downloads(df_latest, base_filename_hub)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("📄 Baixar Resumo dos Totais")
        summary_data = {
            "Descrição": ["Total Honorários do Mês", "Total Devendo (Acumulado)", "Total Recebido no Mês"],
            "Valor": [total_honorarios, total_devendo, total_recebido]
        }
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, hide_index=True, use_container_width=True)

        summary_dl_col1, summary_dl_col2 = st.columns(2)
        with summary_dl_col1:
            st.download_button(
                label="📥 Baixar Resumo (.xlsx)", data=to_excel(df_summary),
                file_name=f"{base_filename_hub}_resumo_totais.xlsx"
            )
        with summary_dl_col2:
            st.download_button(
                label="📥 Baixar Resumo (.csv)", data=to_csv(df_summary),
                file_name=f"{base_filename_hub}_resumo_totais.csv"
            )