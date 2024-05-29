from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import data
import pymysql

app = Dash(__name__)

fig_gender_country = px.scatter(title="Gender by Country")
fig_nationality_phone = px.scatter(title="Nationality by Phone Number")

app.layout = html.Div([
    html.H1("Data Visualizations", style={'textAlign': 'center'}),
    dcc.Graph(id='gender-country-graph', figure=fig_gender_country),
    dcc.Graph(id='nationality-phone-graph', figure=fig_nationality_phone),
    dcc.Interval(
            id='interval-component',
            interval=5*1000,
            n_intervals=0
        )
])

@app.callback(
    [Output('gender-country-graph', 'figure'),
     Output('nationality-phone-graph', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    try:
        raw_data = data.get_data()
        print(raw_data)
    except Exception as e:
        print(f"Failed to retrieve data: {e}")
        return px.scatter(title="Failed to Load Data"), px.scatter(title="Failed to Load Data")
    
    if not raw_data:
        print("No data retrieved.")
        return px.scatter(title="No Data Available"), px.scatter(title="No Data Available")

    df = pd.DataFrame(raw_data, columns=['id', 'gender', 'first_name', 'last_name', 'email', 'dob', 'registered', 'phone', 'nationality', 'country', 'postcode'])
    

    gender_country_data = df[['gender', 'country']]
    fig_gender_country = px.scatter(gender_country_data, x="gender", y="country", title="Dynamic Gender by Country Scatter Plot")
    

    nationality_phone_data = df[['nationality', 'phone']]
    fig_nationality_phone = px.scatter(nationality_phone_data, x="nationality", y="phone", title="Dynamic Nationality by Phone Number Scatter Plot")
    
    return fig_gender_country, fig_nationality_phone

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050, dev_tools_hot_reload=True)