import streamlit as st

# Set page config for wide layout
st.set_page_config(layout="wide")

# Add custom CSS for the title bar
st.markdown("""
<style>
.title-bar {
    background-color: #dcef6e;
    padding: 10px 15px; /* Added padding */
    border-radius: 5px;
    margin-bottom: 20px; /* Add some space below the title bar */
    color: #333; /* Darker text color for better contrast */
    font-size: 24px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Display the title bar
st.markdown('<div class="title-bar">Dashboard Title</div>', unsafe_allow_html=True)

# Add a sidebar
with st.sidebar:
    st.header("Sidebar Controls")
    st.write("Add sidebar elements here.")
