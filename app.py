import streamlit as st

# Em cada arquivo .py, adicione este bloco no início

# Use um link de uma imagem online ou o caminho para um arquivo local
st.sidebar.image("imagem.png") 
st.sidebar.title("CONTABILIDADE AYRES")
st.sidebar.markdown("---")
# O restante da navegação (st.page_link, etc.) virá aqui, gerado automaticamente pelo Streamlit


st.set_page_config(
    page_title="Bem-vindo",
    page_icon="👋",
    layout="centered"
)

st.title("Gestor de CONTABILIDADE AYRES")

st.markdown("---")

st.header("Uma Ferramenta Completa para Gestão de Cobranças Mensais")

st.info("""
Esta aplicação foi desenvolvida para automatizar e organizar o controle de pagamentos e dívidas mensais de seus clientes.

**Navegue pelas páginas na barra lateral para:**

- **🏠 Hub Inicial:** A sua tela principal. Tenha uma visão geral do último mês fechado, com os totais de honorários, dívidas e valores recebidos, além de poder filtrar e baixar relatórios detalhados.

- **📊 Dashboard Gráfico:** Analise a saúde financeira do seu negócio com gráficos que mostram a evolução das receitas, das dívidas acumuladas e os maiores devedores de cada mês.

- **📂 Histórico:** Consulte os detalhes de qualquer mês anterior. Visualize a tabela completa de resultados de um período específico e baixe os relatórios correspondentes.

- **⚙️ Operações:** Onde toda a ação acontece. Envie novos arquivos, prepare o modelo para o próximo mês ou reverta para um mês anterior caso precise fazer correções.
""", icon="ℹ️")

st.markdown("Para começar, vá para a página **Operações** para fazer o seu primeiro envio de dados.")