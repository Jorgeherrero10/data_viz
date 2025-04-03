import streamlit as st

# Set page config for wide layout
st.set_page_config(layout="wide")

# Add custom CSS for the title bar
st.markdown("""
<style>
.title-bar {
    background-color: #dcef6e;
    padding: 0 15px; /* Simplified padding */
    border-radius: 5px;
    margin-bottom: 20px; /* Add some space below the title bar */
    color: #333; /* Darker text color for better contrast */
    font-size: 24px;
    font-weight: bold;
    display: flex; /* Added for vertical centering */
    align-items: center; /* Added for vertical centering */
    height: 50px; /* Fixed height for consistent appearance */
}
</style>
""", unsafe_allow_html=True)

# Display the title bar
st.markdown('<div class="title-bar">Dashboard Title</div>', unsafe_allow_html=True)

# Add a sidebar
with st.sidebar:
    st.header("Sidebar Controls")
    st.write("Add sidebar elements here.")
