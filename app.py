from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import data
import pycountry
import dash_bootstrap_components as dbc
import graph

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY]) # Bootstrap dark theme

# Vytvoření empty grafů
fig_scatter_country_count = px.scatter(title="Přehled uživatel jednotlivch zemí")
fig_vek_skupin = px.scatter(title="Heatmap - věkové skupiny")
fig_bar_sex = px.bar(title="Přehled pohlaví - berem v potaz pouze 2!")
fig_map_scatter = px.scatter_geo(title="Mapa - země a počet uživatelů")
fig_registered_time = px.line(title="Čas registrace")

# Update interval - 30 sekund
update_interval = 30

app.layout = dbc.Container([
    dcc.Interval(
        id='interval-component',
        interval=update_interval*1000,  # Interval pro update dat - zavolá funkci
        n_intervals=0
    ),
    dcc.Interval(
        id='countdown-interval',
        interval=1000,  # Interval pro update dat - zavolá funkci
        n_intervals=0
    ),
    html.Div(id='countdown-display', className="text-center mb-3"
    ),
    dbc.Row(
        dbc.Col(html.H1("Přehled uživatelů aplikace", className="text-center my-4"), width=12)
    ),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Celkový počet uživatelů:", className="card-title"),
                    html.P(id="total-users", className="card-text"),
                ]),
                className="mb-4"
            ),
            width=6, style={"display": "inline-block"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Počet unikátních zemí:", className="card-title"),
                    html.P(id="total-countries", className="card-text"),
                ]),
                className="mb-4"
            ),
            width=6, style={"display": "inline-block"}
        )
    ], justify="start"),
    dbc.Row(
        dbc.Col(
            dcc.Dropdown(
                id='country-filter',
                options=[],
                multi=True,
                placeholder="Vyberte země jako globální filtr pro celý dashboard",
                style={"width": "100%", "backgroundColor": "#222", "borderColor": "#333", "color": "black"}
            ),
            width=12, className="mb-3"
        )
    ),
    dbc.Row(
        dbc.Col(
            dbc.Button('Resetuj filtr zemí', id='reset-button', n_clicks=0, className="btn-dark btn-block"),
            width=4, className="mb-3"
        )
    ),
    dbc.Row(
        dbc.Col(dcc.Graph(id='scatter-country-count', figure=fig_scatter_country_count), width=12, className="mb-3")
    ),
    dbc.Row(
        dbc.Col(
            html.Div([
                html.H4("Filtr věkových skupin"),
                dcc.RangeSlider(
                    id='age-filter',
                    min=0,
                    max=100,
                    step=1,
                    marks={i: str(i) for i in range(0, 101, 10)},
                    value=[0, 30, 60, 100], # inital hodnoty pro 3 skupiny
                    allowCross=False,
                    pushable=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id='age-filter-output')
            ])
        ),
    ),
    dbc.Row(
        dbc.Col(
            dbc.Button('Resetuj věkové skupiny', id='reset-button-age', n_clicks=0, className="btn-dark btn-block"),
            width=4, className="mb-3 mt-3"
        ),
    ),
    dbc.Row(
        dbc.Col(dcc.Graph(id='vek-skupin', figure=fig_vek_skupin), width=12, className="mb-3")
    ),
    dbc.Row(
        dbc.Col(dcc.Graph(id='sex-bargraph', figure=fig_bar_sex), width=12, className="mb-3")
    ),
    dbc.Row(
        dbc.Col(dcc.Graph(id='map-scatter', figure=fig_map_scatter), width=12, className="mb-3")
    ),
    dbc.Row(
        dbc.Col(
            html.Div([
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    display_format='YYYY-MM-DD',
                    style={"width": "45%", "padding": "5px", "backgroundColor": "#222", "color": "white"}
                ),
                dbc.Button('Resetuj datum', id='reset-button-date', n_clicks=0, className="btn-dark ml-2")
            ], style={"display": "flex", "justify-content": "space-between", "width": "100%"}),
            width=12, className="mb-3"
        )
    ),
    dbc.Row(
        dbc.Col(dcc.Graph(id='registered-time', figure=fig_registered_time), width=12, className="mb-3")
    ),
    dbc.Row(
        dbc.Col(
            html.Footer(
                html.P("Made with ❤ by Martin Vlnas!", className="text-center")
            ),
            width=12
        )
    )
])

def prepare_data():
    try:
        raw_data = data.get_data()
        raw_data = raw_data.values() # seznam uživatelů - odstraím klíč id
        total_users = len(raw_data)
        print("Získal jsem data!")
        print(total_users)
    except Exception as e:
        print(f"Získání dat - chyba: {e}")
    return raw_data, total_users


@app.callback(
    [Output('vek-skupin', 'figure'),
     Output('sex-bargraph', 'figure'),
     Output('scatter-country-count', 'figure'),
     Output('map-scatter', 'figure'),
     Output('country-filter', 'options'),
     Output('total-users', 'children'),
     Output('total-countries', 'children'),
     Output('registered-time', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('country-filter', 'value'),
     Input('age-filter', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(n_intervals, country_filter, age_filter, start_date, end_date):
    # Získám data z DB
    try:
        raw_data, total_users = prepare_data()
    except Exception as e:
        print(f"Získání dat - chyba: {e}")

    # Vstupní data frame
    df = pd.DataFrame(raw_data, columns=['id', 'gender', 'first_name', 'last_name', 'email', 'dob', 'registered', 'phone', 'nationality', 'country', 'postcode'])
    
    countries_unique = df['country'].unique()
    total_countries = len(countries_unique)

    # Příprava dat pro Dropdown
    country_options = [{'label': country, 'value': country} for country in countries_unique]
    
    # Filtrace zemí
    if country_filter:
        df = df[df['country'].isin(country_filter)]

    # Scatter - země
    fig_scatter_country_count = graph.scatter_zeme_count(df)

    # Heatmap - vekove skupiny
    if age_filter:
        fig_age_gender_country = graph.heatmap_vekove_skupiny(df, age_filter)
    else:
        fig_age_gender_country = graph.heatmap_vekove_skupiny(df)

    # Bar plot - gender by country
    fig_bar_sex = graph.barplot_gender_country(df)

    # Mapa uživatelů - geografická vizualizace
    fig_map_scatter = graph.mapa_uzivatelu(df)
    
    # line graf pro vizualizaci registrací na čase s timesliderem pro každý ze států dle filtru
    fig_registered_time = graph.line_registrace_zeme(df, start_date, end_date)
    
    # Return grafů
    return fig_age_gender_country, fig_bar_sex, fig_scatter_country_count, fig_map_scatter, country_options, f'{total_users}', f'{total_countries}', fig_registered_time


@app.callback(
    Output('country-filter', 'value'),
    Input('reset-button', 'n_clicks'),
)
def reset_button(n):
    if n and n > 0:
        return [] # Vracím prázdn seznam, do komponenty country-filter - nastaví seznam zemí na prázdný
        # To následně vyvolá vrchní callback funkci a aktualizuje graf - načte hodnoty do filtru...


@app.callback(
    Output('age-filter', 'value'),
    Input('reset-button-age', 'n_clicks'),
)
def reset_button_age(n):
    if n and n > 0:
        return [0, 30, 60, 100]

# Callback pro reset datumu
@app.callback(
    [Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    [Input('reset-button-date', 'n_clicks')],
)
def reset_datetime(n):
    return (None, None)

@app.callback(
    Output('countdown-display', 'children'),
    [Input('countdown-interval', 'n_intervals'),
     Input('interval-component', 'n_intervals')]
)
def update_countdown(n_countdown, n_update):
    seconds_left = update_interval - (n_countdown % update_interval)
    return f"Příští aktualizace dat za: {seconds_left} sekund"

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050, dev_tools_hot_reload=True)
