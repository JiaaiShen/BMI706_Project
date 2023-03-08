import altair as alt
import pandas as pd
import numpy as np
import streamlit as st
from vega_datasets import data

@st.cache_data
def load_data():    
    df1_1 = pd.read_csv('https://github.com/JiaaiShen/BMI706_Project/blob/9dafb2d261002fcfa498aadf5050c80fd9519e8a/data/interface_1_df_1.csv?raw=true')
    df1_2 = pd.read_csv('https://github.com/JiaaiShen/BMI706_Project/blob/9dafb2d261002fcfa498aadf5050c80fd9519e8a/data/interface_1_df_2.csv?raw=true')
    return df1_1, df1_2


df1_1, df1_2 = load_data()
states = alt.topo_feature(data.us_10m.url, 'states')


st.write("## Relationship between Chronic Disease Mortality Rates, Age-Adjusted and Risk Factors")

year = st.slider('Year', min(df1_2['YearStart']), max(df1_2['YearStart']), 2018)
subset_1 = df1_1[df1_1['YearStart'] == year]
subset_2 = df1_2[df1_2['YearStart'] == year]

disease = st.selectbox('Disease', df1_1['Question'].unique())
subset_1 = subset_1[subset_1['Question'] == disease]

risk_factor = st.radio('Risk factor', df1_2['Question'].unique())
subset_2 = subset_2[subset_2['Question'] == risk_factor]

domain_min_d = np.nanmin(subset_1['Rate'].apply(float))
domain_max_d = np.nanmax(subset_1['Rate'].apply(float))

domain_min_r = np.nanmin(subset_2['Amount'].apply(float))
domain_max_r = np.nanmax(subset_2['Amount'].apply(float))

width = 600
height  = 400
project = 'albersUsa'

# a gray map using as the visualization background
background = alt.Chart(states
).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

selector = alt.selection_multi(on = 'click', fields = ['LocationDesc'], empty = 'all')

amount_scale = alt.Scale(domain=(domain_min_r, domain_max_r), scheme='blues')
amount_color = alt.Color(field='Amount', type='quantitative', scale=amount_scale)

chart_amount = alt.Chart(states).mark_geoshape().encode(
    color = amount_color,
    opacity = alt.condition(selector, alt.value(1), alt.value(0)),
    tooltip = [alt.Tooltip('LocationDesc:N', title='State'), 'Amount:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(subset_2, 'LocationID', ['Amount', 'LocationDesc', 'Question', 'YearStart']),
).project(
    type='albersUsa'
).add_selection(
    selector
).transform_filter(
    selector
).properties(
    width=width,
    height=height,
    title=f'Age-adjusted Prevalence of {risk_factor}'
)

df1_2_r = df1_2.loc[df1_2['Question'] == risk_factor]

trendline_r = alt.Chart(df1_2_r).properties(
    width=width,
    height=height/2
).add_selection(
    selector
).transform_filter(
    selector
).mark_line(
    point = True
).encode(
    x=alt.X('YearStart:O', title='Year'),
    y=alt.Y('Amount', type='quantitative', title='Prevalence', scale=alt.Scale(domain=(domain_min_r, domain_max_r))),
    color=alt.Color(field='LocationDesc', type='nominal', title='State', scale=alt.Scale(scheme='blues'), legend=alt.Legend(symbolLimit=10)),
    tooltip=[alt.Tooltip('YearStart:O', title='Year'), alt.Tooltip('LocationDesc:N', title='State'), 'Amount:Q']
)

df1_1_d = df1_1.loc[df1_1['Question'] == disease]

trendline_d = alt.Chart(df1_1_d).properties(
    width=width,
    height=height/2,
    title=f'Age-adjusted Mortality Rate of {disease}'
).add_selection(
    selector
).transform_filter(
    selector
).mark_line(
    point = True
).encode(
    x=alt.X('YearStart:O', title='Year'),
    y=alt.Y('Rate', type='quantitative', title='Mortality rate', scale=alt.Scale(domain=(domain_min_d, domain_max_d))),
    color=alt.Color(field='LocationDesc', type='nominal', title='State', scale=alt.Scale(scheme='blues'), legend = None),
    tooltip=[alt.Tooltip('YearStart:O', title='Year'), alt.Tooltip('LocationDesc:N', title='State'), 'Rate:Q']
)

if (len(subset_1) == 0) or (len(subset_2) == 0):
    st.write("No data avaiable for given subset.")
else:
    st.altair_chart(alt.vconcat(alt.vconcat(background + chart_amount, trendline_r), trendline_d).resolve_scale(color='shared'), use_container_width = True)