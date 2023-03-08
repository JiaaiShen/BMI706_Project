import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

@st.cache_data
def load_data():    
    df1 = pd.read_csv('https://raw.githubusercontent.com/JiaaiShen/BMI706_Project/main/data/interface_1_df.csv')
    return df1


df1 = load_data()
states = alt.topo_feature(data.us_10m.url, 'states')


st.write("## Relationship between Chronic Disease Mortality Rates, Age-Adjusted and Risk Factors")

year = st.slider('Year', min(df1['YearStart']), max(df1['YearStart']), 2018)
subset = df2[df2['YearStart'] == year]

disease = st.selectbox('Disease', df2['Question'].unique())
subset = subset[subset['Question'] == disease]

risk_factors = st.multiselect(
    'Risk Factors',
    df1['Question'].unique().isin(['Obesity', 'Healthy weight', 'Per capita alcohol consumption', 'Bringe drinking prevalence', 'Smoking']),
    ['Obesity', 'Smoking'])
subset = subset[subset['Question'].isin(risk_factors)]

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