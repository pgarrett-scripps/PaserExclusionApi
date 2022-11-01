import streamlit as st
body = ""
PROCESS_CANDIDATES_FILE = "data/process_candidates.py"

with open(PROCESS_CANDIDATES_FILE) as file:
    body=str(file.read())

st.header('APIO exclusionms list methods')

st.markdown("""
Include the methods on the instruments pyhton plugin.py script.
""")

st.code(body, language="python")