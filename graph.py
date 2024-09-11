import pycountry
import pandas as pd
import plotly.express as px
import pycountry

# Scatter - země a count()
def scatter_zeme_count(input_data):
    scatter_country_count = input_data.groupby(['country']).size().reset_index(name='count')
    fig_scatter_country_count = px.scatter(scatter_country_count, x="country", y="count", size="count", color="count", title="Přehled uživatel jednotlivch zemí")
    return fig_scatter_country_count


# Heatmap - vekove skupiny
def heatmap_vekove_skupiny(input_data, filter_age_group=None):
    input_data['dob'] = pd.to_datetime(input_data['dob'])
    input_data['age'] = (pd.Timestamp('now') - input_data['dob']).dt.days // 365

    if filter_age_group:
        bins = [filter_age_group[0], filter_age_group[1], filter_age_group[2], filter_age_group[3]]
        labels = [f"{filter_age_group[0]}-{filter_age_group[1]}", f"{filter_age_group[1]}-{filter_age_group[2]}", f"{filter_age_group[2]}-{filter_age_group[3]}"]
    else:
        # Default filter
        bins = [0, 30, 60, 100]
        labels = ['0-30', '31-60', '61-100']

    input_data['age_group'] = pd.cut(input_data['age'], bins=bins, labels=labels, right=False)
    age_gender_country_count = input_data.groupby(['country', 'age_group']).size().unstack(fill_value=0)
    
    title = "Heatmap - věkové skupiny"
    fig_age_gender_country = px.imshow(age_gender_country_count, height=600, aspect='auto', title=title)
    return fig_age_gender_country


# Bar plot - gender by country
def barplot_gender_country(input_data):
    gender_country_data = input_data.groupby(['country', 'gender']).size().reset_index(name='count')
    fig_bar_sex = px.bar(gender_country_data, x="country", y="count", color="gender", title="Přehled pohlaví v jednotlivch zemích")
    return fig_bar_sex

# Převod na kod země dle názvu pro graf kvůli navázaní na mapu
def get_country_code(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except:
            return None


# Mapa uživatelů - geografická vizualizace
def mapa_uzivatelu(input_data):
    country_counts = input_data['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    # Převod na kod země dle názvu pro graf
    country_counts['country_code'] = country_counts['country'].apply(get_country_code)
    country_counts = country_counts[country_counts['country_code'].notna()]
    country_filter = [{'label': country, 'value': code} for country, code in zip(country_counts['country'], country_counts['country_code'])]
    fig_map_scatter = px.scatter_geo(country_counts, locations="country_code", size="count", color="count", height=800, title="Mapa - země a počet uživatelů")
    return fig_map_scatter


def line_registrace_zeme(input_data, start_date, end_date):
    registered_time_country = input_data.groupby(['country', 'registered']).size().reset_index(name='count')
    fig_registered_time = px.line(registered_time_country, x="registered", y="count", color="country", title="Čas registrace podle země", range_x=[start_date, end_date])
    return fig_registered_time