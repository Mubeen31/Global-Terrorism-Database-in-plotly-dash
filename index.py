import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

terr2 = pd.read_csv('modified_globalterrorismdb_0718dist.csv')

location1 = terr2[['country_txt', 'latitude', 'longitude']]
list_locations = location1.set_index('country_txt')[['latitude', 'longitude']].T.to_dict('dict')

region = terr2['region_txt'].unique()

app = dash.Dash(__name__, )
app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div([
                html.H3('Global Terrorism Database', style = {"margin-bottom": "0px", 'color': 'white'}),
                html.H5('1970 - 2017', style = {"margin-top": "0px", 'color': 'white'}),

            ]),
        ], className = "six column", id = "title")

    ], id = "header", className = "row flex-display", style = {"margin-bottom": "25px"}),

    html.Div([
        html.Div([
            dcc.Graph(id = 'map_1',
                      config = {'displayModeBar': 'hover'}),

        ], className = "create_container 12 columns"),

    ], className = "row flex-display"),

    html.Div([
        html.Div([
            html.P('Select Region:', className = 'fix_label', style = {'color': 'white'}),
            dcc.Dropdown(id = 'w_countries',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         value = 'South Asia',
                         placeholder = 'Select Countries',
                         options = [{'label': c, 'value': c}
                                    for c in region], className = 'dcc_compon'),

            html.P('Select Country:', className = 'fix_label', style = {'color': 'white'}),
            dcc.Dropdown(id = 'w_countries1',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         placeholder = 'Select Countries',
                         options = [], className = 'dcc_compon'),

            html.P('Select Year:', className = 'fix_label', style = {'color': 'white', 'margin-left': '1%'}),
            dcc.RangeSlider(id = 'select_years',
                            min = 1970,
                            max = 2017,
                            dots = False,
                            value = [2010, 2017]),

        ], className = "create_container three columns"),

        html.Div([
            dcc.Graph(id = 'bar_line_1',
                      config = {'displayModeBar': 'hover'}),

        ], className = "create_container six columns"),

        html.Div([
            dcc.Graph(id = 'pie',
                      config = {'displayModeBar': 'hover'}),

        ], className = "create_container three columns"),

    ], className = "row flex-display"),

], id = "mainContainer", style = {"display": "flex", "flex-direction": "column"})


@app.callback(
    Output('w_countries1', 'options'),
    Input('w_countries', 'value'))
def get_country_options(w_countries):
    terr3 = terr2[terr2['region_txt'] == w_countries]
    return [{'label': i, 'value': i} for i in terr3['country_txt'].unique()]


@app.callback(
    Output('w_countries1', 'value'),
    Input('w_countries1', 'options'))
def get_country_value(w_countries1):
    return [k['value'] for k in w_countries1][0]

# Create scattermapbox chart
@app.callback(Output('map_1', 'figure'),
              [Input('w_countries', 'value')],
              [Input('w_countries1', 'value')],
              [Input('select_years', 'value')])
def update_graph(w_countries, w_countries1, select_years):
    terr3 = terr2.groupby(['region_txt', 'country_txt', 'provstate', 'city', 'iyear', 'latitude', 'longitude'])[['nkill', 'nwound']].sum().reset_index()
    terr4 = terr3[(terr3['region_txt'] == w_countries) & (terr3['country_txt'] == w_countries1) & (terr3['iyear'] >= select_years[0]) & (terr3['iyear'] <= select_years[1])]

    if w_countries1:
        zoom = 3
        zoom_lat = list_locations[w_countries1]['latitude']
        zoom_lon = list_locations[w_countries1]['longitude']


    return {
        'data': [go.Scattermapbox(
            lon = terr4['longitude'],
            lat = terr4['latitude'],
            mode = 'markers',
            marker = go.scattermapbox.Marker(
                size = terr4['nwound'],
                color = terr4['nwound'],
                colorscale = 'hsv',
                showscale = False,
                sizemode = 'area'),

            hoverinfo = 'text',
            hovertext =
            '<b>Region</b>: ' + terr4['region_txt'].astype(str) + '<br>' +
            '<b>Country</b>: ' + terr4['country_txt'].astype(str) + '<br>' +
            '<b>Province/State</b>: ' + terr4['provstate'].astype(str) + '<br>' +
            '<b>City</b>: ' + terr4['city'].astype(str) + '<br>' +
            '<b>Longitude</b>: ' + terr4['longitude'].astype(str) + '<br>' +
            '<b>Latitude</b>: ' + terr4['latitude'].astype(str) + '<br>' +
            '<b>Killed</b>: ' + [f'{x:,.0f}' for x in terr4['nkill']] + '<br>' +
            '<b>Wounded</b>: ' + [f'{x:,.0f}' for x in terr4['nwound']] + '<br>' +
            '<b>Year</b>: ' + terr4['iyear'].astype(str) + '<br>'

        )],

        'layout': go.Layout(
            margin = {"r": 0, "t": 0, "l": 0, "b": 0},
            hovermode = 'closest',
            mapbox = dict(
                accesstoken = 'pk.eyJ1IjoicXM2MjcyNTI3IiwiYSI6ImNraGRuYTF1azAxZmIycWs0cDB1NmY1ZjYifQ.I1VJ3KjeM-S613FLv3mtkw',  # Use mapbox token here
                center = go.layout.mapbox.Center(lat = zoom_lat, lon = zoom_lon),
                # style='open-street-map',
                style = 'dark',
                zoom = zoom
            ),
            autosize = True,

        )

    }

# Create combination of bar and line  chart (show number of attack and death)
@app.callback(Output('bar_line_1', 'figure'),
              [Input('w_countries', 'value')],
              [Input('w_countries1', 'value')],
              [Input('select_years', 'value')])
def update_graph(w_countries, w_countries1, select_years):
    # Data for line and bar
    terr5 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])['nkill'].sum().reset_index()
    terr6 = terr5[(terr5['region_txt'] == w_countries) & (terr5['country_txt'] == w_countries1) & (terr5['iyear'] >= select_years[0]) & (terr5['iyear'] <= select_years[1])]
    terr7 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])[['attacktype1', 'nwound']].sum().reset_index()
    terr8 = terr7[(terr7['region_txt'] == w_countries) & (terr7['country_txt'] == w_countries1) & (terr7['iyear'] >= select_years[0]) & (terr7['iyear'] <= select_years[1])]

    return {
        'data': [go.Scatter(x = terr6['iyear'],
                            y = terr6['nkill'],
                            mode = 'lines+markers',
                            name = 'Death',
                            line = dict(shape = "spline", smoothing = 1.3, width = 3, color = '#FF00FF'),
                            marker = dict(size = 10, symbol = 'circle', color = 'white',
                                          line = dict(color = '#FF00FF', width = 2)
                                          ),
                            hoverinfo = 'text',
                            hovertext =
                            '<b>Region</b>: ' + terr6['region_txt'].astype(str) + '<br>' +
                            '<b>Country</b>: ' + terr6['country_txt'].astype(str) + '<br>' +
                            '<b>Year</b>: ' + terr6['iyear'].astype(str) + '<br>' +
                            '<b>Death</b>: ' + [f'{x:,.0f}' for x in terr6['nkill']] + '<br>'

                            ),
                 go.Bar(
                     x = terr8['iyear'],
                     y = terr8['attacktype1'],
                     text = terr8['attacktype1'],
                     texttemplate = '%{text:.2s}',
                     textposition = 'auto',
                     name = 'Attack',

                     marker = dict(color = 'orange'),

                     hoverinfo = 'text',
                     hovertext =
                     '<b>Region</b>: ' + terr8['region_txt'].astype(str) + '<br>' +
                     '<b>Country</b>: ' + terr8['country_txt'].astype(str) + '<br>' +
                     '<b>Year</b>: ' + terr8['iyear'].astype(str) + '<br>' +
                     '<b>Attack</b>: ' + [f'{x:,.0f}' for x in terr8['attacktype1']] + '<br>'
                 ),

                 go.Bar(x = terr8['iyear'],
                        y = terr8['nwound'],
                        text = terr8['nwound'],
                        texttemplate = '%{text:.2s}',
                        textposition = 'auto',
                        textfont = dict(
                            color = 'white'
                        ),
                        name = 'Wounded',

                        marker = dict(color = '#9C0C38'),

                        hoverinfo = 'text',
                        hovertext =
                        '<b>Region</b>: ' + terr8['region_txt'].astype(str) + '<br>' +
                        '<b>Country</b>: ' + terr8['country_txt'].astype(str) + '<br>' +
                        '<b>Year</b>: ' + terr8['iyear'].astype(str) + '<br>' +
                        '<b>Wounded</b>: ' + [f'{x:,.0f}' for x in terr8['nwound']] + '<br>'
                        )],

        'layout': go.Layout(
            barmode = 'stack',
            plot_bgcolor = '#010915',
            paper_bgcolor = '#010915',
            title = {
                'text': 'Attack and Death : ' + (w_countries1) + '  ' + '<br>' + ' - '.join(
                    [str(y) for y in select_years]) + '</br>',

                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': 'white',
                'size': 20},

            hovermode = 'x',

            xaxis = dict(title = '<b>Year</b>',
                         tick0 = 0,
                         dtick = 1,
                         color = 'white',
                         showline = True,
                         showgrid = True,
                         showticklabels = True,
                         linecolor = 'white',
                         linewidth = 2,
                         ticks = 'outside',
                         tickfont = dict(
                             family = 'Arial',
                             size = 12,
                             color = 'white'
                         )

                         ),

            yaxis = dict(title = '<b>Attack and Death</b>',
                         color = 'white',
                         showline = True,
                         showgrid = True,
                         showticklabels = True,
                         linecolor = 'white',
                         linewidth = 2,
                         ticks = 'outside',
                         tickfont = dict(
                             family = 'Arial',
                             size = 12,
                             color = 'white'
                         )

                         ),

            legend = {
                'orientation': 'h',
                'bgcolor': '#010915',
                'xanchor': 'center', 'x': 0.5, 'y': -0.3},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = 'white'),

        )

    }


# Create pie chart (total casualties)
@app.callback(Output('pie', 'figure'),
              [Input('w_countries', 'value')],
              [Input('w_countries1', 'value')],
              [Input('select_years', 'value')])
def display_content(w_countries, w_countries1, select_years):
    terr9 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])[
        ['nkill', 'nwound', 'attacktype1']].sum().reset_index()
    death = terr9[(terr9['region_txt'] == w_countries) & (terr9['country_txt'] == w_countries1) & (terr9['iyear'] >= select_years[0]) & (terr9['iyear'] <= select_years[1])]['nkill'].sum()
    wound = terr9[(terr9['region_txt'] == w_countries) & (terr9['country_txt'] == w_countries1) & (terr9['iyear'] >= select_years[0]) & (terr9['iyear'] <= select_years[1])]['nwound'].sum()
    attack = terr9[(terr9['region_txt'] == w_countries) & (terr9['country_txt'] == w_countries1) & (terr9['iyear'] >= select_years[0]) & (terr9['iyear'] <= select_years[1])]['attacktype1'].sum()
    colors = ['#FF00FF', '#9C0C38', 'orange']

    return {
        'data': [go.Pie(labels = ['Total Death', 'Total Wounded', 'Total Attack'],
                        values = [death, wound, attack],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13)
                        # hole=.7,
                        # rotation=45
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            plot_bgcolor = '#010915',
            paper_bgcolor = '#010915',
            hovermode = 'closest',
            title = {
                'text': 'Total Casualties : ' + (w_countries1) + '  ' + '<br>' + ' - '.join(
                    [str(y) for y in select_years]) + '</br>',

                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': 'white',
                'size': 20},
            legend = {
                'orientation': 'h',
                'bgcolor': '#010915',
                'xanchor': 'center', 'x': 0.5, 'y': -0.07},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = 'white')
        ),

    }




if __name__ == '__main__':
    app.run_server(debug = True)
