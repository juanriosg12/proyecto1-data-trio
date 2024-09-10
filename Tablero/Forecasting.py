import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import statsmodels.api as sm

# Cargar los datos
data1 = pd.read_csv('data/SeoulBikeData_limpio.csv')
data1['Date'] = pd.to_datetime(data1['Date'])
data1.set_index('Date', inplace=True)

# Entrenar el modelo ARIMA
model = sm.tsa.ARIMA(data1['Rented Bike Count'], order=(5,1,0))
model_fit = model.fit()

# Pronosticar los próximos 50 períodos
forecast = model_fit.get_forecast(steps=50)
forecast_index = pd.date_range(start=data1.index[-1], periods=51, freq='D')[1:]

# Obtener predicciones y errores estándar
forecast_mean = forecast.predicted_mean
forecast_ci = forecast.conf_int()

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación Dash
app.layout = html.Div([
    html.H1("Pronóstico de la Demanda de Bicicletas con ARIMA"),
    
    # Gráfico de pronóstico
    dcc.Graph(id='forecast-graph')
])

# Callback para generar el gráfico
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
        title='Pronóstico de Demanda de Bicicletas con ARIMA',
        xaxis=dict(title='Fecha'),
        yaxis=dict(title='Demanda'),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        hovermode='x'
    )
    
    return {
        'data': [trace_actual, trace_forecast, trace_ci],
        'layout': layout
    }

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True)
