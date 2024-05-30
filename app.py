from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import data

app = Dash(__name__)

fig_scatter_country_count = px.scatter(title="Přehled uživatel jednotlivch zemí")
fig_gender_country = px.scatter(title="Heatmap - pohlaví jednotlivých obyvatel")
fig_bar_sex = px.bar(title="Přehled pohlaví - berem v potaz pouze 2!")

app.layout = html.Div([
    html.H1("Přehled uživatelů aplikace", style={'textAlign': 'center'}),
    dcc.Graph(id='scatter-country-count', figure=fig_scatter_country_count),
    dcc.Graph(id='gender-country-graph', figure=fig_gender_country),
    dcc.Graph(id='sex-bargraph', figure=fig_bar_sex),
    dcc.Interval(
            id='interval-component',
            interval=4*1000, # Interval pro update DB
            n_intervals=0
        )
])

@app.callback(
    [Output('gender-country-graph', 'figure'),
     Output('sex-bargraph', 'figure'),
     Output('scatter-country-count', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    # Získám data z DB
    try:
        raw_data = data.get_data()
        print(raw_data)
    except Exception as e:
        print(f"Zíkání dat - chyba: {e}")
        return px.scatter(title="Nemáme data.."), px.bar(title="Nemáme data..")
    
    if not raw_data:
        print("Nezískla jsem data")
        return px.scatter(title="Nemáme data.."), px.bar(title="Nemáme data..")

    df = pd.DataFrame(raw_data, columns=['id', 'gender', 'first_name', 'last_name', 'email', 'dob', 'registered', 'phone', 'nationality', 'country', 'postcode'])
    
    # Scatter - země a count()
    scatter_country_count = df.groupby(['country']).size().reset_index(name='count')
    fig_scatter_country_count = px.scatter(scatter_country_count, x="country", y="count", title="Přehled uživatel jednotlivch zemí")

    gender_country_count = df.groupby(['country', 'gender']).size().unstack(fill_value=0)
    fig_gender_country = px.imshow(gender_country_count,height=600, aspect='auto', title="Heatmap - pohlaví jednotlivých obyvatel")
    fig_gender_country.update_layout(title_x=0.5)
    
    sex_data = df['gender'].value_counts().reset_index(name='count')
    fig_bar_sex = px.bar(sex_data, x="gender", y="count", title="Přehled pohlaví - berem v potaz pouze 2!")
    
    return fig_gender_country, fig_bar_sex, fig_scatter_country_count

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050, dev_tools_hot_reload=True)