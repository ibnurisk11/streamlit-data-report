import streamlit as st

# Define the pages
def main_page():
    st.title("Selamat Datang 🎈")
    st.write("Welcome to the Main Page!")

def page_2():
    st.title("Marketing & Risk ❄️")
    st.write("Welcome to Page 2!")

def page_3():
    st.title("Collection 🎉")
    st.write("Welcome to Page 3!")

# Set up navigation
pages = {
    "Home": main_page,
    "Marketing - Risk": page_2,
    "Collection": page_3
}

st.sidebar.title("Sanders Data Report")
st.sidebar.image("assets/logo-sanders-white.png", width=200)
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Render the selected page
pages[selection]()