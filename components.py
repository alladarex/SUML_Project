import streamlit as st
import matplotlib.pyplot as plt
from db import authenticate_user, register_user, add_report, delete_report, delete_article, toggle_article_label

@st.dialog("Article details", width="large")
def article_view(data):
    """Display article details inline, with report functionality."""
    user = st.session_state["user"]
    st.markdown(f"### {data['title']}")
    if data['label'] == "FAKE":
        st.error("This news is likely FAKE.")
    else:
        st.success("This news is likely REAL.")
    st.write(data['content'])

    # Conditional report button
    if user and user[1] != "guest" and user[3] != "admin":
        if st.button("Report", key=f"report_{data['title']}"):
            st.session_state["reporting"] = True

        # Report form
        if st.session_state.get("reporting"):
            report_text = st.text_area("Enter your report (at least 20 characters):", key="report_box")
            if st.button("Send Report"):
                if len(report_text) >= 20:
                    add_report(user[0], data['id'], report_text)  # user_id, article_id
                    st.session_state["reporting"] = False
                    st.success("Report sent.")
                else:
                    st.warning("Report must be at least 20 characters long.")

    # Data breakdown
    if st.button("Data breakdown", key=f"data_breakdown_{data['title']}"):
        st.session_state["data_breakdown"] = True
    if st.session_state["data_breakdown"]:
        data_breakdown(data)





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

def report():
    st.title("Report article:")
    st.text_area("Why is this article validation wrong?")
    st.button(":material/mail: Send report") #TODO: add code to submit report to database


@st.dialog("Report Details", width="large")
def report_dialog(report, article_label, article_content):
    """
    Dialog for admin to interact with a report.
    Args:
        report (dict): Contains report details (user_id, article_id, report_content, title).
        article_label (str): The current label of the article ('FAKE' or 'REAL').
        article_content (str): The full content of the article.
    """
    st.markdown(f"### Report by User {report['user_id']}")

    # Display the article label as FAKE or REAL
    if article_label == "FAKE":
        st.error("This article is labeled as FAKE.")
    else:
        st.success("This article is labeled as REAL.")

    # Report content
    st.write("**Report Content:**")
    st.info(report["report_content"])

    # Article content
    st.markdown("---")
    st.write("**Article Content:**")
    st.write(article_content)

    # Buttons for actions
    if "action_taken" not in st.session_state:
        st.session_state["action_taken"] = False

    if not st.session_state["action_taken"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Toggle Label"):
                new_label = toggle_article_label(report["article_id"])
                delete_report(report["user_id"], report["article_id"])
                st.success(f"Article label changed to {new_label}.")
                st.session_state["action_taken"] = True
        with col2:
            if st.button("Delete Article"):
                delete_article(report["article_id"])
                delete_report(report["user_id"], report["article_id"])
                st.success("Article deleted successfully.")
                st.session_state["action_taken"] = True
        with col3:
            if st.button("Delete Report"):
                delete_report(report["user_id"], report["article_id"])
                st.success("Report deleted successfully.")
                st.session_state["action_taken"] = True
    else:
        st.success("Action completed successfully.")

def data_breakdown(data):
    accuracy = float(st.session_state['accuracy'])
    confidence = 1-float(data['confidence'])
    likelyhood = accuracy*max(confidence,1-confidence)
    if confidence == 0 or confidence == 1:
        st.warning("this article's classification was chosen manually")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Model accuracy")
        labels = 'Correct','Incorrect'
        sizes = [accuracy,1-accuracy]
        explode = [0.1,0]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes,explode=explode, labels=labels, shadow=True, startangle=90,labeldistance=.1,autopct='%1.1f%%',pctdistance=1.25)
        ax1.axis('equal')

        st.pyplot(fig1)
    with col2:
        st.write("Classification confidence")
        labels = 'True', 'Fake'
        sizes = [confidence,1-confidence]
        explode = [0.1, 0]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, shadow=True, startangle=90,labeldistance=.6,autopct='%1.1f%%',pctdistance=1.25)
        ax1.axis('equal')

        st.pyplot(fig1)
    st.write("Probability of correct classification")
    labels = 'Correct', 'Incorrect'
    sizes = [likelyhood,1-likelyhood]
    explode = [0.1, 0]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, shadow=True, startangle=90,labeldistance=.6,autopct='%1.1f%%',pctdistance=1.25)
    ax1.axis('equal')
    st.pyplot(fig1)

    if st.button("Show less", key=f"show_less_{data['title']}"):
        st.session_state["data_breakdown"] = False
