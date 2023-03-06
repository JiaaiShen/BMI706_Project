import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

@st.cache
def load_data():    
    df2 = pd.read_csv('https://raw.githubusercontent.com/JiaaiShen/BMI706_Project/0861cc067c5080d479c6762fcd94e9cca2b851cf/interface_2_df.csv')
    return df2


df2 = load_data()
states = alt.topo_feature(data.us_10m.url, 'states')


st.write("## Sex- and Race/Ethnicity-Stratified Chronic Disease Mortality Rates")

year = st.slider('Year', min(df2['YearStart']), max(df2['YearStart']), min(df2['YearStart']))
subdata = df2[df2["YearStart"] == year]

sex = st.radio('Sex', ('Male','Female','Overall'))
subdata = subdata[subdata["Stratification1"] == sex]

chart = alt.Chart(states).mark_geoshape().encode(
    color='Death:Q'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(subdata, 'LocationID', ['Death'])
).project(
    type='albersUsa'
).properties(
    width=500,
    height=300
)

st.altair_chart(chart, use_container_width=True)
