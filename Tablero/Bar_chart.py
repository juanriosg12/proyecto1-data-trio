import dash
from dash import dcc  # dash core components
from dash import html  # dash html components
import plotly.express as px
import pandas as pd

# Leer el archivo CSV
datab = pd.read_csv(r"C:\Users\USER\OneDrive - Universidad de los andes\Analitica comp\Proyecto\SeoulBikeData_utf8.csv")

# Estilos externos
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Inicializar la app Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Crear la gráfica
fig = px.histogram(datab, x='Seasons', y='Rented Bike Count', color='Seasons') 

# Definir el layout de la app
app.layout = html.Div(children=[
    html.H1(children='Cantidad de Bicicletas Rentadas por Estación'),

    dcc.Graph(
        id='graph-rented-bikes',
        figure=fig
    )
])

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)



