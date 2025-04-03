<<<<<<< HEAD
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

# --- Custom CSS for styling ---
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
            text-align: center;
            z-index: 1000;
            border-bottom: 1px solid #ccc; /* Optional: line closest to the top */
        }
        /* Offset the body so content doesn't hide behind the fixed bar */
        body {
            margin-top: 60px; /* Adjust if you change the height of .fixed-top-bar */
        }
        /* Container with 16:9 aspect ratio */
        .aspect-ratio-container {
            width: 100%;
            aspect-ratio: 16 / 9; /* Modern CSS property for aspect ratio */
            background-color: #f0f2f6; /* Optional background color for content area */
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Fixed top bar with title and subtitle ---
st.markdown("""
    <div class="fixed-top-bar">
        <h1 style="margin: 0; padding: 0;">Dashboard Title</h1>
        <p style="margin: 0; padding: 0;">Dashboard Subtitle</p>
    </div>
    """, unsafe_allow_html=True)

# --- Main content container with a 16:9 aspect ratio ---
# You can add your Streamlit components inside this container or below it.
st.markdown('<div class="aspect-ratio-container"></div>', unsafe_allow_html=True)

# Example: Place additional content below the aspect ratio container
st.write("Add your main dashboard content below this line.")
=======
>>>>>>> e416466d60a30cd64725676171e68603d3747e41
