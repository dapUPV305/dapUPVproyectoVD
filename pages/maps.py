# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context
import geopandas as gpd
from st_pages import Page, show_pages, add_page_title

prov = ['ALBACETE','ALICANTE','ALMERÍA','ARABA/ÁLAVA','ASTURIAS','ÁVILA','BADAJOZ','BALEARS (ILLES)','BARCELONA','BIZKAIA','BURGOS','CÁCERES','CÁDIZ','CANTABRIA','CASTELLÓN / CASTELLÓ','CIUDAD REAL','CÓRDOBA','CORUÑA (A)','CUENCA','GIPUZKOA','GIRONA','GRANADA','GUADALAJARA','HUELVA','HUESCA','JAÉN','LEÓN','LLEIDA','LUGO',
'MADRID','MÁLAGA','MURCIA','NAVARRA','OURENSE','PALENCIA','PONTEVEDRA','RIOJA (LA)','SALAMANCA','SEGOVIA','SEVILLA','SORIA','TARRAGONA','TERUEL','TOLEDO','VALENCIA / VALÈNCIA','VALLADOLID','ZAMORA','ZARAGOZA','PALMAS (LAS)']

cod = ['02','03', '04',  '01', '33',  '05',  '06',  '07', '08',  '48',  '09',  '10',  '11',  '39',  '12', '13',  '14',  '15', '16',  '20',  '17',  '18',  '19', '21',  '22',  
'23',  '24',  '25',  '27',  '28',  '29',  '30',  '31',  '32',  '34',  '36',  '26', '37',  '40',  '41',  '42',  '43',  '44',  '45',  '46', '47',  '49',  '50', '35']
map_prov_cod = {x:y for x,y in zip(prov,cod)}

prov_geo = 'provincias.geojson'


@st.cache_data(ttl=86400) 
def load_data():
    df = pd.read_csv("stadiums.csv", sep=';', index_col=0)
    cols = ['Aforo','Lat','Lon']
    df[cols] = df[cols].replace(',','.',regex=True).astype(float)
    
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Lat, df.Lon))
    
    prov_data = df.groupby('Provincia')['Equipo'].aggregate(['count']).reset_index()
    prov_data['codigo'] = ''
    prov_data['codigo'] = prov_data['Provincia'].apply(lambda x: map_prov_cod[x])

    df['data'] = ''
    for i in range(len(df)):
        df['data'].iat[i] = str("Estadio: {} | Equipo: {} | Aforo: {}".format(df.Estadio.iat[i],df.Equipo.iat[i],df.Aforo.iat[i]))

    return df, gdf, prov_data

def display_prov_filter():    
    provincia = st.sidebar.selectbox('Provincia', prov, index=44, key='selectProv')
    return provincia

st.set_page_config(page_title="Estadios", page_icon="🇪🇸")
show_pages(
    [
        Page("streamlit_app.py", "Home", "⚽"),
        Page("pages/plots.py", "Datos por temporadas", "📊"),
        Page("pages/maps.py", "Estadios", "🇪🇸"),
    ]
)
st.title("Estadios de los equipos")

provincia = display_prov_filter()

df, gdf, prov_data = load_data()

if provincia:
    lonMap = df[df['Provincia'] == provincia].Lon.mean()
    latMap = df[df['Provincia'] == provincia].Lat.mean()    
    estadios = df[(df['Provincia'] == provincia)].reset_index(inplace=False)
    st.subheader('Estadios: {}'.format(provincia))
else:
    st.error("Por favor, seleccione al menos una provincia.")

x=len(estadios)
if x>0:
    for i in range(x):
        st.write(estadios.data)    

m = folium.Map(location=[latMap, lonMap], zoom_start=8,attr='LOL',max_bounds=True,min_zoom=5.5)
mc = MarkerCluster()
for i in range(len(df)):
    folium.CircleMarker(location=[df.Lat.iat[i],df.Lon.iat[i],],popup=df.data.iat[i],radius=10,color="#fe6f47",fill=True, fill_opacity=0.7).add_to(mc)

mc.add_to(m)
folium.Choropleth(geo_data=prov_geo,name="choropleth",data=prov_data,columns=["codigo", 'count'], key_on="properties.codigo", fill_color="Greys",fill_opacity=0.4,line_opacity=1.0,legend_name="Número de Estadios").add_to(m)

folium_static(m, width=1000, height=800)