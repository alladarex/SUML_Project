import streamlit as st
from db import authenticate_user, register_user

@st.dialog("Article details", width="large")
def article_view(data):
    """Display article details in a dialog."""
    st.title(data['title'])
    st.write(data['content'])
    if data['label'] == "FAKE":
        st.error("This news is likely FAKE.")
    else:
        st.success("This news is likely REAL.")


def list_articles(articles):
    """List articles as clickable buttons."""
    for idx, row in articles.iterrows():
        if st.button(row['title'], key=f"article_{idx}"):
            # Pass the entire row to article_view
            article_view(row)


@st.dialog("User authentication", width="large")
def login_view():
    """Display user authentication in a dialog."""
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in",key=1):
        user = authenticate_user(username, password)
        if user:
            st.session_state["user"] = user
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

@st.dialog("Register", width="large")
def register_view():
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    user_type = st.selectbox("User Type", ["normal", "admin"])
    if st.button("Register", key=2):
        if register_user(username, password, user_type):
            st.success("Registration successful! You can now log in.")
        else:
            st.error("Username already exists. Please choose another.")
