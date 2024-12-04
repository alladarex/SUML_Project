import streamlit as st

@st.dialog("Article details", width="large")
def article_view(data):
    """Display article details in a dialog."""
    st.title(data['title'])
    st.write(data['content'])
    if data['label'] == "FAKE":
        st.error("This news is likely FAKE.")
    else:
        st.success("This news is likely REAL.")
    if st.button(":material/gavel: Report"):
        report()



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
