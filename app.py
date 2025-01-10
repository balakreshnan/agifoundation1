import streamlit as st
from cadto3d import autocadinsights
from mfgagentst import mfgagents
from cadto3do1 import autocadinsightso1

# Set page size
st.set_page_config(
    page_title="Gen AI Application Validation",
    page_icon=":rocket:",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)

# Load your CSS file
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to load the CSS
load_css("styles.css")

#st.logo("images/mfglogo.png")
#st.sidebar.image("images/mfglogo.png", use_column_width=True)

# Sidebar navigation
nav_option = st.sidebar.selectbox("Navigation", ["Home", 
                                                 "AutoCAD", "Auto CAD o1"
                                                 , "Manufacturing"
                                                 , "About"])

# Display the selected page
if nav_option == "AutoCAD":
    autocadinsights()
if nav_option == "Auto CAD o1":
    autocadinsightso1()
elif nav_option == "Manufacturing":
    mfgagents()
elif nav_option == "About":
    autocadinsights()