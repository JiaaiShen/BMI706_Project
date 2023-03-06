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

year = st.slider('Year', min(df2['YearStart']), max(df2['YearStart']), 2018)
subdata = df2[df2["YearStart"] == year]

sex = st.radio('Sex', ('Male','Female','Overall'))
subdata = subdata[subdata["Stratification1"] == sex]

disease = st.selectbox('Disease', df2['Question'].unique())
subdata = subdata[subdata['Question'] == disease]

domain_min = df2['Rate'].loc[df2['Question'] == disease].loc[df2['Stratification1'] == sex].loc[pd.notna(df2['Rate'])].apply(float).min()
domain_max = df2['Rate'].loc[df2['Question'] == disease].loc[df2['Stratification1'] == sex].loc[pd.notna(df2['Rate'])].apply(float).max()

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

# chart_base = alt.Chart(states
#     ).properties( 
#         width=width,
#         height=height
#     ).project(project
#     ).add_selection(selector
#     ).transform_lookup(
#         lookup="id",
#         from_=alt.LookupData(subdata, "LocationID", ["Rate", 'LocationDesc', 'Question', 'YearStart', 'Stratification1']),
#     )

rate_scale = alt.Scale(domain=(domain_min, domain_max), scheme='oranges')
rate_color = alt.Color(field="Rate", type="quantitative", scale=rate_scale)

chart_rate = alt.Chart(states).mark_geoshape().encode(
    color = rate_color,
    opacity = alt.condition(selector, alt.value(1), alt.value(0)),
    tooltip = ['LocationDesc:N','Rate:Q']
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(subdata, "LocationID", ["Rate", 'LocationDesc', 'Question', 'YearStart', 'Stratification1']),
    ).project(
     type='albersUsa'
    ).add_selection(selector
    ).transform_filter(selector
    ).properties(
        width=width,
        height=height,
        title=f'Age-adjusted Mortality Rate of {disease}'
        )

df2_sub = df2.loc[df2['Question'] == disease].loc[df2['Stratification1'] == sex]
df2_sub_avg = df2_sub.groupby(['YearStart','LocationDesc'])['Rate'].mean().reset_index().groupby('YearStart')['Rate'].mean().reset_index()

# avgline = alt.Chart(df2_sub_avg).properties(
#     width = width,
#     height = height/2
# ).mark_line(point = True
# ).encode(
#     x = 'YearStart:T',
#     y = alt.Y('Rate', type="quantitative", scale=alt.Scale(domain = [df2_sub_avg['Rate'].min(),df2_sub_avg['Rate'].max() ])),
#     color = 'orange'
# )

trendline = alt.Chart(df2_sub).properties(
    width = width,
    height = height/2
).add_selection(
    selector
).transform_filter(
    selector
).mark_line(point = True
).encode(
    x='YearStart:T',
    y=alt.Y('Rate', type="quantitative", scale=alt.Scale(domain=[df2_sub['Rate'].loc[pd.notna(df2['Rate'])].apply(float).min(), df2_sub['Rate'].loc[pd.notna(df2['Rate'])].apply(float).max()])),
    color=alt.Color(field="LocationDesc", type="nominal", scale=alt.Scale(scheme = 'oranges')),
)

#alt.condition(selector, alt.value(1), alt.value(0))


# chart = alt.Chart(states).mark_geoshape().encode(
#     color=alt.condition(
#         alt.datum.Rate,
#         alt.Color('Rate:Q', scale=alt.Scale(scheme='reds', domain=(domain_min, domain_max), clamp=True)),
#         alt.value('lightgray')
#     ),
#     tooltip=[
#         alt.Tooltip('LocationDesc:N'),
#         alt.Tooltip('Rate:Q')
#     ]
# ).transform_lookup(
#     lookup='id',
#     from_=alt.LookupData(subdata, 'LocationID', ['Rate'])
# ).project(
#     type='albersUsa'
# ).properties(
#     width=500,
#     height=300
# )


if len(subdata) == 0:
    st.write("No data avaiable for given subset.")
else:
    st.altair_chart(alt.vconcat(background + chart_rate, trendline).resolve_scale(color='shared'), use_container_width=True)