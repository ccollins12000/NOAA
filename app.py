import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import station
import pandas as pd
from dateutil import parser
import dash.exceptions
import StationSearch

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

current_date = int(datetime.date.today().strftime('%Y'))

app.layout = html.Div([

    html.Label('NOAA API Key', id='lbl-api-key', className='filter-label'),
    dcc.Input(value='API_KEY', type='text', id='txt-api-key', className='filter-txt'),
    html.Label('Zip Code: '),
    dcc.Input(value='55105', id='zip-code'),
    html.Button(children='Find Station', n_clicks=0, id='find-station'),
    html.Label('Station_Id', id='station-id'),
    dcc.RangeSlider(
        id='date-range',
        min=1860,
        max=current_date,
        step=50,
        value=[1860, current_date],
        marks={str(year): str(year) for year in range(1800, current_date + 1, 20)}
    ),
    html.Button(children='Get Data', n_clicks=0, id='get-data'),
    dcc.Graph(id='temperatures')
], id='controls', className='columns')


@app.callback(
    [Output(component_id='date-range', component_property='min'),
     Output(component_id='date-range', component_property='max'),
     Output(component_id='date-range', component_property='step'),
     Output(component_id='date-range', component_property='value'),
     Output(component_id='date-range', component_property='marks'),
     Output(component_id='station-id', component_property='children')
     ],
    [Input(component_id='find-station', component_property='n_clicks')],
    [State(component_id='zip-code', component_property='value'),
     State(component_id='txt-api-key', component_property='value')]
)
def find_station(n_clicks, zip_code, api_key):
    if n_clicks > 0:
        StationSearcher = StationSearch.StationSearch(api_key=api_key)
        StationSearcher.search(zip_code)
        Station = StationSearcher.return_station(station_index=0)

        start_year = int(Station._MIN_DATA_DATE.strftime('%Y'))
        end_year = int(Station._MAX_DATA_DATE.strftime('%Y'))
        years = end_year - start_year
        if years > 20:
            step = int((end_year - start_year) / 20)
        else:
            step = 1

        marks = {str(year): str(year) for year in range(start_year, end_year, step)}
        return start_year, end_year, step, [start_year, end_year], marks, Station._STATION_ID
    else:
        return 1800, 2020, 20, [1800, 2020], {str(year): str(year) for year in range(1800, current_date + 1, 20)}, ''


@app.callback(
    Output(component_id='temperatures', component_property='figure'),
    Input(component_id='get-data', component_property='n_clicks'),
    [State(component_id='txt-api-key', component_property='value'),
     State(component_id='station-id', component_property='children'),
     State(component_id='date-range', component_property='value')]
)
def retrieve_station_data(n_clicks, api_key, station_id, years):
    if n_clicks > 0:
        Station = station.Station(station_id, api_key)
        if not Station is None:
            Station.retrieve_temperature_data(datetime.date(years[0], 1, 1), datetime.date(years[1], 1, 2))

            temp_data = pd.DataFrame(Station.temperature_data)

            temp_data['date'] = temp_data['date'].apply(lambda x: parser.parse(x))
            fig = px.scatter(x=temp_data['date'],
                             y=temp_data['value'],
                             color=temp_data['datatype'])
            fig.update_xaxes(title='Date')

            fig.update_yaxes(title='Temperature')
            return fig
    else:
        fig = px.scatter(x=[1, 2],
                         y=[1, 2])
        fig.update_xaxes(title='Date')

        fig.update_yaxes(title='Temperature')

        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
