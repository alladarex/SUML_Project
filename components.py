import streamlit as st
from db import add_report

@st.dialog("Article details", width="large")
def article_view(data):
    """Display article details inline, with report functionality."""
    user = st.session_state["user"]
    #st.markdown(f"{user[3]}")
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




def list_articles(articles):
    """List articles as clickable buttons."""
    for idx, row in articles.iterrows():
        if st.button(row['title'], key=f"article_{idx}"):
            # Pass the entire row to article_view
            article_view(row)

def report():
    st.title("Report article:")
    st.text_area("Why is this article validation wrong?")
    st.button(":material/mail: Send report") #TODO: add code to submit report to database
