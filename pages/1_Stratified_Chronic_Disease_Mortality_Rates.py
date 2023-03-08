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

df2['Year'] = pd.to_datetime(df2['YearStart'], format='%Y')
df2['State'] = df2['LocationDesc']

st.write("## Stratified Chronic Disease Mortality Rates")

with st.sidebar:
    st.markdown(
    """
    ### What now?
    * Drag the slidebar to select a subset of data based on year of collection
    * Choose 'Overall' or one of the stratification levels to show statistics of the population that you are interested in
    * Choose 1 of the 8 chronic diseases that you want to explore
    """
    )

    year = st.slider('Year', min(df2['YearStart']), max(df2['YearStart']), 2018)
    subdata = df2[df2["YearStart"] == year]

    strat = st.radio('Stratification', ('Overall', 'Male', 'Female','Asian or Pacific Islander', 'Hispanic', 'White, non-Hispanic', 'American Indian or Alaska Native', 'Black, non-Hispanic'), horizontal = True)
    subdata = subdata[subdata["Stratification1"] == strat]

    disease = st.selectbox('Disease', df2['Question'].unique())
    subdata = subdata[subdata['Question'] == disease]

domain_min = df2['Rate'].loc[df2['Question'] == disease].loc[df2['Stratification1'] == strat].loc[pd.notna(df2['Rate'])].apply(float).min()
domain_max = df2['Rate'].loc[df2['Question'] == disease].loc[df2['Stratification1'] == strat].loc[pd.notna(df2['Rate'])].apply(float).max()

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

selector = alt.selection_multi(on = 'click', fields = ['State'], empty = 'all')

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
    tooltip = ['State:N','Rate:Q']
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(subdata, "LocationID", ["Rate", 'State', 'Question', 'YearStart', 'Stratification1']),
    ).project(
     type='albersUsa'
    ).add_selection(selector
    ).transform_filter(selector
    ).properties(
        width=width,
        height=height,
        title=f'Age-adjusted Mortality Rate of {disease}'
        )

df2_sub = df2.loc[df2['Question'] == disease].loc[df2['Stratification1'] == strat]
df2_sub_avg = df2_sub.groupby(['YearStart','State'])['Rate'].mean().reset_index().groupby('YearStart')['Rate'].mean().reset_index()

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
    x='Year:T',
    y=alt.Y('Rate', type="quantitative", scale=alt.Scale(domain=[df2_sub['Rate'].loc[pd.notna(df2['Rate'])].apply(float).min(), df2_sub['Rate'].loc[pd.notna(df2['Rate'])].apply(float).max()])),
    color=alt.Color(field="State", type="nominal", scale=alt.Scale(scheme = 'oranges'), legend=alt.Legend(symbolLimit=10)),
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


allstates = df2['LocationDesc'].unique().tolist()
allstates.remove('United States')
allstates.sort()

comparestates = st.multiselect(
    'Select up to 5 states to keep track of and compare their statistics',
    allstates,
    ['Massachusetts','West Virginia', 'Texas', 'California','New York'], max_selections = 5)

col_all = st.columns(5)
for i in range(len(comparestates)):
    val = subdata.loc[subdata['LocationDesc'] == comparestates[i]]['Rate']
    col_all[i].metric(label=comparestates[i], value=val)

if len(subdata) == 0:
    st.write("No data avaiable for given subset.")
else:
    st.altair_chart(alt.vconcat(background + chart_rate, trendline).resolve_scale(color='shared'), use_container_width=True)
