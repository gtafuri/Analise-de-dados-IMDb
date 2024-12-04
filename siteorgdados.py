# #bibliotecas

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
import kagglehub
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

dados = pd.read_csv("imdb_top_1000.csv")

# #tratamento dos dados
dados['Genre'] = dados['Genre'].str.replace('\s*,\s*', ',', regex=True) #deixa os gêneros sem espaços que dificultem na hora de separar
dados['Released_Year'] = pd.to_numeric(dados['Released_Year'], errors='coerce') #transforma o ano de lançamento em float
dados['Decada'] = (dados['Released_Year'] // 10) * 10 #cria coluna decada
dados['Gross'] = dados['Gross'].str.replace(',', '', regex=True).astype(float) #troca as virgulas por espaços para facilitar na hora de dividir
dados["Gross"] = pd.to_numeric(dados['Gross'], errors = 'coerce') #transforma o faturamento em float

LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/375px-IMDB_Logo_2016.svg.png"
st.markdown(f"""
    <div style="text-align: center;">
        <img src="{LOGO}" width="375">
    </div>
""", unsafe_allow_html=True)


#Cabeçalho
st.title('Análise de dados IMDb')

#funções para o conteúdo de cada página
def pagina_inicial():
    st.title("Página Inicial")
    st.write("O objetivo do site é apresentar gráficos e análises relevantes, desenvolvidos a partir de um dataset contendo os 1000 filmes com maior nota no IMDb. A partir das análise disponibilizadas aqui, é possível entender se a duração, gênero ou período de lançamento pode interferir no lucro ou na recepção da obra pelo público e pela crítica.")
    st.markdown("[link do dataset](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows?resource=download)", unsafe_allow_html=True)


def faturamento_decadas(): 
    st.title("Relação entre faturamento e década de lançamento")
    media_faturamento = dados.groupby('Decada')['Gross'].mean().reset_index()
    
    fig = px.bar(media_faturamento, x='Decada', y='Gross', labels={'Decada': 'Década', 'Gross': 'Faturamento'},
                 title="Faturamento Médio por Década", color='Decada', color_continuous_scale='teal')
    fig.update_layout(plot_bgcolor='white')  
    st.plotly_chart(fig)

    # Análise
    st.subheader('Análise')
    st.text('Observando o gráfico, percebe-se que, de modo geral, o faturamento médio dos filmes cresceu de modo acentuado com o passar dos anos. Nota-se que na década de 1930 temos o primeiro faturamento médio significativo da nossa análise, em decorrência do surgimento do cinema sonoro. Mas esse faturamento cai drasticamente em 1940 com a segunda guerra mundial e depois cresce continuamente até a década de 90, época em que há uma redução junto às grandes crises econômicas mundiais.')



def faturamento_x_gênero():
    st.title("Relação entre faturamento e o gênero")
    
    faturamentoxgenero = dados.assign(Genre=dados['Genre'].str.split(',')).explode('Genre')
    faturamentoxgenero = faturamentoxgenero.dropna(subset = ['Gross'])
    faturamentoxgenero = faturamentoxgenero.groupby('Genre')['Gross'].apply(list).reset_index(name='Faturamento')
    
    palette = sns.color_palette("Set2", len(faturamentoxgenero))
    
    fig, ax = plt.subplots(figsize=(10, 6))  
    
    ax.boxplot(faturamentoxgenero['Faturamento'], patch_artist=True, 
               boxprops=dict(facecolor=palette[0], edgecolor='black', linewidth=1.2))
    
    ax.set_xticklabels(faturamentoxgenero['Genre'], rotation=90)
    
    ax.set_xlabel('Gênero')
    ax.set_ylabel('Faturamento')
    
    st.pyplot(fig)
    st.subheader('Análise')
    st.text('Observamos que o faturamento dos filmes Noir são muito inferiores aos das outras categorias, '
            'além de os filmes de aventura serem os mais lucrativos devido a sua popularidade com o público geral.')



def nota_imdb_metascore():
    st.title("Comparativo entre a distribuição de notas IMDb e Metascore")
    plot = pd.DataFrame()
    plot['IMDb'] = dados['IMDB_Rating'] * 10
    plot["MetaScore"] = dados["Meta_score"]
    plot = pd.melt(plot, value_vars=["IMDb", "MetaScore"], var_name="Instituicao", value_name="Nota")
    
    # Interactivity with Plotly Box Plot
    fig = px.box(plot, x="Instituicao", y="Nota", color="Instituicao", title="IMDb vs MetaScore")
    fig.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig)

    # Análise
    st.subheader('Análise')
    st.write("As notas Metascore variam mais que as notas IMDb. Nota-se que notas do IMDb são baseadas em avaliações de usuários, enquanto as notas Metascore representam um consenso dos críticos cinematográficos. Portanto, percebe-se que o espectador “comum” não possui o costume de avaliar filmes nos extremos da escala, principalmente de forma negativa, ao contrário dos críticos profissionais.")

def Metascore_x_IMDb_gênero(): 
    st.title("Comparativo entre notas Metascore x IMDb por gênero")
    datam=pd.DataFrame()
    fig, ax = plt.subplots(figsize=(10, 6))#criando a figura
    datam['IMDb']= dados['IMDB_Rating'] * 10 #deixando as notas na mesma escala
    datam['MetaScore'] = dados['Meta_score']
    datam['Genre'] = dados ['Genre']
    datam['Genre'] = datam["Genre"].str.split(',') #separa os gêneros entre vírgulas
    datam = datam.explode("Genre")
    datam = datam.reset_index()
    datam = datam.melt( id_vars = ["Genre"], value_vars=["IMDb","MetaScore"] ,value_name="Notas", var_name='Instituicao'  )
    
    fig, ax = plt.subplots(figsize=(10,6))#cria a figura
    #cria o boxplot
    sns.boxplot(data= datam, y="Genre", x="Notas", hue="Instituicao", ax = ax)
    ax.set_title("IMDb vs MetaScore por gênero")
    st.pyplot(fig)
    #analise
    st.subheader('Análise')
    st.write(" A partir da observação do gráfico podemos perceber que os filmes Noir são os que mais recebem notas altas do Metascore e os que têm as notas mais distribuídas são os dramas. Semelhante ao observado na análise de distribuição de notas IMDb e Metascore,  as notas IMDb têm uma variação muito baixa independentemente do gênero.")


def notas_metascore_x_imdb_por_decada():
    st.title("Notas IMDb e notas Metacritic por década")
    
    data = pd.DataFrame()
    data['Released_Year'] = pd.to_numeric(dados['Released_Year'], 'coerce')
    data['IMDB_Rating'] = dados['IMDB_Rating'] * 10  
    data['Meta_score'] = dados['Meta_score']
    
    decade_start = st.slider('Escolha a década de lançamento', 
                             min_value=1920, 
                             max_value=2020, 
                             step=10, 
                             value=(1920, 2020))

    data_filtered = data[(data['Released_Year'] >= decade_start[0]) & (data['Released_Year'] <= decade_start[1])]

    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.set(style="whitegrid", palette="Blues")
    
    sns.regplot(data=data_filtered, 
                x='Released_Year', 
                y='IMDB_Rating', 
                order=4, 
                scatter_kws={'alpha': 0.3, 'color': '#F5DE50'}, 
                line_kws={'color': '#F5DE50'})
    
    sns.regplot(data=data_filtered, 
                x='Released_Year', 
                y='Meta_score', 
                order=4, 
                scatter_kws={'alpha': 0.3, 'color': '#6495ED'}, 
                line_kws={'color': '#6495ED'})

    ax.set_xlim([decade_start[0], decade_start[1]])
    ax.set_xlabel('Ano')
    ax.set_ylabel('Nota')

    redLine = mpatches.Patch(color='#F5DE50', label='IMDB Rating')
    blueLine = mpatches.Patch(color='#6495ED', label='Meta Score')
    ax.legend(handles=[redLine, blueLine])
    st.pyplot(fig)

    # Analise
    st.subheader('Análise')
    st.write("Observando o gráfico, percebemos que as avaliações Metascore tendem a ser maiores que as IMDb para filmes anteriores à década de 80 "
             "e menores para os filmes após a década de 80, apresentando seu pico de notas baixas nos anos 2000.")


def notas_metascore_x_duração(): #perfeito
    st.title("Comparativo entre a duração dos filmes e suas notas Metascore")
    #grafico 
    data = pd.DataFrame()
    data['Runtime'] = dados['Runtime'].str.split(' ').str[0].astype(int)
    data['Meta_score'] = dados['Meta_score']
    fig, ax = plt.subplots(figsize=(10,6))
    sns.set(style="whitegrid")
    sns.regplot(
        data=data, 
        x='Meta_score', 
        y="Runtime", 
        order=2, 
        scatter_kws={'alpha': 0.1, 'color': '#1f77b4'},  
        line_kws={'color': '#1f77b4'},  
        ax=ax
    )
    sns.regplot(data = data, x='Meta_score', y="Runtime",order = 2,scatter_kws={'alpha':0.1}, ax = ax)
    plt.ylim(0,250)
    plt.ylabel('Duração')
    plt.xlabel('Nota MetaScore')
    st.pyplot(fig)
    #analise
    st.subheader('Análise')
    st.write("As notas são bem distribuídas entre as diversas durações de filmes, não aparentando existir alguma correlação.")

def decadas_x_duração(): 
    st.title("Duração dos filmes de acordo com as décadas")
    #grafico 
    data = pd.DataFrame()
    data['Released_Year'] = pd.to_numeric(dados['Released_Year'], 'coerce')
    bins = [1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
    labels = ['1920', '1930', '1940', '1950', '1960','1970','1980', '1990','2000', '2010']
    data['Runtime'] = dados['Runtime'].str.split(' ').str[0].astype(int)
    fig, ax = plt.subplots(figsize=(10,6))
    sns.regplot(
        data=data, 
        x='Released_Year', 
        y="Runtime", 
        order=4, 
        scatter_kws={'alpha': 0.1, 'color': '#1f77b4'},  
        line_kws={'color': '#1f77b4'},  
        ax=ax
    )
    plt.ylim(0,250)
    st.pyplot(fig)
    #analise
    st.subheader('Análise')
    st.write(" Observando a tendência percebemos que a duração dos filmes aumentou com o passar do tempo e hoje caminha para uma estabilização por volta dos 130 min.")

def atores_x_frequencia(): 
    st.title("Frequência de atores e atrizes em papéis de destaque")
    #grafico 
    #contando a frequência em cata categoria
    frequencia = dados['Star1'].value_counts().reset_index(name='frequency')
    temp1 = dados['Star2'].value_counts().reset_index(name='frequency')
    temp2 = dados['Star3'].value_counts().reset_index(name='frequency')
    frequencia = frequencia.rename(columns={"Star1": "n"})
    temp1 = temp1.rename(columns={'Star2': 'n'})
    temp2 = temp2.rename(columns={'Star3': 'n'})
    #concatenando as listas
    frequencia = pd.concat([frequencia, temp1, temp2])
    frequencia = frequencia.groupby('n',as_index=False)['frequency'].sum()
    frequencia = frequencia.sort_values(by='frequency', ascending=False)
    #criando a nuvem de palavras
    d = {}
    for n, Total in frequencia.values:
      d[n] = Total
      #configurando a aparencia
    wordcloud = WordCloud(
    background_color = 'white', # cor de fundo
    width = 1000, # largura
    height = 500, # altura
    colormap = 'Blues_r') # cor das palavras)
    wordcloud.generate_from_frequencies(frequencies = d)
    #plotando a figura no site
    plt.figure(figsize = (15, 10))
    plt.imshow(wordcloud, interpolation = 'bilinear')
    plt.axis('off')
    st.pyplot(plt)
    #analise
    st.subheader('Análise')
    st.write("Conseguimos visualizar alguns nomes muito frequentes: Tom Hanks, Leonardo Dicaprio, Robert De Niro, Clint Eastwood e Al Pacino. Além disso, podemos observar que a maioria são homens.")


#Criando o menu com selectbox
paginas = {
    "🍿 Página Inicial": pagina_inicial,
    "💲 Faturamento x Década": faturamento_decadas,
    "💰 Faturamento x Gênero": faturamento_x_gênero,
    "📉 Nota IMDb x MetaScore": nota_imdb_metascore,
    "📈 Notas IMDb x MetaScore por Gênero": Metascore_x_IMDb_gênero,
    "🗓️ Notas IMDb e MetaScore por Década": notas_metascore_x_imdb_por_decada,
    "🧮 Notas MetaScore x Duração": notas_metascore_x_duração,
    "⌛ Duração dos Filmes por Década": decadas_x_duração,
    "🎥 Atores x Frequência": atores_x_frequencia,
}

# Selectbox para navegação
escolha = st.selectbox("Selecione a Análise", list(paginas.keys()))

# Renderizando o conteúdo da página selecionada
paginas[escolha]()  # Chama a função correspondente
