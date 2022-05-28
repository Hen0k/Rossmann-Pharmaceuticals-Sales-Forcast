import streamlit as st
import pandas as pd
from io import StringIO


st.image('images/ROSSMANN.jpg')
st.header("Rossmann Pharmaceuticals Sales Forecaster")

input_data = st.file_uploader(label="Upload a CSV or excel file",
                              type=['csv', 'xlsx'],
                              accept_multiple_files=False)

if input_data is not None:

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(input_data)
    st.write(dataframe)
