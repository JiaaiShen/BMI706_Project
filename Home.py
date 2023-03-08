import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home"
)

st.write("# U.S. Chronic Disease Mortality Trend Map 🇺🇸")

st.sidebar.success("Select a demo to start.")
image = Image.open('titleimg.png')
st.image(image)
st.markdown(
    """
    ### What is the data?  
    We will be utilizing a publicly available dataset of the U.S. Chronic Disease
    Indicators (CDI), sourced from the Division of Population Health at the Centers
    for Disease Control and Prevention (CDC) . This comprehensive dataset
    includes chronic disease data pertaining to key areas of public health practice
    as reported by U.S. states and territories via the Behavioral Risk Factor
    Surveillance System (BRFSS). The dataset consists of an extensive array of
    time-labeled chronic disease prevalence statistics and data on relevant risk
    factors. 

    
    ##### 👈 Select a demo from the sidebar to explore our visualizations!!
    **Source of the dataset**: Centers for Disease Control and Prevention. (2021). U.S. Chronic Disease Indicators. CDC Division of Population Health. 
    Retrieved February 16, 2023, from https://chronicdata.cdc.gov/Chronic-Disease-Indicators/U-S-Chronic-Disease-Indicators-CDI-/g4ie-h725

"""
)
st.markdown("""---""")
st.markdown(
    """
    *Visualization created by Ziqian Liao & Joanna Shen*
"""
)