import streamlit as st

# Set page config for wide layout
st.set_page_config(layout="wide")

# Add custom CSS to remove padding and style the title
st.markdown("""
<style>
    /* Target the main app container to remove top padding/margin */
    div[data-testid="stAppViewContainer"] > .main > .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    /* Ensure block-container padding is zero */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Display the title bar using H1 with inline styles
st.markdown(
    f'''
    <h1 style="
        text-align: center; 
        margin-top: 0;
        background-color: #dcef6e;
        padding: 10px 15px;
        border-radius: 5px;
        color: #333;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px; /* Added margin-bottom back */
    ">
        Dashboard Title
    </h1>
    ''',
    unsafe_allow_html=True
)

# Add a sidebar
with st.sidebar:
    st.header("Sidebar Controls")
    st.write("Add sidebar elements here.")

# Main area remains empty as requested
# You can add content like st.title("Main Area") later

# To run this app, save the file and run `streamlit run dashboard2.py` in your terminal.
