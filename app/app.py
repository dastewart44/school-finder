import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

def main():
    st.snow()
    st.markdown(
        """
        <style>
        .stButton {
            margin-top: 100px;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 200px;
            height: 50px;
            font-size: 18px;
        }
        .stApp {
            background-image: url("https://i.imgur.com/YFcGVI9.jpg");
            background-attachment: fixed;
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display an image
    image_url = "https://i.imgur.com/aEuKt99.png"  # Replace with your image URL
    st.image(image_url, use_column_width=True)

    # Add a button to navigate to the next page
    if st.button("Find Schools"):
        # Redirect to the next page when the button is clicked
        st.write("Redirecting to the next page...")
        switch_page("page_01")

if __name__ == "__main__":
    main()
