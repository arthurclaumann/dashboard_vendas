# importando as bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px


# Função para a formatação de numeros
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


# escolhendo a configuração da pagina e o titulo
st.set_page_config(layout='wide')
st.title('DASHBOARD DE VENDAS :shopping_trolley:')



# fazendo a leitura de dados a partir de uma API e criando um filtro
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

# Criando filtros de regiao e de ano
st.sidebar.title('Filtros')

# Região
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

# Anos
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

# query -> requests -> json -> dataframe
query_string = {'regiao': regiao.lower(), 'ano':ano}
response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

# Filtro de vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
# Receita e quantidade de vendas estados
receita_estados = dados.groupby('Local da compra')['Preço'].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on = 'Local da compra', right_index=True).sort_values('Preço', ascending=False)

vendas_estado = dados.groupby('Local da compra')['Preço'].agg('count')
vendas_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat','lon']].merge(vendas_estado, left_on = 'Local da compra', right_index=True).sort_values('Preço', ascending = False).reset_index(drop=True)

# Receita e quantidade de vendas mensal
receita_mensal = dados.set_index('Data da Compra')['Preço'].resample("M").sum().reset_index()
receita_mensal['ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['mes'] = receita_mensal['Data da Compra'].dt.month_name()

venda_mensal = dados.set_index('Data da Compra')['Preço'].resample('M').agg('count').reset_index()
venda_mensal['ano'] = venda_mensal['Data da Compra'].dt.year
venda_mensal['mes'] = venda_mensal['Data da Compra'].dt.month_name()

# Receita e quantidade de vendas por categoria

receita_categorias = dados.groupby('Categoria do Produto')['Preço'].sum().sort_values( ascending=False)

vendas_categorias = dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending=False).reset_index()

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))


## Gráficos
# Gráficos de mapa
fig_mapa_receita = px.scatter_geo(receita_estados, lat ='lat', lon='lon', scope='south america', template='seaborn', size='Preço', hover_name = 'Local da compra', hover_data = {'lat': False, 'lon': False}, title = 'Receita por Estado')

fig_mapa_vendas = px.scatter_geo(vendas_estado, lat='lat', lon= 'lon', size= 'Preço', template = 'seaborn', scope = 'south america', hover_name='Local da compra', hover_data={'lat':False,'lon':False}, title='Quantidade de vendas (estados)'
)
# fig_mapa_vendas.update_traces(hovertemplate = "Quantidade: %{size}")

# Gráfico de linhas
fig_receita_anual = px.line(receita_mensal, 
                            x = 'mes',
                            y= 'Preço', 
                            color = 'ano', 
                            markers=True,
                            range_y = (0, receita_mensal.max()),
                            line_dash= 'ano',
                            title = 'Receita mensal'
                            )

fig_receita_anual.update_layout(yaxis_title = 'Receita', hovermode='x unified')

fig_vendas_anual = px.line(venda_mensal, x='mes', y = 'Preço', color = 'ano', markers=True, range_y = (0, venda_mensal.max()), line_dash='ano', title = 'quantidade de vendas')
fig_vendas_anual.update_layout(yaxis_title = 'Quantidade', hovermode='x unified')

# Gráfico de barras
fig_receita_estados = px.bar(receita_estados.head(),
                                            x = 'Local da compra',
                                            y = 'Preço',
                                            )
fig_receita_estados.update_layout(yaxis_title = 'Receita', hovermode='x unified')

fig_receita_categorias = px.bar(receita_categorias.head(),
       text_auto=True,
       title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita', hovermode='x unified')

fig_vendas_categorias = px.bar(vendas_categorias.head(), x = 'Categoria do Produto', y = 'Preço', title = 'Top categorias (quantidade de vendas)', text_auto = True)
fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade de vendas', hovermode='x unified')

fig_vendas_estados = px.bar(vendas_estado.head(), x = 'Local da compra', y = 'Preço', text_auto= True, title = 'Top estados (quantidade de vendas)')
fig_vendas_estados.update_layout(yaxis_title = 'Quantidade', hovermode='x unified')

## Visualização no streamlit
# construindo as métricas 
# Criando abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])
# Separando as métricas em duas colunas
with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita Total', formata_numero(dados['Preço'].sum(), 'R$'))   
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:   
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_anual, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita Total', formata_numero(dados['Preço'].sum(), 'R$'))   
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with col2:   
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_anual, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    fig_receita_vendedores = px.bar(
        vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
        x = 'sum',
        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
        text_auto = True,
        title = f'Top {qtd_vendedores} vendedores (receita total)'
    )

    fig_venda_vendedores = px.bar(
        vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
        x = 'count',
        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
        text_auto = True,
        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)'
    )
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))   
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)
        
    with col2:   
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_venda_vendedores, use_container_width=True)
  

# st.dataframe(dados)