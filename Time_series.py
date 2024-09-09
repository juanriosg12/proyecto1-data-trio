import dash
from dash import dcc  # dash core components
from dash import html  # dash html components
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from datetime import date

# Leer el archivo CSV
datab = pd.read_csv(r"C:\Users\USER\OneDrive - Universidad de los andes\Analitica comp\Proyecto\SeoulBikeData_utf8.csv")

# Convertir la columna 'Date' a formato de fecha
datab['Date'] = pd.to_datetime(datab['Date'], format='%d/%m/%Y')

# Añadir columna con el día de la semana
datab['DayOfWeek'] = datab['Date'].dt.day_name()

# Estilos externos
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Inicializar la app Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Layout de la app con DatePickerSingle
app.layout = html.Div(children=[
    html.H1(children='Cantidad de Bicicletas Rentadas por Hora y Día de la Semana'),

    dcc.DatePickerSingle(
        id='date-picker-single',
        min_date_allowed=datab['Date'].min().date(),
        max_date_allowed=datab['Date'].max().date(),
        date=datab['Date'].min().date(),
        display_format='YYYY-MM-DD'
    ),

    dcc.Graph(
        id='graph-rented-bikes'
    )
])

# Callback para actualizar el gráfico basado en la fecha seleccionada
@app.callback(
    Output('graph-rented-bikes', 'figure'),
    [Input('date-picker-single', 'date')]
)
def update_graph(selected_date):
    if selected_date is None:
        selected_date = datab['Date'].min().date()
    
    # Filtrar datos por la fecha seleccionada
    filtered_data = datab[datab['Date'].dt.date == pd.to_datetime(selected_date).date()]
    
    # Crear el boxplot
    fig = px.line(filtered_data, 
                 x="Hour", 
                 y="Rented Bike Count", 
                 color="DayOfWeek", 
                 title=f"Bicicletas Rentadas por Hora en {selected_date}")
    
    return fig

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)
