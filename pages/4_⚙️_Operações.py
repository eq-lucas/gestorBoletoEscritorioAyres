import streamlit as st
import pandas as pd
import os
import io
import shutil
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- SIDEBAR CUSTOMIZADA (MANTIDA) ---
st.sidebar.image("imagem.png") 
st.sidebar.title("CONTABILIDADE AYRES")
st.sidebar.markdown("---")

# --- 1. CONFIGURAÇÕES E FUNÇÕES AUXILIARES ---
st.set_page_config(page_title="Operações", layout="wide")
DATA_DIR = "datasetssalvos"

def to_excel(df_to_download):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_download.to_excel(writer, index=False, sheet_name='Relatorio', float_format="%.2f")
    return output.getvalue()

def to_csv(df_to_download):
    return df_to_download.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

def normalize_value_from_string(value_str):
    s = str(value_str).strip()
    if s == '' or pd.isna(s) or s.lower() == 'nan': return 0.0
    try: return float(s.replace(',', '.'))
    except (ValueError, TypeError): return 0.0

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

def delete_files_after(base_filename):
    base_id, _, _ = parse_filename(base_filename)
    for f in os.listdir(DATA_DIR):
        file_id, _, _ = parse_filename(f)
        if file_id > base_id:
            os.remove(os.path.join(DATA_DIR, f))

# >>> NOVA FUNÇÃO PARA DELETAR TUDO <<<
def delete_all_data():
    """Apaga a pasta de datasets e a recria vazia."""
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR)

def create_next_month_template(latest_result_df):
    template_df = latest_result_df[['nome', 'honorarios do mes']].copy()
    template_df['pagou?'] = ''
    template_df['devendo'] = latest_result_df['devendo']
    return template_df

def calcular_resultado(df_cleaned):
    df_processado = df_cleaned.copy()
    if 'devendo' not in df_processado.columns:
        df_processado['devendo'] = 0.0
    df_processado['pagou?'] = df_processado['pagou?'].fillna('Na').astype(str)
    for index, row in df_processado.iterrows():
        if 'x' not in row['pagou?'].lower():
            df_processado.loc[index, 'devendo'] = row['devendo'] + row['honorarios do mes']
    return df_processado

# --- 2. DEFINIÇÃO DAS "SUB-PÁGINAS" DE OPERAÇÕES ---

def display_uploader_tabs():
    saved_files = get_saved_files()
    if saved_files:
        tab1, tab2 = st.tabs(["▶️ Iniciar Próximo Mês", "⏪ Reverter Mês"])
        with tab1:
            with st.container(border=True):
                st.header("Iniciar Próximo Mês")
                # ... (código da tab1 continua o mesmo)
                latest_file_path = get_latest_file_path()
                _, last_year, last_month = parse_filename(os.path.basename(latest_file_path))
                next_date = datetime(last_year, last_month, 1) + relativedelta(months=1)
                st.subheader(f"Preparando dados para: {next_date.month}/{next_date.year}")
                latest_df = pd.read_csv(latest_file_path, sep=';', decimal=',')
                df_template = create_next_month_template(latest_df)
                st.dataframe(df_template, hide_index=True)
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button(label="📥 Baixar Modelo (.csv)", data=to_csv(df_template), file_name=f"modelo_{next_date.year}_{next_date.month}.csv")
                with dl_col2:
                    st.download_button(label="📥 Baixar Modelo (.xlsx)", data=to_excel(df_template), file_name=f"modelo_{next_date.year}_{next_date.month}.xlsx")
                uploaded_file = st.file_uploader("Envie o boleto preenchido do mês:", type=['csv', 'xlsx'], key="uploader_proximo_mes")
                if uploaded_file:
                    if st.button("Processar Novo Mês"):
                        with st.spinner("Processando arquivo..."):
                            df_raw = pd.read_csv(uploaded_file, sep=';', dtype=str) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file, dtype=str)
                            df_cleaned = df_raw.copy()
                            for col in ['honorarios do mes', 'devendo']:
                                if col in df_cleaned.columns:
                                    df_cleaned[col] = df_cleaned[col].apply(normalize_value_from_string)
                            st.session_state.df_enviado_cleaned = df_cleaned
                            st.session_state.next_year = next_date.year
                            st.session_state.next_month = next_date.month
                            st.session_state.show_processing_view = True
                            st.rerun()
        with tab2:
            with st.container(border=True):
                st.header("Reverter Mês")
                st.caption("Ação Destrutiva")
                st.warning("AVISO: Reverter para um mês **APAGARÁ PERMANENTEMENTE** todos os meses seguintes a ele.")
                selected_file_to_revert = st.selectbox("Selecione o último mês que deseja manter:", [""] + saved_files)
                if selected_file_to_revert:
                    if st.button(f"Confirmar e reverter para '{selected_file_to_revert}'", type="primary"):
                        with st.spinner("Revertendo histórico..."):
                            delete_files_after(selected_file_to_revert)
                        st.success("Histórico revertido com sucesso!")
                        st.rerun()

                # >>> NOVA SEÇÃO PARA DELETAR TUDO <<<
                st.markdown("---")
                st.subheader("Apagar Todo o Histórico")
                with st.expander("🚨 Clique aqui para ver a opção de exclusão total 🚨"):
                    st.error("ATENÇÃO: Esta ação é irreversível e apagará todos os arquivos salvos permanentemente.")
                    if st.button("Sim, quero apagar todos os dados", type="primary"):
                        with st.spinner("Apagando todos os dados..."):
                            delete_all_data()
                        st.success("Todos os dados foram apagados com sucesso!")
                        st.rerun()

    else: # Se não houver arquivos salvos
        with st.tabs(["🚀 Primeiro Envio"])[0]:
            with st.container(border=True):
                st.header("Primeiro Envio de Dados")
                st.info("Use esta opção para carregar o primeiro arquivo no sistema.")
                # ... (código da tab3 continua o mesmo)
                uploaded_file_primeiro = st.file_uploader("Envie o arquivo inicial", type=['csv', 'xlsx'], key="uploader_primeiro")
                if uploaded_file_primeiro:
                    if st.button("Processar Primeiro Mês"):
                        with st.spinner("Processando arquivo inicial..."):
                            df_raw = pd.read_csv(uploaded_file_primeiro, sep=';', dtype=str) if uploaded_file_primeiro.name.endswith('.csv') else pd.read_excel(uploaded_file_primeiro, dtype=str)
                            df_cleaned = df_raw.copy()
                            for col in ['honorarios do mes', 'devendo']:
                                if col in df_cleaned.columns:
                                    df_cleaned[col] = df_cleaned[col].apply(normalize_value_from_string)
                            st.session_state.df_enviado_cleaned = df_cleaned
                            st.session_state.next_year = datetime.now().year
                            st.session_state.next_month = datetime.now().month
                            st.session_state.show_processing_view = True
                            st.rerun()

def display_processing_view():
    st.title("🔬 Processamento e Verificação")
    # ... (código desta função continua o mesmo)
    df_enviado_cleaned = st.session_state.get('df_enviado_cleaned')
    if df_enviado_cleaned is None:
        st.error("Erro nos dados de sessão. Por favor, tente novamente.")
        if st.button("Voltar"): st.session_state.show_processing_view = False; st.rerun()
        return
    with st.container(border=True):
        df_resultado = calcular_resultado(df_enviado_cleaned.copy())
        count = len(get_saved_files()) + 1
        year = st.session_state.get('next_year', datetime.now().year)
        month = st.session_state.get('next_month', datetime.now().month)
        nome_base = f"{count}_{year}_{month}"
        st.subheader("📊 Comparativo")
        col1, col2 = st.columns(2)
        col1.caption("Arquivo Enviado (Sua base para o cálculo)")
        col1.dataframe(df_enviado_cleaned, hide_index=True)
        col2.caption("Resultado Final")
        col2.dataframe(df_resultado, hide_index=True)
        st.info(f"O resultado será salvo como: `{nome_base}_resultado.csv`")
        if st.session_state.get('save_complete', False):
            st.success("Salvo com sucesso!")
            if st.button("Voltar às Operações"):
                del st.session_state.save_complete
                if 'df_enviado_cleaned' in st.session_state: del st.session_state.df_enviado_cleaned
                st.session_state.show_processing_view = False
                st.rerun()
        else:
            action_col1, action_col2 = st.columns(2)
            if action_col1.button("Salvar Resultado", type="primary"):
                with st.spinner("Salvando arquivos..."):
                    caminho_bruto = os.path.join(DATA_DIR, f"{nome_base}_bruto.csv")
                    caminho_resultado = os.path.join(DATA_DIR, f"{nome_base}_resultado.csv")
                    df_enviado_cleaned.to_csv(caminho_bruto, index=False, sep=';', decimal=',', float_format='%.2f')
                    df_resultado.to_csv(caminho_resultado, index=False, sep=';', decimal=',', float_format='%.2f')
                st.session_state.save_complete = True
                st.balloons()
                st.rerun()
            if action_col2.button("Desfazer e Voltar"):
                st.session_state.show_processing_view = False
                if 'df_enviado_cleaned' in st.session_state: del st.session_state.df_enviado_cleaned
                st.rerun()

# --- 3. LÓGICA PRINCIPAL DA PÁGINA ---
st.title("⚙️ Operações")

if 'show_processing_view' not in st.session_state:
    st.session_state.show_processing_view = False

if st.session_state.show_processing_view:
    display_processing_view()
else:
    display_uploader_tabs()