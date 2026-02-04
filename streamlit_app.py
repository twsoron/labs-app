import streamlit as st

lab_1 = st.Page('lab_1.py', title = "Lab 1")
lab_2 = st.Page('lab_2.py', title = "Lab 2")
lab_3 = st.Page('lab_3.py', title = "Lab 3", default=True)

nav = st.navigation([lab_1, lab_2, lab_3])
st.set_page_config(page_title= "Labs", initial_sidebar_state="expanded")
nav.run()