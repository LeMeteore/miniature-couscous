import Levenshtein
import pandas as pd
import streamlit as st
import pathlib
import io


basedir = pathlib.Path(__file__).parent.parent.parent
datadir = basedir / "data"

st.set_page_config(
   page_title="Data reconciliation",
   layout="wide",
   initial_sidebar_state="collapsed",
   menu_items=None,
)

# Function to find the best match using Levenshtein distance
def find_best_match(value, c2_values):
    best_ratio = 0
    best_match = None
    for c2_value in c2_values:
        ratio = Levenshtein.ratio(str(value), str(c2_value))
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = c2_value
    return best_match, best_ratio

def build_matches(df1, c1, df2, c2):
    df3 = df1.copy(deep=True)
    match_col = []
    ratio_col = []
    for value in df1[c1]:
        best_match, ratio = find_best_match(value, df2[c2])
        match_col.append(best_match)
        ratio_col.append(ratio)
    df3["Ratio"] = ratio_col
    df3["Match"] = match_col
    # who are the not matched ?
    not_matched = set(df2[c2]) - set(df3["Match"])
    match_perct = len(set(df3["Match"])) / len(df2[c2]) * 100
    return df3, not_matched, match_perct

multi = '''## Data reconciliation

Form built specifically_for the people at AXE.

This form will help you do your data reconciliation.

First, upload an Excel file containing your first dataset. Next, upload the Excel file containing the second dataset.
'''
st.markdown(multi)

with st.form("my_form1", clear_on_submit=True):
   col1, col2 = st.columns(2)
   with col1:
       file1 = st.file_uploader(
          "First file",
          type=["xls", "xlsx"],
          help="Enter an Excel file containing your first Excel file."
       )
   with col2:
       file2 = st.file_uploader(
          "Second file",
          type=["xls", "xlsx"],
          help="Enter an Excel file containing your second Excel file."
       )
   submit1 = st.form_submit_button("Submit files")
   if submit1:
       df1 = pd.read_excel(file1, dtype=str)
       df2 = pd.read_excel(file2, dtype=str)
       st.session_state.df1 = df1
       st.session_state.df2 = df2


if ("df1" in st.session_state) and ("df2" in st.session_state):
    with st.form("my_form2", clear_on_submit=True):
        df1 = st.session_state.df1
        df2 = st.session_state.df2
        col3, col4 = st.columns(2)
        with col3:
            c1 = st.selectbox('Select one column from the first dataset', df1.columns)
        with col4:
            c2 = st.selectbox('Select one column from the second dataset', df2.columns)
        submit2 = st.form_submit_button("Submit columns")
        if submit2:
            df3, not_matched, perct = build_matches(df1, c1, df2, c2)
            global_ratio = sum(df3['Ratio'])/len(df3['Ratio'])
            st.write("Here is the matches")
            st.dataframe(df3)
            st.write(f"Global ratio: {global_ratio} %")
            st.write(f"Percentage of matched values: {perct} %")
            st.write(f"Not matched values are: {not_matched}")
