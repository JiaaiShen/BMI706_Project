import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

@st.cache_data
def load_data():    
    df2 = pd.read_csv('https://github.com/JiaaiShen/BMI706_Project/blob/4dbab360c4292ef68bcba27da8729b80b3c74b7a/data/interface_2_df_updated.csv?raw=true')
    return df2


df2 = load_data()
states = alt.topo_feature(data.us_10m.url, 'states')


st.write("## Sex- and Race/Ethnicity-Stratified Chronic Disease Mortality Rates, Age-Adjusted")

year = st.slider('Year', min(df2['YearStart']), max(df2['YearStart']), min(df2['YearStart']))
subdata = df2[df2["YearStart"] == year]

sex = st.radio('Sex', ('Male','Female','Overall'))
subdata = subdata[subdata["Stratification1"] == sex]

disease = st.selectbox('Disease', df2['Question'].unique())
subdata = subdata[subdata['Question'] == disease]

foreground = alt.Chart(states).mark_geoshape().encode(
    color=alt.Color('Rate:Q', scale=alt.Scale(scheme='reds', domain=(min(df2['Rate']), max(df2['Rate'])), clamp=True),legend=alt.Legend(title="Age-Adjusted Mortality Rate per 100k")),
    tooltip=[
        alt.Tooltip('LocationDesc:N'),
        alt.Tooltip('Rate:Q')
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(subdata, 'LocationID', ['Rate'])
).project(
    type='albersUsa'
).properties(
    width=500,
    height=300
)

background = alt.Chart(states).mark_geoshape(
    fill = 'lightgray',
    stroke = 'white'
).properties(
    title=f"age-adjusted {disease} mortality rates for {sex} in {year}",
    width=500,
    height=300
).project('albersUsa')

if len(subdata) == 0:
    st.write("No data avaiable for given subset.")
else:
    st.altair_chart(foreground+background, use_container_width=True)