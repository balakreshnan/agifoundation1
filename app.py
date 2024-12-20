import streamlit as st
from cadto3d import autocadinsights

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
                                                 "AutoCAD", "About"])

# Display the selected page
if nav_option == "AutoCAD":
    autocadinsights()
elif nav_option == "About":
    autocadinsights()