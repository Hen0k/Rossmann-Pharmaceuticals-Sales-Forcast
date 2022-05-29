import streamlit as st
import pandas as pd
from src.dashboard_helper import (
    load_model,
    preprocess,
    plot_predictions
)

rf_reg_model = load_model(model_path='models/model.pkl')

st.image('images/ROSSMANN.jpg')
st.header("Rossmann Pharmaceuticals Sales Forecaster")

input_data = st.file_uploader(label="Upload a CSV or excel file",
                              type=['csv', 'xlsx'],
                              accept_multiple_files=False)

if input_data is not None:

    # Can be used wherever a "file-like" object is accepted:
    test_df = pd.read_csv(input_data)
    test_df = preprocess(test_df)
    preds = rf_reg_model.predict(test_df)
    print(preds.shape)
    pred_fig = plot_predictions(date=[*range(len(preds))], sales=preds)
    st.write(f"---\n# Predictions")
    st.pyplot(pred_fig)
    st.write(f"---\n**Filtering by stores coming soon**")
