import streamlit as st

@st.dialog("Article details", width="large")
def article_view(data):
    """Display article details in a dialog."""
    startingbuttn = 0
    st.title(data['title'])
    st.write(data['content'])
    if data['label'] == "FAKE":
        st.error("This news is likely FAKE.")
        startingbuttn = 0
    else:
        st.success("This news is likely REAL.")
        startingbuttn = 1
    reportbtn = st.button(":material/gavel: Report")
    if reportbtn:
        report()
    editbtn = st.button(":material/edit: Edit")
    if editbtn:
        edit(startingbuttn)



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

def edit(startingButton):
    st.title("Edit article result:")
    st.write("User report:")
    st.write("I am absolutely appauled at the fact that this article's validation is incorrect, here are the specific reasons as to why this is wrong:Lorem ipsum dolor sit amet, ...")
    st.radio("Validation result:",["Fake","True"],index=startingButton)