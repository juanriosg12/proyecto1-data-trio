import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import statsmodels.api as sm

# Leer el archivo CSV
datab = pd.read_csv("data/SeoulBikeData_limpio.csv")

# Convertir la columna 'Date' a formato de fecha
datab['Date'] = pd.to_datetime(datab['Date'])
datab['Día de la Semana'] = datab['Date'].dt.day_name()

# Entrenar el modelo ARIMA para el pronóstico
data1 = datab.copy()
data1.set_index('Date', inplace=True)

model = sm.tsa.ARIMA(data1['Rented Bike Count'], order=(5, 1, 0))
model_fit = model.fit()

# Pronosticar los próximos 50 períodos
forecast = model_fit.get_forecast(steps=50)
forecast_index = pd.date_range(start=data1.index[-1], periods=51, freq='D')[1:]

# Obtener predicciones y errores estándar
forecast_mean = forecast.predicted_mean
forecast_ci = forecast.conf_int()

# Estilos externos
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Inicializar la app Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Colores por estación
color_map = { 
    "Spring": "hotpink",  
    "Summer": "palegreen",  
    "Autumn": "darkorange",  
    "Winter": "lightskyblue" 
}

# Opciones para el dropdown del tercer gráfico
x_options = {
    'Temperature(C)': 'Temperatura (C)',
    'Humidity(%)': 'Humedad (%)',
    'Wind speed (m/s)': 'Velocidad del viento (m/s)',
    'Visibility (10m)': 'Visibilidad (10m)',
    'Solar Radiation (MJ/m2)': 'Radiación Solar (MJ/m2)'
}

season_value_map = {
    3:'Winter',
    0:'Autumn',
    2:'Summer',
    1:'Spring'
}

datab['Season Value'] = datab['Seasons'].map(season_value_map)

# Layout de la aplicación con las cuatro visualizaciones
app.layout = html.Div(children=[
    # Título del Dashboard
    html.H1(children='Demanda de Bicicletas en Seúl', style={'text-align': 'center', }),

    # Primera visualización: Histograma de demanda de bicicletas por estación
    html.Div([
        html.H2('Demanda de Bicicletas por Estación'),
        dcc.Graph(
            id='graph-rented-bikes-seasons',
            figure=px.histogram(datab, x='Seasons', y='Rented Bike Count', color='Season Value', text_auto=True,
                                color_discrete_map=color_map)  # Colores personalizados
                   .update_layout(
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       xaxis_title="Estaciones",
                       yaxis_title='Demanda de Bicicletas',
                       xaxis=dict(mirror=True, ticks='outside', gridcolor='lightgrey'),
                       yaxis=dict(mirror=True, ticks='outside', gridcolor='lightgrey'),
                       coloraxis_colorbar=dict(
                           title="Valor de la Estación",
                           tickvals=[0, 1, 2, 3],
                           ticktext=['Autumn (0)', 'Spring (1)', 'Summer (2)', 'Winter (3)']
                       )
                   )
        )
    ], style={'margin-bottom': '40px'}),
    
    # Segunda visualización: Línea de demanda por hora y fecha seleccionada
    html.Div([
        html.H2('Demanda de Bicicletas por Hora'),
        html.Div('Seleccione una fecha para visualizar la demanda de bicicletas:'),
        dcc.DatePickerSingle(
            id='date-picker-single',
            min_date_allowed=datab['Date'].min().date(),
            max_date_allowed=datab['Date'].max().date(),
            date=datab['Date'].min().date(),
            display_format='YYYY-MM-DD'
        ),
        dcc.Graph(id='graph-rented-bikes-hour')
    ], style={'margin-bottom': '40px'}),

    # Tercera visualización: Gráfico de dispersión con diferentes variables climáticas
    html.Div([
        html.H2('Demanda de Bicicletas vs. Condiciones Climáticas'),
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': label, 'value': value} for value, label in x_options.items()],
                value='Wind speed (m/s)'  # Valor por defecto
            ),
        ], style={'width': '100%', 'display': 'inline-block'}),
        
        dcc.Graph(id='indicator-graphic')
    ], style={'margin-bottom': '40px'}),
    
    # Cuarta visualización: Pronóstico de demanda con ARIMA
    html.Div([
        html.H2('Pronóstico de la Demanda de Bicicletas con ARIMA'),
        dcc.Graph(id='forecast-graph')
    ])
])

# Callback para actualizar el gráfico de demanda por hora según la fecha seleccionada
@app.callback(
    Output('graph-rented-bikes-hour', 'figure'),
    [Input('date-picker-single', 'date')]
)
def update_graph_hour(selected_date):
    if selected_date is None:
        selected_date = datab['Date'].min().date()
    
    filtered_data = datab[datab['Date'].dt.date == pd.to_datetime(selected_date).date()]
    
    fig = px.line(filtered_data, x="Hour", y="Rented Bike Count", color="Día de la Semana", markers=True)
    
    fig.update_layout(
        title=f"Bicicletas Rentadas por Hora en {selected_date}",
        xaxis_title="Hora",
        yaxis_title="Demanda de Bicicletas",
        plot_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(mirror=True, ticks='outside', gridcolor='lightgrey'),
        yaxis=dict(mirror=True, ticks='outside', gridcolor='lightgrey')
    )
    
    return fig

# Callback para actualizar el gráfico de dispersión con variables climáticas
@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value')]
)
def update_graph_climate(xaxis_column_name):
    fig = px.scatter(datab, x=xaxis_column_name, y='Rented Bike Count', hover_name=datab['Date'], color_discrete_sequence=['#ba69cf'])
    
    fig.update_layout(
        title=f'Dispersión de Demanda Bicicletas vs {x_options.get(xaxis_column_name, xaxis_column_name)}',
        xaxis_title=x_options.get(xaxis_column_name, xaxis_column_name),
        yaxis_title="Demanda de Bicicletas",
        plot_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(mirror=True, ticks='outside', gridcolor='lightgrey'),
        yaxis=dict(mirror=True, ticks='outside', gridcolor='lightgrey')
    )
    
    return fig

# Callback para generar el gráfico de pronóstico
@app.callback(
    Output('forecast-graph', 'figure'),
    [Input('forecast-graph', 'id')]
)
def update_forecast_graph(_):
    # Gráfico con Plotly
    trace_actual = go.Scatter(x=data1.index, y=data1['Rented Bike Count'], mode='lines', name='Valor Actual')
    trace_forecast = go.Scatter(x=forecast_index, y=forecast_mean, mode='lines', name='Pronóstico', line=dict(color='red'))
    trace_ci = go.Scatter(
        x=np.concatenate([forecast_index, forecast_index[::-1]]), 
        y=np.concatenate([forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1][::-1]]),
        fill='toself',
        fillcolor='rgba(255, 182, 193, 0.3)',  # Color rosa semitransparente
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    )
    
    layout = go.Layout(
        title='Pronóstico de Demanda de Bicicletas con ARIMA (50 periodos siguientes)',
        xaxis=dict(title='Fecha'),
        yaxis=dict(title='Demanda'),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        hovermode='x'
    )
    
    return {
        'data': [trace_actual, trace_forecast, trace_ci],
        'layout': layout
    }

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)
