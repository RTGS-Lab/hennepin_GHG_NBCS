import os
import io
import base64

from dash import Dash, html, dcc, no_update
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from .tools import calculate_carbon
import matplotlib.colors as mcolors
import plotly.graph_objects as go

import json
import pandas as pd
import geopandas as gpd

import warnings

warnings.filterwarnings("ignore")

#1. Reading a shape file with MN counties and selectin Hennepin
shape = gpd.read_file('./data/shp_bdry_census2020counties_ctus/Census2020Counties.shp').to_crs(4326)
shape = shape[shape['CO_NAME_FU']=='Hennepin County']
poly = shape.geometry.unary_union #getting a polygon to center the feature map

#2. Creating a custom colormap for different landcover classes
custom_cmap = [
    (0, (0.0, 0.0, 0.0, 0.0)),   # None         
    (1, 'yellow'), #Agro
    (2, 'darkgreen'), #Forest     
    (3, 'green'), #Shrub          
    (4, 'brown'), #Wetland        
    (5, 'lime'), #Grassland          
    (6, 'grey'), #Urban        
    (7, 'lightgrey'), #Sparse    
    (8, 'lightgreen') #Heathland    
]

colors = [color for value, color in custom_cmap if color != 'None']

cmap = mcolors.ListedColormap(colors)

#3. Initializing a Dash app
dash_app = Dash(
        __name__,external_stylesheets=[dbc.themes.DARKLY], prevent_initial_callbacks=True,
    )
dash_app.index_string = '''
                        <!DOCTYPE html>
                        <html>
                            <head>
                                {%metas%}
                                <title>{%title%}</title>
                                {%favicon%}
                                {%css%}
                                <style>
                                    /* Remove default margin and padding */
                                    html, body {
                                        margin: 0;
                                        padding: 0;
                                        overflow: hidden; /* Prevents scrolling */
                                        height: 100vh;
                                        width: 100vw;
                                    }
                                </style>
                            </head>
                            <body>
                                {%app_entry%}
                                <footer>
                                    {%config%}
                                    {%scripts%}
                                    {%renderer%}
                                </footer>
                            </body>
                        </html>
                        '''
#4. Uploading pre-computed combinations of sequiestration scenarios
df_before = pd.read_csv('./data/nlcd_bootstrapped.csv')

#5. Creating a set of histograms with defualt pre-computed sequestration rates
histogram_1 = go.Figure(data=[go.Histogram(x=df_before.storage)], layout=go.Layout(template='plotly_dark', title="Storage"))
histogram_2 = go.Figure(data=[go.Histogram(x=df_before.sequestration)], layout=go.Layout(template='plotly_dark', title="Sequestration"))
histogram_3 = go.Figure(data=[go.Histogram(x=df_before.storage)], layout=go.Layout(template='plotly_dark'))
histogram_4 = go.Figure(data=[go.Histogram(x=df_before.sequestration)], layout=go.Layout(template='plotly_dark'))

histogram_1.update_layout(yaxis_title="2021", xaxis_title="million T CO2e yr-1", width=320, height=300)
histogram_1.add_annotation(x=df_before.storage.mean(),
            text=f"Mean: {round(df_before.storage.mean(),2)}",
            showarrow=True,
            arrowhead=1)
histogram_2.update_layout(yaxis_title="2021", xaxis_title="million T CO2e yr-1",width=320, height=300)
histogram_2.add_annotation(x=df_before.sequestration.mean(),
            text=f"Mean: {round(df_before.sequestration.mean(),2)}",
            showarrow=True,
            arrowhead=1)
histogram_3.update_layout(yaxis_title="Now", xaxis_title="million T CO2e yr-1", width=320, height=300)
histogram_4.update_layout(yaxis_title="Now", xaxis_title="million T CO2e yr-1", width=320, height=300)

#6. Setting up dashboard layout
dash_app.layout = html.Div(
        [
            dbc.Row([
                dbc.Col([
                    html.H1("Hennepin Carbon Calculator", style={'display': 'block', 'grid-area': 'a'}, className='block'),
                ]),
                
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([dcc.Input(
                        id="class",
                        placeholder="Enter Polygon Class(es)",
                        style={
                            'display': 'block', 'border-radius': '1px', 'background-color': 'black',
                            'font-size': '22px', 'height': '40px', 'color': 'white',
                            'width': '400px'}
                    ), html.Button(id='submit-button', type='submit', children='✓',
                                style={'height': '40px', 'color': 'white', 'background-color': 'black',
                                        'border-radius': '1px', 'font-size': '22px', 'width': '40px'}
                                )],
                        style={'grid-area': 'b', 'display': 'flex'}),
                ]),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dl.Map(center=[poly.centroid.y, poly.centroid.x], zoom=10, children=[
                        dl.LayersControl([
                            dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png",
                                id="TileMap")), name="CartoDB", checked=False),
                            dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
                                id="TileMap2")), name="Alidade Dark", checked=True),
                            dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                url="https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}",
                                id="USGS")), name="USGS", checked=False),
                            dl.Overlay(dl.LayerGroup(dl.ImageOverlay(
                                url='/assets/nlcd.png', id='image-overlay',
                                bounds=[[44.785014, -93.768081], [45.24612, -93.17681]]
                            )), name="NLCD Hennepin", checked=True),
                            dl.Colorbar(colorscale=colors, width=20, height=200, min=0, max=8, position="bottomleft"),
                            dl.FeatureGroup([dl.EditControl(id='draw-control')]),
                        ]),
                    ], style={'width': '800px', 'height': '600px', 'display': 'flex'}),
                ]),
                dbc.Col([
                    dbc.Row([
                        html.Div([dcc.Graph(id='hist-1', figure=histogram_1)]),
                    ]),
                    dcc.Loading(
                        id="loading-hist",
                        type="circle",
                        children=[dbc.Row([
                            html.Div([dcc.Graph(id='hist-3', figure=histogram_3)])]),
                        ]
                    )
                ], className="gx-0"),
                dbc.Col([
                    dbc.Row([
                        html.Div([dcc.Graph(id='hist-2', figure=histogram_2)]),
                    ]),
                    dcc.Loading(
                        id="loading-hist2",
                        type="circle",
                        children=[dbc.Row([
                            html.Div([dcc.Graph(id='hist-4', figure=histogram_4)])]),
                        ]
                    )
                ], className="gx-0"),
            ], className="gx-0"),
            html.Br(),
        ]
    )

#7. Creating a callback to update two histograms and the map if submit button is clicked
@dash_app.callback(
    Output('image-overlay', 'url'),
    Output('hist-4', 'figure'),
    Output('hist-3', 'figure'),
    Input('draw-control', 'geojson'),
    Input('submit-button', 'n_clicks'),
    Input('class', 'value')
)
def update_output(geojson, click, lc):
    global polygons, classes, encoded_image, df_before

    if geojson!=None and click!=None:
        polygons = geojson
        classes = list(lc)
        df, fig = calculate_carbon(polygons, classes)
        histogram_3 = go.Figure(data=[go.Histogram(x=df.storage)], layout=go.Layout(template='plotly_dark'))
        histogram_4 = go.Figure(data=[go.Histogram(x=df.sequestration)], layout=go.Layout(template='plotly_dark'))

        histogram_3.update_layout(yaxis_title="2021", width=320, height=300)
        histogram_3.add_annotation(x=df.storage.mean(),
            text=f"Mean: {round(df.storage.mean(),2)}",
            showarrow=True,
            arrowhead=1)
        histogram_4.update_layout(yaxis_title="2021",width=320, height=300)
        histogram_4.add_annotation(x=df.sequestration.mean(),
            text=f"Mean: {round(df.sequestration.mean(),2)}",
            showarrow=True,
            arrowhead=1)
                             
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True, dpi=1200)
        buf.seek(0)
        encoded_image = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        url = f"data:image/png;base64,{encoded_image}"
        return url, histogram_4, histogram_3
    return no_update, no_update, no_update
