import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_icon=None, layout="centered", initial_sidebar_state="collapsed", menu_items=None)

def main():
    st.title('Nohting to see here until Fahd finishes his page.')

    # Add custom CSS style
    st.markdown(
        """
        <style>
        .custom-bar {
            background-color: lightgrey;
            height: 4px;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Insert the custom bar
    st.markdown('<div class="custom-bar"></div>', unsafe_allow_html=True)

    next_page = st.button("Enter")
    if next_page:
        switch_page("page_01")

if __name__ == "__main__":
    main()
