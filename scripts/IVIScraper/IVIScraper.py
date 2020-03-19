#%%
# Importa as bibliotecas necessárias
import wget
import pandas as pd
import json
import datetime
import os
from pandas import json_normalize
import numpy as np
import matplotlib.pyplot as plt


#%%
PASTA_TEMPORARIOS = '../../dados/temporarios/'
PASTA_AUXILIARES = '../../dados/auxiliares/'
PASTA_SAIDA = '../../dados/'


#%%
# Define os dados para download
url = 'http://plataforma.saude.gov.br/novocoronavirus/resources/scripts/database.js'
arquivo = os.path.join(PASTA_TEMPORARIOS,'database.js')


#%%
# Baixa o arquivo JS
wget.download(url, arquivo)


#%%
# Converte o arquivo JavaScript para JSON
base_js = open(arquivo, "rt")
base_json = open(
    os.path.join(PASTA_TEMPORARIOS,"database.json"),
    "wt"
)

for line in base_js:
	base_json.write(line.replace('var database=', ''))

base_js.close()
base_json.close()


#%%
# Exporta o dataframe
df = json.load(open(os.path.join(PASTA_TEMPORARIOS,"database.json")))
df = json_normalize(data=df['brazil'], record_path='values',meta=['date','time'])


#%%
# Carrega a tabela com IDs e estados
indice = pd.read_csv(os.path.join(
    PASTA_AUXILIARES,
    'indice.csv'
))


#%%
# Transforma as IDs em string
df.uid = df.uid.astype(str)
indice.uid = indice.uid.astype(str)


#%%
# Insere as UFs nos dados
df = pd.merge(df, indice, on='uid', how='left')


#%%
# Transforma números em inteiros
dados_numericos = ['suspects', 'refuses', 'confirmado', 'deads','cases', 'deaths']

for coluna in dados_numericos:
    df[coluna] = df[coluna].fillna(0)
    df[coluna] = df[coluna].astype(int)

    

#%%
# Extraindo informacoes por estado (UF)
estado_look = 'SP'
df_uf = df[df.uf == estado_look]


#%%
# Extraindo informaçoes do DataFrame
dias = df_uf['date'].values
dias = [d[0:5] for d in dias]
suspeitos = df_uf['suspects'].values
descartados = df_uf['refuses'].values
confirmados = df_uf['cases'].values
mortes = df_uf['deaths'].values


#%%
# Plotando um grafico de Barras empilhadas

fig, ax = plt.subplots()

width = 0.25       # the width of the bars: can also be len(x) sequence
ax.bar(dias, suspeitos, width, label='Suspeitos')
ax.bar(dias, descartados, width, label='Descartados', bottom=suspeitos)
ax.bar(dias, confirmados, width, label='Confirmados', bottom=descartados)
ax.bar(dias, mortes, width, label='Obitos', bottom=confirmados)

ax.set_ylabel('Notificados')
ax.set_title('Notificações COVID-19: {}'.format(estado_look))
ax.legend()

plt.show()


#%%
# Plotando um gráfico simples

fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()

ax.plot(dias, suspeitos, label='Suspeitos')
ax.plot(dias, descartados, label='Descartados')
ax.plot(dias, confirmados, label='Confirmados')
ax.plot(dias, mortes, label='Óbitos')

ax.set(xlabel='Dias', ylabel='Notificações', title='Notificações COVID-19 ({})'.format(estado_look))

ax.legend(loc='left', shadow=True)

plt.show()
# fig.savefig("COVID-19 - {}".format(estado_look))

  
#%%
# Exporta a base em CSV
dados = os.path.join(PASTA_SAIDA, 'corona_brasil' + '.csv')
df.to_csv(dados, index = False)


#%%


