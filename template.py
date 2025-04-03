import streamlit as st

# --- Page configuration ---
st.set_page_config(page_title="My Dashboard", layout="wide")

# --- Hide Streamlit default menu and footer ---
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Adjust the z-index of the fixed-top-bar to ensure it stays on top
custom_css = """
    <style>
        /* Fixed top bar styling */
        .fixed-top-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #dcef6e;
            padding: 10px;
            text-align: left;
            z-index: 1100; /* Increased z-index to ensure it's above other elements */
            border-bottom: 1px solid #ccc;
        }
        /* Offset the body so content doesn't hide behind the fixed bar */
        body {
            margin-top: 60px;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)

# --- Fixed top bar with title and subtitle ---
st.markdown("""
    <div class="fixed-top-bar">
        <h1 style="float: left; padding: 60px 0 0 250px;">Dashboard Title</h1>
    </div>
    """, unsafe_allow_html=True)

# Update automatically on changes
st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- Sidebar with filters ---
with st.sidebar:
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    st.header("Filters", anchor="filters")
    # Add filters here as needed


