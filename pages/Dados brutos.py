import streamlit as st
import requests
import pandas as pd
import time

# Função para manter o arquivo no cache
@st.cache_data

## função para converter o dataframe em um arquivo CSV
def converte_csv(df):
    return df.to_csv(index = False, encoding = 'utf-8').encode('utf-8')

def mensage_success():
    success = st.success('Download successfully!', icon = '✅')
    time.sleep(5)
    success.empty()
st.title('Dados Brutos')


url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criando filtros
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Crianndo filtros barra lateral
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Categoria do produto'):
    category = st.multiselect('Selecione a categoria dos produtos', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    price = st.slider('Selecione o preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete do produto'):
    frete = st.slider('Selecione o preço do frete', dados['Frete'].min(), dados['Frete'].max(), (dados['Frete'].min(), dados['Frete'].max()))

with st.sidebar.expander('Data da compra'):
    date = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'):
    local = st.multiselect('Local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avialiação', dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max(), (dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max()))

with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Parcelas', dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max(), (dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max()))


query = ''' 
Produto in @produtos and \
`Categoria do Produto` in @category and \
@price[0] <= Preço <= @price[1] and \
@date[0] <= `Data da Compra` <= @date[1] and \
@frete[0] <= Frete <= @frete[1] and \
`Vendedor` in @vendedor and \
`Local da compra` in @local and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''


dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    file_name = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    file_name += '.csv'

with coluna2:
    st.download_button('Download table in csv', data = converte_csv(dados_filtrados), file_name = file_name, mime = 'text/csv', on_click = mensage_success)
