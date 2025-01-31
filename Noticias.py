import streamlit as st 
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import pandas as pd
# import os
from geopy.geocoders import Nominatim
from time import time
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
import plotly.express as px

#Agregar la url de la pagina
html = urlopen('https://www.elsiglodetorreon.com.mx/seccion/policiaca/')
bs = BeautifulSoup(html.read(), 'html.parser')

noticias = []
tiempo = []

#Obtencioon de los encabezados de cada noticia
for i in bs.find_all('h3',attrs={'class':'my-0'}):
    news = i.text
    noticias.append(news)

#Obtencion del tiempo de cada noticia
for i in bs.find_all('div',{'class':'col-3'}):
    tim = i
    for j in tim.find_all('time'):
        tim = j.attrs["datetime"][:10]
        # tim_2 = j.text
        tiempo.append(tim)
        
        
# Tabla de tiempo y noticia
df = pd.DataFrame({'Tiempo':tiempo, 'Noticias':noticias}) 

#Ciudad donde ocurre la noticia

Ciudad = []
#Consultamos de la columna Noticias la ciudad y la añadimos a la  columna ciudad
for city in df['Noticias']:
    if 'Gómez' in city:
       Ciudad.append('Gómez Palacio, Durango')
    elif 'Lerdo' in city:
       Ciudad.append('Lerdo, Durango')
    elif 'Torreón' in city:
       Ciudad.append('Torreón, Coahuila')
    else:
       Ciudad.append('Saltillo, Coahuila')

#Tabla de la ciudad
Ciudad = pd.DataFrame(Ciudad,columns=['Ciudad'])

#join entre la tabla de tiempo y la ciudad
df_2 = df.join(Ciudad, how='outer')

#georrefenciacion de la ciudad donde ocurre la noticia
geolocator = Nominatim(user_agent='Bruno')

##**Delay para cada busqueda**"""

start = time()

geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

#Creamos otro campo para guardar las coordenadas
df_2['Location'] = df_2['Ciudad'].apply(geocode)
df_2['Coordenadas'] = df_2['Location'].apply(lambda x: (x.latitude, x.longitude))

end = time()
elapsed = end - start

Noticias = df_2[['Tiempo','Noticias','Ciudad','Coordenadas']]

Longitud = []
Latitud = []
for i in Noticias['Coordenadas']:
        Longitud.append(i[1])
        Latitud.append(i[0])

Noticias_2 = Noticias[['Tiempo','Noticias','Ciudad']]

Noticias_2 = pd.concat([Noticias_2, pd.DataFrame(Latitud,columns=['Latitud']),
                        pd.DataFrame(Longitud,columns=['Longitud'])], axis=1)

#Visualizacion del mapa interactivo donde ocurre la notica
fig = px.scatter_mapbox(Noticias_2, lat= 'Latitud', lon= 'Longitud',
                        animation_frame="Tiempo", hover_name="Noticias",
                        color_discrete_map = {"Gómez Palacio, Durango": "blue", "Torreón, Coahuila": "brown",
                                                    "Lerdo, Durango": "red", "Saltillo, Coahuila" :"green"},
                        color= 'Ciudad', size_max=15, zoom=6, height=600,width = 1000,
                        center = dict(lat=25.5, lon = -102),
                        mapbox_style="carto-positron")
# fig.show()
# fig.savefig("image", dpi = 300)

st.plotly_chart(fig)