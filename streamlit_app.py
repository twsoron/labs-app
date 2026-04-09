import streamlit as st

lab_1 = st.Page('lab_1.py', title = "Lab 1")
lab_2 = st.Page('lab_2.py', title = "Lab 2")
lab_3 = st.Page('lab_3.py', title = "Lab 3")
lab_4 = st.Page('lab_4.py', title = "Lab 4")
lab_5 = st.Page('lab_5.py', title = "Lab 5")
lab_6 = st.Page('lab_6.py', title = "Lab 6")
lab_8 = st.Page('lab_8.py', title = "Lab 8", default=True)

nav = st.navigation([lab_1, lab_2, lab_3, lab_4, lab_5, lab_6, lab_8])
st.set_page_config(page_title= "Labs", initial_sidebar_state="expanded")
nav.run()