from pathlib import Path
import pandas as pd
import requests, json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly, time, datetime
import numpy as np

## DEFINICIONES GENERALES

token = '92170321-528f-f1dd-5d59-f8613e072746'
banxico_token = '7deb6f657b170b10ea009e84f6daf7346360a10fcbe2beaa53130542c3ad6283'
covid = pd.read_csv('http://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip',
                    encoding='latin-1')
estados = pd.read_csv('clave_estados.csv')
estados = estados[estados.columns[1:]]
geojson = json.loads(Path('estados_geojson.json').read_text())
desocupacion = pd.read_csv('desocupacion.csv')
desocupacion = desocupacion.rename(columns={desocupacion.columns[0]:'fecha'})
desocupacion.index = pd.to_datetime(desocupacion.fecha,format='%Y-%m-%d')
desocupacion = desocupacion.drop(['fecha'],axis=1)

## METODOS GENERALES

def obtener_json(indicador,banco):
    global token
    liga_base = 'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/'
    indicador = indicador + '/'
    idioma = 'es/'
    banco = banco + '/2.0/'
    final_liga = str(token) + '?type=json'
    liga_api = liga_base + indicador + idioma + '0700/false/' + banco + final_liga
    req = requests.get(liga_api,verify=False)
    while True:
        try:
            data = json.loads(req.text)
            break
        except: 
            time.sleep(10)
            continue
    return data

def indicador_a_df(indicador,banco):
    data = obtener_json(indicador,banco)
    obs_totales = len(data['Series'][0]['OBSERVATIONS'])
    dic = {'fechas':[data['Series'][0]['OBSERVATIONS'][i]['TIME_PERIOD'] for i in range(obs_totales)],
            indicador:[float(data['Series'][0]['OBSERVATIONS'][i]['OBS_VALUE']) for i in range(obs_totales)]}
    df = pd.DataFrame.from_dict(dic)
    return df

def indicadores_a_df(indicadores,banco):
    lista_df = []
    for i in range(len(indicadores)):
        indicador = indicadores[i]
        df = indicador_a_df(indicador, banco)
        if i > 0: df = df.drop(['fechas'],axis=1)
        lista_df.append(df)
   
    df = pd.concat(lista_df,axis=1)
    return df    

def banxico_a_df(indicador):
    global banxico_token       
    liga_banxico = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'
    req = requests.get(liga_banxico+indicador+'/datos',params={'token':banxico_token})
    data = json.loads(req.text)
    n = len(data['bmx']['series'][0]['datos'])
    dict_df = dict(fechas = [data['bmx']['series'][0]['datos'][i]['fecha'] for i in range(n)],
                    vals = [data['bmx']['series'][0]['datos'][i]['dato'] for i in range(n)])
    df = pd.DataFrame.from_dict(dict_df)
    df.index = pd.to_datetime(df.fechas,format='%d/%m/%Y')
    df = df.drop(['fechas'],axis=1)
    df.columns = [indicador]
    return df

#### GRAFICAS ####

## PRODUCCION

def graficar_pib():
    indicadores = ['493911','493925','493932','493967']
    df = indicadores_a_df(indicadores,'BIE')
    df.columns = ['fechas','Total','Primario','Secundario','Terciario']
    df.index = pd.date_range(df.fechas.iloc[0],df.fechas.iloc[-1],periods=len(df.fechas))
    df = df.sort_index()
    vars = df[df.columns[1:]].pct_change()*100
    
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    fig = make_subplots(rows=1,cols=2,shared_xaxes=True)
    for i in range(1,len(df.columns)):
        leg_group = 'group{}'.format(i)
        col = df.columns[i]
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col,legendgroup=leg_group,
                                line=dict(color=colors[i-1])),row=1,col=1)
    for i in range(len(vars.columns)):
        leg_group = 'group{}'.format(i+1)
        col = vars.columns[i]
        fig.add_trace(go.Scatter(x=vars.index,y=vars[col],legendgroup=leg_group,
                                line=dict(color=colors[i]),showlegend=False,
                                opacity=0.7),row=1,col=2)

    fig.update_layout(template='simple_white',
                        hovermode='x', height=600,width=1200,
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=20,
                                        label="20 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=20,
                                        label="20 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"
                        ))
    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True)
    fig.update_yaxes(title_text='PIB trimestral',row=1,col=1)
    fig.update_yaxes(zeroline=True,title_text='Variación (%)',row=1,col=2)
    fig.write_html('../templates/grafica_pib.html')

## INFLACION

def graficar_inflacion():
    indicadores = ['628229','628230','628233','628231','628232','628234','628235']
    df = indicadores_a_df(indicadores,'BIE')
    df.columns = ['fechas','Índice general','Subyacente','No subyacente',
                    'Mercancias','Servicios','Agropecuarios',
                    'Energéticos y tarifas autorizadas por el gobierno']
    df.fechas = df.fechas.str.replace(r'(\d{4}/\d{2})/02',r'\1/15')
    df.index = pd.to_datetime(df.fechas,format='%Y/%m/%d')
    df = df.drop(['fechas'],axis=1)
    df = df[::-1].loc['2010':]
    fig = make_subplots(rows=1,cols=2,shared_xaxes=True,shared_yaxes=True)
    for col in df.columns[:3]:
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col,legendgroup=col,
                                opacity=0.6),row=1,col=1)
    for col in df.columns[3:]:
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col,
                                opacity=0.6),row=1,col=2)

    fig.update_layout(template='simple_white',
                        hovermode='x',height=600,width=1200,
                        legend=dict(orientation="h",yanchor='bottom'),
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=3,
                                        label="3 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=3,
                                        label="3 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"
                        ))
    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True,zeroline = True)
    fig.update_yaxes(title_text='Variación (%)',row=1,col=1)
    fig.write_html('../templates/grafica_inflacion.html')

## TASAS DE INTERES

def graficar_tasas_interes():
    indicadores = ['SF61745','SF43783','SF43773','SF44073','SF43936']
    nombres = ['Tasa objetivio','TIIE a 28 días','Tasa de fondeo bancario','Mexibor a 3 meses','Cetes a 28 días']
    fig = px.line()
    for i in range(len(indicadores)):
        id = indicadores[i]
        df = banxico_a_df(id)
        df = df.loc['2005':]
        fig.add_scatter(x=df.index,y=df[id],mode='lines',name=nombres[i],opacity=0.7)
    fig.update_layout(template='simple_white',
                        hovermode='x',height=600,width=1200,
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            )))
    fig.update_xaxes(showspikes = True,title_text='Tasas')
    fig.update_yaxes(showspikes = True)
    fig.write_html('../templates/grafica_tasas_interes.html')

## TIPO DE CAMBIO

def graficar_tipo_cambio():
    indicadores = ['SF46405','SF46410','SF46406','SF46407','SF290383','SF46411']
    nombres = ['Dólar EUA','Euro','Yen japonés','Libra esterlina','Yuan chino',
                'Derecho Especial de Giro']
    fig = make_subplots(rows=1,cols=2,shared_xaxes=True)
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    for i in range(len(indicadores)):
        id = indicadores[i]
        df = banxico_a_df(id)
        df = df[df[id]!='N/E'].astype(float)
        df = df.loc['2005':]
        df['variacion'] = df.pct_change()
        fig.add_trace(go.Scatter(x=df.index,y=df[id],name=nombres[i],
                                legendgroup=nombres[i],line=dict(color=colors[i])),
                    row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df.variacion,name=nombres[i],
                                legendgroup=nombres[i],line=dict(color=colors[i]),
                                showlegend=False,opacity=0.5),
                    row=1,col=2)

    fig.update_layout(template='simple_white',
                        hovermode='x',height=600,width=1200,
                        legend=dict(orientation="h",yanchor='bottom'),
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all")
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"
                        ))

    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True)
    fig.update_yaxes(title_text='Tipo de cambio',row=1,col=1)
    fig.update_yaxes(title_text='Variación (%)',row=1,col=2)
    fig.write_html('../templates/grafica_tipo_cambio.html')

## COVID

def limpiar_casos_nacionales(df):
    df = df[['FECHA_INGRESO','RESULTADO']]
    df['casos_diarios'] = df.groupby(df.FECHA_INGRESO).transform('sum')
    df = df.drop_duplicates()
    df = df.sort_values(['FECHA_INGRESO'])
    df['casos_acumulados'] = df.casos_diarios.cumsum() 
    df['media_diarios'] = df.casos_diarios.rolling(window=7).mean()
    df = df.drop(['RESULTADO'],axis=1)
    df.index = pd.to_datetime(df.FECHA_INGRESO,format='%Y-%m-%d')
    df = df.drop(['FECHA_INGRESO'],axis=1)
    return df
def graficar_covid_total():
    global covid
    defunciones_mex = limpiar_casos_nacionales(covid[(covid.RESULTADO==1)&(covid.FECHA_DEF!='9999-99-99')])
    casos_mex = limpiar_casos_nacionales(covid[covid.RESULTADO==1])
    defunciones_mex = defunciones_mex.loc['2020-03':]
    casos_mex = casos_mex.loc['2020-03':]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=casos_mex.index,y=casos_mex.casos_diarios,name='Casos diarios confirmados'))
    fig.add_trace(go.Bar(x=defunciones_mex.index,y=defunciones_mex.casos_diarios,name='Defunciones diarias confirmadas'))
    fig.update_layout(template='simple_white',
                        hovermode='x',
                        legend=dict(orientation="h",yanchor='bottom'),
                        height=500,width=1000,
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 mes",
                                        step="month",
                                        stepmode="backward"),
                                    dict(count=3,
                                        label="3 meses",
                                        step="month",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 meses",
                                        step="month",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 mes",
                                        step="month",
                                        stepmode="backward"),
                                    dict(count=3,
                                        label="3 meses",
                                        step="month",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 meses",
                                        step="month",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"))

    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True)
    fig.write_html('../templates/grafica_covid_total.html')

def limpiar_casos_estados(df,estados):
    df = df[['ENTIDAD_RES','FECHA_INGRESO','RESULTADO']]
    df = pd.merge(df,estados,left_on='ENTIDAD_RES',right_on='cve',how='left')
    df = df.drop(['ENTIDAD_RES'],axis=1)
    casos_edos = df[df.RESULTADO == 1]
    casos_edos['casos_diarios'] = casos_edos.groupby(['NAME','FECHA_INGRESO'])['RESULTADO'].transform('sum')
    casos_edos = casos_edos[['FECHA_INGRESO','NAME','casos_diarios']]
    casos_edos = casos_edos.drop_duplicates()
    casos_edos = casos_edos.sort_values(['FECHA_INGRESO'])
    casos_edos['variacion_diaria'] = casos_edos.groupby('NAME')['casos_diarios'].pct_change()
    casos_edos['variacion_media'] = casos_edos.groupby('NAME')['variacion_diaria'].rolling(7).mean().reset_index(0, drop=True)
    casos_edos['casos_media'] = casos_edos.groupby('NAME')['casos_diarios'].rolling(7).mean().reset_index(0, drop=True)
    return casos_edos
def obtener_pivotes(df):
    media_pivote = df.pivot('NAME','FECHA_INGRESO','casos_media')
    media_pivote = media_pivote.fillna(0)
    data_pivote = media_pivote.copy(deep=True)
    data_pivote['fecha_max'] = data_pivote.idxmax(axis=1)
    data_pivote = data_pivote.sort_values(['fecha_max'],ascending=False)
    data_pivote = data_pivote.drop(['fecha_max'],axis=1)
    data_pivote = data_pivote.sub(data_pivote.mean(axis=1),axis=0)
    data_pivote = data_pivote.div(data_pivote.std(axis=1),axis=0)
    media_pivote = media_pivote.loc[data_pivote.index]
    diarios_pivote = df.pivot('NAME','FECHA_INGRESO','casos_diarios')
    diarios_pivote = diarios_pivote.fillna(0)
    diarios_pivote = diarios_pivote.loc[data_pivote.index]
    return data_pivote,media_pivote,diarios_pivote
def graficar_heatmap_covid():
    global covid,estados
    casos_edos = limpiar_casos_estados(covid,estados)
    data_pivote, media_pivote, diarios_pivote = obtener_pivotes(casos_edos)
    fig = go.Figure(go.Heatmap(z=data_pivote.values,
                            x=data_pivote.columns,
                            y=data_pivote.index,
                            customdata=np.dstack((media_pivote.values,diarios_pivote.values)),
                            hovertemplate='<b>%{y}</b> <br>%{x}</br> <br>Promedio movil: %{customdata[0]:.2f}</br> <br>Casos diarios: %{customdata[1]}<extra></extra>',
                            colorscale=[[0, 'rgb(85,107,47)'],[0.416, 'rgb(152,251,152)'],[1.0, 'rgb(260,0,0)']]))
    fig.update_layout(height=1000,width=1000)
    fig.write_html('../templates/heatmap_covid.html')


def graficar_mapa_covid():
    global covid,estados,geojson
    casos_edos = limpiar_casos_estados(covid,estados)
    defunciones_edos = limpiar_casos_estados(covid[covid.FECHA_DEF!='9999-99-99'],estados)
    var_casos_pivote = casos_edos.pivot('NAME','FECHA_INGRESO','variacion_diaria')
    var_defs_pivote = defunciones_edos.pivot('NAME','FECHA_INGRESO','variacion_diaria')
    casos_pivote = casos_edos.pivot('NAME','FECHA_INGRESO','casos_diarios')
    defs_pivote = defunciones_edos.pivot('NAME','FECHA_INGRESO','casos_diarios')
    geodata = estados[:32].copy(deep=True)
    geodata['Variación promedio de casos'] = var_casos_pivote.iloc[:,-8:-1].mean(axis=1).to_list()
    geodata['Variación promedio de defunciones'] = var_defs_pivote.iloc[:,-8:-1].mean(axis=1).to_list()
    geodata['Promedio de casos'] = casos_pivote.iloc[:,-8:-1].mean(axis=1).to_list()
    geodata['Promedio de defunciones'] = defs_pivote.iloc[:,-8:-1].mean(axis=1).to_list()
    data = [go.Choroplethmapbox(locations = geodata['CODE'],
                                z = geodata['Variación promedio de casos'],
                                colorscale = 'reds',
                                geojson = geojson,
                                featureidkey="properties.CODE",visible=True,
                                customdata=geodata['NAME'],
                                colorbar = dict(title="Variación promedio<br>en la última semana</br>",
                                                tickformat='%'),
                                hovertemplate='<b>%{customdata}</b><br>Variación promedio: %{z:>7.2%}</br><extra></extra>')]
    data.append(go.Choroplethmapbox(locations = geodata['CODE'],
                                z = geodata['Variación promedio de defunciones'],
                                colorscale = 'reds',
                                geojson = geojson,
                                featureidkey="properties.CODE",visible=False,
                                customdata=geodata['NAME'],
                                colorbar = dict(title="Variación promedio<br>en la última semana</br>"),
                                hovertemplate='<b>%{customdata}</b><br>Variación promedio: %{z:>7.2%}</br><extra></extra>'))
    data.append(go.Choroplethmapbox(locations = geodata['CODE'],
                                z = geodata['Promedio de casos'],
                                colorscale = 'reds',
                                geojson = geojson,
                                featureidkey="properties.CODE",visible=False,
                                customdata=geodata['NAME'],
                                colorbar = dict(title="Casos promedio<br>en la última semana</br>"),
                                hovertemplate='<b>%{customdata}</b><br>Casos promedio: %{z:>7.2f}</br><extra></extra>'))
    data.append(go.Choroplethmapbox(locations = geodata['CODE'],
                                z = geodata['Promedio de defunciones'],
                                colorscale = 'reds',
                                geojson = geojson,
                                featureidkey="properties.CODE",visible=False,
                                customdata=geodata['NAME'],
                                colorbar = dict(title="Defunciones promedio<br>en la última semana</br>"),
                                hovertemplate='<b>%{customdata}</b><br>Defunciones promedio: %{z:>7.2f}</br><extra></extra>'))
    layout = go.Layout(mapbox = dict(center= {'lat':23.7,'lon':-103},
                                    zoom=4,style="carto-positron"),
                        margin={"r":0,"t":0,"l":0,"b":0},height=600,width=1000)
    layout.update(
        updatemenus=[
            dict(direction="down",
                x=0,
                xanchor="left",
                y=1.1,
                yanchor="top",
                buttons=list([
                    dict(label="Casos confirmados (variación)",
                        method="update",
                        args=[{"visible": [True, False,False,False]}]),
                    dict(label="Defunciones confirmadas (variación)",
                        method="update",
                        args=[{"visible": [False,True,False,False]}]),
                    dict(label="Casos confirmados",
                        method="update",
                        args=[{"visible": [False,False,True,False]}]),
                    dict(label="Defunciones confirmadas",
                        method="update",
                        args=[{"visible": [False,False,False,True]}])
                ]),
            )
        ])
    fig=go.Figure(data,layout)
    fig.write_html('../templates/mapa_covid.html')


## DESEMPLEO

def graficar_mapa_desempleo():
    global desocupacion,estados,geojson
    geodata = estados[:32].copy(deep=True)
    geodata['Tasa de desempleo'] = desocupacion.iloc[-1].to_list()
    fig = px.choropleth_mapbox(geodata,geojson=geojson,locations='CODE',color='Tasa de desempleo',
                            featureidkey="properties.CODE",mapbox_style="carto-positron",
                            color_continuous_scale='reds',center={'lat':23.7,'lon':-103},
                            zoom=4,hover_name='NAME',
                            hover_data={'Tasa de desempleo':':>7.2f',
                                        'CODE':False})
    fig.update_layout(coloraxis_colorbar=dict(title="Tasa de desempleo"))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},height=600,width=1000)
    fig.write_html('../templates/mapa_desempleo.html')

if (__name__)=='__main__':
    graficar_pib()
    graficar_inflacion()
    graficar_tasas_interes()
    graficar_tipo_cambio()
    graficar_covid_total()
    graficar_heatmap_covid()
    graficar_mapa_covid()
    graficar_mapa_desempleo()