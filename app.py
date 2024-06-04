from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import data
import pycountry
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

fig_scatter_country_count = px.scatter(title="Přehled uživatel jednotlivch zemí")
fig_vek_skupin = px.scatter(title="Heatmap - pohlaví jednotlivých obyvatel")
fig_bar_sex = px.bar(title="Přehled pohlaví - berem v potaz pouze 2!")
fig_map_scatter = px.scatter_geo(title="Mapa - země a počet uživatelů")
fig_registered_time = px.line(title="Čas registrace")

app.layout = html.Div([
    html.H1("Přehled uživatelů aplikace", style={'textAlign': 'center', "margin": "10px", "padding": "20px"}),
    dbc.Card(
       [
           dbc.CardBody(
               [
                   html.H4("Celkový počet uživatelů", className="card-title"),
                   html.P(id="total-users", className="card-text"),
               ]
           )
       ],
       style={"width": "18rem", "margin": "10px", "padding-bottom": "10px", "backgroundColor": "#222", "borderColor": "#333"}
   ),


    dcc.Dropdown(
        id='country-filter', 
        options=[],
        multi=True, 
        placeholder="Vyberte země jako globální filtr pro celý dashboard",
        style={"margin": "10px auto", "width": "80%", "maxWidth": "80%", "backgroundColor": "#222", "borderColor": "#333", "color": "black"}),

        dcc.Graph(id='scatter-country-count', figure=fig_scatter_country_count),

        dcc.Graph(id='vek-skupin', figure=fig_vek_skupin),

        dcc.Graph(id='sex-bargraph', figure=fig_bar_sex),

        dcc.Graph(id='map-scatter', figure=fig_map_scatter),

        dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            display_format='YYYY-MM-DD',
            style={"margin": "10px auto", "width": "80%", "padding": "10px", "maxWidth": "80%", "backgroundColor": "#222", "color": "black"}),

        dcc.Graph(id='registered-time', figure=fig_registered_time),

        dcc.Interval(
                id='interval-component',
                interval=30*1000,  # Interval pro update DB
                n_intervals=0
            ),

    html.Footer(
        html.P(
            "Made with ❤ by Martin Vlnas!",
            style={"textAlign": "center", "margin": "10px 0"}
        )
    )
    
])
@app.callback(
    [Output('vek-skupin', 'figure'),
     Output('sex-bargraph', 'figure'),
     Output('scatter-country-count', 'figure'),
     Output('map-scatter', 'figure'),
     Output('country-filter', 'options'),
     Output('total-users', 'children'),
     Output('registered-time', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('country-filter', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(n, country_filter, start_date, end_date):
    # Získám data z DB
    try:
        raw_data = data.get_data()
        total_users = len(raw_data)
    except Exception as e:
        print(f"Zíkání dat - chyba: {e}")
        return px.scatter(title="Nemáme data.."), px.bar(title="Nemáme data.."), px.scatter(title="Nemáme data.."), px.scatter_geo(title="Nemáme data.."), []
    
    if not raw_data:
        print("Nezískla jsem data")
        return px.scatter(title="Nemáme data.."), px.bar(title="Nemáme data.."), px.scatter(title="Nemáme data.."), px.scatter_geo(title="Nemáme data.."), []

    df = pd.DataFrame(raw_data, columns=['id', 'gender', 'first_name', 'last_name', 'email', 'dob', 'registered', 'phone', 'nationality', 'country', 'postcode'])
    
    
    # Příprava dat pro Dropdown
    country_options = [{'label': country, 'value': country} for country in df['country'].unique()]
    
    # Filtrace zemí
    if country_filter:
        df = df[df['country'].isin(country_filter)]

    # Scatter - země a count()
    scatter_country_count = df.groupby(['country']).size().reset_index(name='count')
    fig_scatter_country_count = px.scatter(scatter_country_count, x="country", y="count", size="count", color="count", title="Přehled uživatel jednotlivch zemí")

    # Heatmap - vekove skupiny
    df['dob'] = pd.to_datetime(df['dob'])
    df['age'] = (pd.Timestamp('now') - df['dob']).dt.days // 365
    bins = [0, 18, 30, 45, 60, 75, 100]
    labels = ['0-18', '19-30', '31-45', '46-60', '61-75', '76-100']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)

    age_gender_country_count = df.groupby(['country', 'age_group']).size().unstack(fill_value=0)
    fig_age_gender_country = px.imshow(age_gender_country_count, height=600, aspect='auto', title="Heatmap - věkové skupiny")

    
    # Bar plot - gender by country
    gender_country_data = df.groupby(['country', 'gender']).size().reset_index(name='count')
    fig_bar_sex = px.bar(gender_country_data, x="country", y="count", color="gender", title="Přehled pohlaví v jednotlivých zemích")

    # Mapa uživatelů
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']

    # Převod na kod země dle názvu pro graf
    def get_country_code(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except:
            return None

    country_counts['country_code'] = country_counts['country'].apply(get_country_code)
    country_counts = country_counts[country_counts['country_code'].notna()]
    country_filter = [{'label': country, 'value': code} for country, code in zip(country_counts['country'], country_counts['country_code'])]
    print(country_filter)
    fig_map_scatter = px.scatter_geo(country_counts, locations="country_code", size="count", color="count", height=800, title="Mapa - země a počet uživatelů")
    
    # line graf pro vizualizaci registrací na čase s timesliderem pro každý ze států dle filtru
    registered_time_country = df.groupby(['country', 'registered']).size().reset_index(name='count')
    fig_registered_time = px.line(registered_time_country, x="registered", y="count", color="country", title="Čas registrace podle země", range_x=[start_date, end_date])
    
    # Return grafů
    return fig_age_gender_country, fig_bar_sex, fig_scatter_country_count, fig_map_scatter, country_options, f'Total Users: {total_users}',fig_registered_time

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050, dev_tools_hot_reload=True)
